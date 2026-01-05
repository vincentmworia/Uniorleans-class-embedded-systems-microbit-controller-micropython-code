import time
import json
import paho.mqtt.client as mqtt


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

        # Callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect

        # Reconnexion auto
        self.client.reconnect_delay_set(min_delay=1, max_delay=30)

    # ---------- Callbacks ----------
    def _on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code.value == 0:
            self.connected = True
            print("MQTT connected")
        else:
            print("MQTT connection failed:", reason_code)

    def _on_disconnect(self, client, userdata, reason_code, properties):
        self.connected = False
        print("MQTT disconnected:", reason_code)

    # ---------- API publique ----------
    def connect(self):
        self.client.connect(self.broker, self.port, keepalive=30)
        self.client.loop_start()

    def publish(self, payload, qos=1, retain=True):
        if not self.connected:
            return False

        result = self.client.publish(
            self.topic,
            json.dumps(payload),
            qos=qos,
            retain=retain
        )

        return result.rc == mqtt.MQTT_ERR_SUCCESS

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
