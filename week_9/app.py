import json
import time
import paho.mqtt.client as mqtt

# Configuration
id = "louistaylor"  # MUST match device ID
client_telemetry_topic = f"{id}/telemetry"
server_command_topic = f"{id}/commands"
client_name = f"{id}_server"

def handle_telemetry(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode())
        print(f"\n[SERVER] Received: {payload}")
        
        # Send command (LED ON if temp > 25°C)
        command = {'led_on': payload['temperature'] > 25}
        client.publish(server_command_topic, json.dumps(command))
        print(f"[SERVER] Sent command: {command}")
        
    except Exception as e:
        print(f"[SERVER] Error: {e}")

# MQTT Setup
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_name)
mqtt_client.connect("test.mosquitto.org")
mqtt_client.subscribe(client_telemetry_topic)
mqtt_client.on_message = handle_telemetry
mqtt_client.loop_start()

print(f"Server started. Listening to: {client_telemetry_topic}")
print(f"Command topic: {server_command_topic}")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Server stopped.")