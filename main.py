# AWS IoT Core - RPi Pico 2 W agro_sync

# Required imports
import time
import ntptime
import machine
import dht
import network
import ujson
from umqtt.simple import MQTTClient
from aws_iot_config import *

# Define light (Onboard Green LED) and set its default state to off
light = machine.Pin("LED", machine.Pin.OUT)
light.off()

# Initialize the DHT11 sensor
sensorDH11 = dht.DHT11(machine.Pin(16))

# Wifi Connection Setup
def wifi_connect():
    print('Connecting to wifi...')
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASS)
    while wlan.isconnected() == False:
        light.on()
        print('Waiting for connection...')
        time.sleep(0.5)
        light.off()
        time.sleep(0.5)
    print('Connection details: %s' % str(wlan.ifconfig()))

# Callback function for all subscriptions
def mqtt_subscribe_callback(topic, msg):
    print("Received topic: %s message: %s" % (topic, msg))
    if topic == SUB_TOPIC:
        mesg = ujson.loads(msg)
        if 'state' in mesg.keys():
            if mesg['state'] == 'on' or mesg['state'] == 'ON' or mesg['state'] == 'On':
                light.on()
                print('Light is ON')
            else:
                light.off()
                print('Light is OFF')

# Read current temperature from RP2040 embeded sensor
def get_rpi_temperature():
    sensor = machine.ADC(4)
    voltage = sensor.read_u16() * (3.3 / 65535)
    temperature = 27 - (voltage - 0.706) / 0.001721
    return temperature

# read current temperature & humidity from DHT11 sensore
def get_dht11_temperature():
    try:
      # Trigger measurement
      sensorDH11.measure()
      # Read values
      temperature = (sensorDH11.temperature())  # In Celsius
      humidity = (sensorDH11.humidity())        # In Percent
      # Print values
      print("Temperature: {}°C   Humidity: {}%".format(temperature, humidity))
      return temperature, humidity
    except OSError as e:
      print("Failed to read sensor.")

# read current time from ntp server
def read_current_time():
    # Once connected:
    try:
        ntptime.settime()  # Synchronize the internal RTC with an NTP server
        rtc = machine.RTC()
        # You can now get the time as a tuple or format it into a string
        current_time = rtc.datetime() 
        print(f"Current time: {current_time}") 
        # Example output format: (year, month, day, weekday, hour, minute, second, subsecond)

    except OSError:
        print("Could not sync with NTP server, using default time (Jan 1, 2021)")
    

# Connect to wifi
wifi_connect()
#read current time
read_current_time()

# Set AWS IoT Core connection details
mqtt = MQTTClient(
    client_id=CLIENT_ID,
    server=AWS_ENDPOINT,
    port=8883,
    keepalive=5000,
    ssl=True,
    ssl_params={'key':DEV_KEY, 'cert':DEV_CRT, 'server_side':False})

# Establish connection to AWS IoT Core
mqtt.connect()

# Set callback for subscriptions
mqtt.set_callback(mqtt_subscribe_callback)

# Subscribe to topic
mqtt.subscribe(SUB_TOPIC)

# Main loop - with 15 sec delay
while True:
    # read dht11 temperature
    tem,hum = get_dht11_temperature()
    # Publisg the temperature & humidity
    message = b'{"temperature":%s, "humidity":%s}' % (tem, hum)
    print('Publishing topic %s message %s' % (PUB_TOPIC, message))
    # QoS Note: 0=Sent zero or more times, 1=Sent at least one, wait for PUBACK
    # See https://docs.aws.amazon.com/iot/latest/developerguide/mqtt.html
    mqtt.publish(topic=PUB_TOPIC, msg=message, qos=0)

    # Check subscriptions for message
    mqtt.check_msg()
    time.sleep(15)
