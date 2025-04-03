import os
import glob
import time
import json
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO

# ----------------- GPIO & Sensor Setup -----------------
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
LED_PIN = 17  # LED pin (optional for Part 2, but kept for reference)
GPIO.setup(LED_PIN, GPIO.OUT, initial=GPIO.LOW)

# DS18B20 Sensor Setup
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
                temp_c = float(lines[1][temp_pos+2:]) / 1000.0
                return round(temp_c, 2)
    except Exception as e:
        print(f"Sensor error: {e}")
        return None

# ----------------- MQTT Setup -----------------
id = 'louistaylor'  # Replace with your unique ID
client_name = id + 'temperature_client'
telemetry_topic = f"{id}/telemetry"  # MQTT topic for telemetry

mqtt_client = mqtt.Client(client_name)
mqtt_client.connect('test.mosquitto.org')
mqtt_client.loop_start()
print("MQTT connected!")

# ----------------- Main Loop -----------------
def main():
    setup_sensor()
    while True:
        temp_c = read_temperature()
        if temp_c is not None:
            print(f"Temperature: {temp_c}°C")
            
            # Publish telemetry as JSON
            payload = json.dumps({
                "temperature": temp_c,
                "timestamp": time.time(),
                "device_id": id
            })
            mqtt_client.publish(telemetry_topic, payload)
            print(f"Published: {payload}")
        
        time.sleep(3)

if __name__ == '__main__':
    print("Press Ctrl+C to exit...")
    try:
        main()
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("\nExiting...")