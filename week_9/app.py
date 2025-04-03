import json
import time
import paho.mqtt.client as mqtt

# MQTT Configuration
id = "louistaylor"  # Must match your Pi's ID
client_telemetry_topic = f"{id}/telemetry"
client_name = f"{id}_temperature_server"

def handle_telemetry(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode())
        print(f"Message received: {payload}")
    except Exception as e:
        print(f"Error processing message: {e}")

# Initialize MQTT client with callback API version
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_name)  # <-- Critical fix
mqtt_client.connect("test.mosquitto.org")
mqtt_client.subscribe(client_telemetry_topic)
mqtt_client.on_message = handle_telemetry
mqtt_client.loop_start()

print(f"Server listening on topic: {client_telemetry_topic}")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Server stopped.")