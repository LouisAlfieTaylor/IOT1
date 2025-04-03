import os
import glob
import time
import json
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO


# ----------------- GPIO & Sensor Setup -----------------
GPIO.setmode(GPIO.BCM)  # Use BCM numbering

# Define GPIO pins
LED_PIN = 17  # Change as needed
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.LOW)  # Ensure LED starts OFF

# DS18B20 1-Wire Setup
def setup():
    os.system('modprobe w1-gpio')
    os.system('modprobe w1-therm')
    base_dir = '/sys/bus/w1/devices/'
    device_folders = glob.glob(base_dir + '28*')
    if not device_folders:
        raise Exception("No DS18B20 sensor found!")
    global device_file
    device_file = device_folders[0] + '/w1_slave'

def read_file():
    with open(device_file, 'r') as f:
        return f.readlines()

def read_temperature():
    while True:
        try:
            lines = read_file()
            if not lines:
                continue
            while lines[0].strip()[-3:] != 'YES':
                time.sleep(0.2)
                lines = read_file()
            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
                temp_c = float(lines[1][equals_pos + 2:]) / 1000.0
                return round(temp_c, 2)
        except (IndexError, FileNotFoundError) as e:
            print(f"Error reading sensor: {e}. Retrying...")
            time.sleep(0.5)


# ----------------- MQTT Setup -----------------
id = 'louistaylor'
client_name = id + 'temperature_client'

mqtt_client = mqtt.Client(client_name)
mqtt_client.connect('test.mosquitto.org')
mqtt_client.loop_start()
print("MQTT connected!")


telemetry_topic = client_name + '/telemetry'
command_topic = client_name + '/commands'

# Callback function for MQTT commands (e.g., LED control)
def on_command(client, userdata, message):
    try:
        command = json.loads(message.payload.decode())
        print("Command received:", command)
        if command.get('led_on'):
            GPIO.output(LED_PIN, GPIO.HIGH)
            print("LED turned ON")
        else:
            GPIO.output(LED_PIN, GPIO.LOW)
            print("LED turned OFF")
    except Exception as e:
        print("Error processing command:", e)

mqtt_client.subscribe(command_topic)
mqtt_client.message_callback_add(command_topic, on_command)

# ----------------- Main Loop -----------------
def loop():
    while True:
        temp_c = read_temperature()
        print(f'Temperature: {temp_c:.2f}°C')

        # Publish temperature telemetry
        payload = json.dumps({'temperature': temp_c})
        mqtt_client.publish(telemetry_topic, payload)
        print("Published telemetry:", payload)

        time.sleep(3)

if __name__ == '__main__':
    print("Press Ctrl+C to stop the program...")
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        print("Exiting...")
        GPIO.cleanup()