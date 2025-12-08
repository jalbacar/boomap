import paho.mqtt.client as mqtt
import json
import threading
import os

class MQTTSubscriber:
    def __init__(self, broker=None, port=1883, on_obd_data=None, on_sensor_data=None):
        self.broker = broker or os.getenv("MQTT_BROKER", "localhost")
        self.port = int(os.getenv("MQTT_PORT", port))
        self.client = mqtt.Client(client_id="boomapp_backend")
        self.connected = False
        
        self.on_obd_data = on_obd_data
        self.on_sensor_data = on_sensor_data
        
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
    
    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            print(f"✓ Backend conectado al MQTT Broker: {self.broker}:{self.port}")
            self.client.subscribe("boomapp/vehicle/obd")
            self.client.subscribe("boomapp/vehicle/sensors")
            print("✓ Suscrito a topics del vehículo")
        else:
            print(f"✗ Error conectando al MQTT: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        self.connected = False
        print("✗ Desconectado del MQTT Broker")
    
    def _on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            
            if msg.topic == "boomapp/vehicle/obd" and self.on_obd_data:
                self.on_obd_data(data)
            elif msg.topic == "boomapp/vehicle/sensors" and self.on_sensor_data:
                self.on_sensor_data(data)
                
        except Exception as e:
            print(f"Error procesando mensaje MQTT: {e}")
    
    def connect(self):
        try:
            self.client.connect(self.broker, self.port, 60)
            threading.Thread(target=self.client.loop_forever, daemon=True).start()
        except Exception as e:
            print(f"Error conectando al broker MQTT: {e}")
    
    def disconnect(self):
        self.client.disconnect()
