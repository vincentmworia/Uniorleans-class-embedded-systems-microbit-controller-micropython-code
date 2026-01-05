import time
import json
from gpiozero import CPUTemperature
import paho.mqtt.client as mqtt

# ========= Config =========
BROKER = "PI5-UBUNTU-8GB.local"
PORT = 1883
TOPIC = "polytech45/telegraf/ep08"

# Your identifier (following the pattern shown in class)
EUI = "00-00-00-00-00-00-00-08"   # EP08 -> ...-08
# ==========================


class MQTTClient:
    def __init__(self, broker, port, topic, client_id=None):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.connected = False

        self.client = mqtt.Client(
            client_id=client_id,
            protocol=mqtt.MQTTv5,
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2
        )
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect

        self.client.reconnect_delay_set(min_delay=1, max_delay=30)

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code.value == 0:
            self.connected = True
            print("MQTT connected")
        else:
            print("MQTT connection failed:", reason_code)

    def _on_disconnect(self, client, userdata, reason_code, properties):
        self.connected = False
        print("MQTT disconnected:", reason_code)

    def connect(self):
        self.client.connect(self.broker, self.port, keepalive=30)
        self.client.loop_start()

    def publish(self, payload, qos=1, retain=False):
        if not self.connected:
            return False
        result = self.client.publish(self.topic, json.dumps(payload), qos=qos, retain=retain)
        return result.rc == mqtt.MQTT_ERR_SUCCESS

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()


def main():
    cpu = CPUTemperature()

    mqttc = MQTTClient(BROKER, PORT, TOPIC, client_id="EP08")
    mqttc.connect()

    try:
        while True:
            # If not connected yet, wait (like your prof code)
            if not mqttc.connected:
                time.sleep(1)
                continue

            temp = round(cpu.temperature, 1)

            payload = {
                "eui": EUI,
                "cpu_temperature": temp,
                "status": "on"
            }

            ok = mqttc.publish(payload, qos=1, retain=False)
            print(f"{TOPIC} {payload}" if ok else "Publish failed")

            time.sleep(5)

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        mqttc.disconnect()


if __name__ == "__main__":
    main()
