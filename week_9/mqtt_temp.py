import os
import glob
import time
import json
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO

# GPIO Setup
GPIO.setwarnings(False)
GPIO.cleanup()  # Critical fix: Reset GPIO
GPIO.setmode(GPIO.BCM)
LED_PIN = 17
GPIO.setup(LED_PIN, GPIO.OUT, initial=GPIO.LOW)

# Test LED on startup
print("Testing LED...")
GPIO.output(LED_PIN, GPIO.HIGH)
time.sleep(1)
GPIO.output(LED_PIN, GPIO.LOW)
print("LED test complete.")

# Sensor Setup
def setup_sensor():
    os.system('modprobe w1-gpio')
    os.system('modprobe w1-therm')
    base_dir = '/sys/bus/w1/devices/'
    device_folder = glob.glob(base_dir + '28*')[0]
    global device_file
    device_file = device_folder + '/w1_slave'

def read_temperature():
    try:
        with open(device_file, 'r') as f:
            lines = f.readlines()
            if lines[0].strip()[-3:] == 'YES':
                temp_pos = lines[1].find('t=')
                return round(float(lines[1][temp_pos+2:]) / 1000.0, 2)
    except Exception as e:
        print(f"Sensor error: {e}")
        return None

# MQTT Setup
id = "louistaylor"  # MUST match server ID
client_name = f"{id}_client"
telemetry_topic = f"{id}/telemetry"
command_topic = f"{id}/commands"

def on_command(client, userdata, message):
    try:
        command = json.loads(message.payload.decode())
        print(f"\n[DEVICE] Received command: {command}")
        GPIO.output(LED_PIN, GPIO.HIGH if command['led_on'] else GPIO.LOW)
        print(f"[DEVICE] LED set to: {'ON' if command['led_on'] else 'OFF'}")
    except Exception as e:
        print(f"[DEVICE] Command error: {e}")

mqtt_client = mqtt.Client(client_name)
mqtt_client.connect("test.mosquitto.org")
mqtt_client.subscribe(command_topic)
mqtt_client.on_message = on_command
mqtt_client.loop_start()

# Main Loop
def main():
    setup_sensor()
    while True:
        temp_c = read_temperature()
        if temp_c is not None:
            payload = json.dumps({"temperature": temp_c})
            mqtt_client.publish(telemetry_topic, payload)
            print(f"\n[DEVICE] Published: {payload}")
        time.sleep(3)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("Device stopped.")