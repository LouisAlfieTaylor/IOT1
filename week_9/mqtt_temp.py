import os
import glob
import time
import json
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO

# ----------------- GPIO & Sensor Setup -----------------
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)  # Disable GPIO warnings
LED_PIN = 17  # Verify physical connection matches this BCM pin

# Initialize GPIO pin safely
try:
    GPIO.setup(LED_PIN, GPIO.OUT, initial=GPIO.LOW)
except Exception as e:
    print(f"GPIO setup failed: {str(e)}")
    exit(1)

# DS18B20 Sensor Setup
def setup():
    os.system('modprobe w1-gpio')
    os.system('modprobe w1-therm')
    base_dir = '/sys/bus/w1/devices/'
    device_folders = glob.glob(base_dir + '28*')
    if not device_folders:
        raise Exception("No DS18B20 sensor found!")
    global device_file
    device_file = device_folders[0] + '/w1_slave'

def read_temperature():
    while True:
        try:
            with open(device_file, 'r') as f:
                lines = f.readlines()
                if lines[0].strip()[-3:] == 'YES':
                    equals_pos = lines[1].find('t=')
                    temp_c = float(lines[1][equals_pos+2:]) / 1000.0
                    return round(temp_c, 2)
                time.sleep(0.2)
        except Exception as e:
            print(f"Sensor error: {str(e)}")
            time.sleep(1)

# ----------------- MQTT Setup -----------------
id = 'louistaylor'
client_name = id + 'temperature_client'
mqtt_client = mqtt.Client(client_name)
mqtt_client.connect('test.mosquitto.org')
mqtt_client.loop_start()
print("MQTT connected!")

# ----------------- Main Loop -----------------
def loop():
    while True:
        temp_c = read_temperature()
        print(f'Temperature: {temp_c}°C')

        # Local LED control
        GPIO.output(LED_PIN, GPIO.HIGH if temp_c > 25 else GPIO.LOW)
        
        time.sleep(3)

if __name__ == '__main__':
    print("Press Ctrl+C to stop")
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("\nExiting...")