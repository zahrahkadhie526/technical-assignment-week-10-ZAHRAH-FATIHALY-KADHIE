import math
import random
import time
import RPi.GPIO as GPIO

import requests
from ubidots import ApiClient

import Adafruit_DHT
import time
 
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 17
trigger_pin = 23
echo_pin = 24

TOKEN = "BBFF-KsIA3idbf4f8wxSpC16zLO4WZKSWci"  # Put your TOKEN here
DEVICE_LABEL = "nugraha"  # Put your device label here
VARIABLE_LABEL_1 = "distance"  # Put your first variable label here
VARIABLE_LABEL_2 = "dht"  # Put your second variable label here
VARIABLE_LABEL_3 = "kelembaban"

api = ApiClient(token=TOKEN)

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(trigger_pin, GPIO.OUT)
    GPIO.setup(echo_pin, GPIO.IN)

def get_distance():
    GPIO.output(trigger_pin, GPIO.LOW)
    time.sleep(0.000002)
    GPIO.output(trigger_pin, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(trigger_pin, GPIO.LOW)

    start_time = time.time()
    end_time = time.time()
    while GPIO.input(echo_pin) == GPIO.LOW:
        start_time = time.time()
    while GPIO.input(echo_pin) == GPIO.HIGH:
        end_time = time.time()

    duration = end_time - start_time
    distance = duration * 34300 / 2  # Kecepatan suara adalah 343 m/s

    return distance

def ultrasonik():
    GPIO.cleanup()
    
def build_payload(variable_1, variable_2, variable_3, value_1, value_2, value_3):
    payload = {variable_1: value_1,
               variable_2: value_2,
               variable_3: value_3}

    return payload



def post_request(payload):
    # Creates the headers for the HTTP requests
    url = "http://industrial.api.ubidots.com"
    url = "{}/api/v1.6/devices/{}".format(url, DEVICE_LABEL)
    headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}

    # Makes the HTTP requests
    status = 400
    attempts = 0
    while status >= 400 and attempts <= 5:
        req = requests.post(url=url, headers=headers, json=payload)
        status = req.status_code
        attempts += 1
        time.sleep(1)

    # Processes results
    print("[INFO] Request code :", req.status_code,",Payload :", req.json())
    if status >= 400:
        print("[ERROR] Could not send data after 5 attempts, please check \
            your token credentials and internet connection")
        return False

    print("[INFO] Request made properly, your device is updated")
    return True


def main():
    payload = build_payload(
        VARIABLE_LABEL_1, VARIABLE_LABEL_2, VARIABLE_LABEL_3)
    print("[INFO] Attemping to send data")
    post_request(payload)
    print("[INFO] Finished send data")


if _name_ == '_main_':
    setup()
    while True:
        # Read sensor
        distance = get_distance()
        humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
        
        # Check sensor and print
        if humidity is not None and temperature is not None:
            print("Temp={0:0.1f}C Humidity={1:0.1f}%".format(temperature, humidity))
        else:
            print("Sensor failure. Check wiring.");
        print("Jarak: %.2f cm" % distance)
        
        # Send to ubidots
        payload = build_payload(VARIABLE_LABEL_1, VARIABLE_LABEL_2, VARIABLE_LABEL_3,
                                distance, humidity, temperature)
        post_request(payload)
        time.sleep(0.5)  # Memberi jeda sebelum membaca data berikutnya
