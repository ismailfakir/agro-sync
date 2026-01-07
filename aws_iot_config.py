# aws_iot_config.py

# Wifi Name / SSID
SSID = b'wifinetwork'
# Wifi Password
PASS = b'wifipassword'

# AWS ThingName is used for the Client ID (Best Practice). Example: RaspberryPiPicoW
CLIENT_ID = b'RaspberryPiPicoW'
# AWS Endpoint (Refer to "Creating a Thing in AWS IoT Core" step 13)
AWS_ENDPOINT = b'AWS_ENDPOINT.iot.eu-west-1.amazonaws.com'

# AWS IoT Core publish topic
PUB_TOPIC = b'/' + CLIENT_ID + '/temperature'
# AWS IoT Core subscribe  topic
SUB_TOPIC = b'/' + CLIENT_ID + '/light'

# Reading Thing Private Key and Certificate into variables for later use
with open('/certs/key.der', 'rb') as f:
    DEV_KEY = f.read()
# Thing Certificate
with open('/certs/cert.der', 'rb') as f:
    DEV_CRT = f.read()

