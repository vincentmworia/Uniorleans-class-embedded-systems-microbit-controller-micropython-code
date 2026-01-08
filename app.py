import time
import json
import paho.mqtt.client as mqtt

BROKER = "PI5-UBUNTU-8GB.local"
PORT = 1883
TOPIC = "telegraf/mars/ep08"
EUI = "00-00-00-00-00-00-00-EP08"

def get_cpu_temp():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        return round(int(f.read().strip()) / 1000.0, 2)

client = mqtt.Client(client_id="ep08")
client.connect(BROKER, PORT, 30)
client.loop_start()

try:
    while True:
        cpu_temp = get_cpu_temp()

        payload = {
            "eui": EUI,
            "cpu_temperature": cpu_temp,
            "status": "on",
            "error": 1 if cpu_temp > 70 else 0
        }

        client.publish(TOPIC, json.dumps(payload))
        print("Sent:", payload)
        time.sleep(5)

except KeyboardInterrupt:
    print("Stopping...")

finally:
    client.loop_stop()
    client.disconnect()
