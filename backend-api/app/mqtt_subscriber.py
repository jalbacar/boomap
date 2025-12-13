import paho.mqtt.client as mqtt
import json
import threading
import os

class MQTTSubscriber:
    def __init__(self, broker=None, port=1883, on_obd_data=None, on_sensor_data=None,
                 on_prediction_data=None, on_alert_data=None):
        self.broker = broker or os.getenv("MQTT_BROKER", "localhost")
        self.port = int(os.getenv("MQTT_PORT", port))
        self.username = os.getenv("MQTT_USERNAME")
        self.password = os.getenv("MQTT_PASSWORD")
        self.use_tls = os.getenv("MQTT_USE_TLS", "false").lower() == "true"
        
        self.client = mqtt.Client(client_id="boomapp_backend")
        self.connected = False
        
        # Configurar autenticación
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
        
        # Configurar TLS
        if self.use_tls:
            self.client.tls_set()
        
        self.on_obd_data = on_obd_data
        self.on_sensor_data = on_sensor_data
        self.on_prediction_data = on_prediction_data
        self.on_alert_data = on_alert_data
        
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
    
    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            print(f"✓ Backend conectado al MQTT Broker: {self.broker}:{self.port}")
            self.client.subscribe("boomapp/vehicle/obd")
            self.client.subscribe("boomapp/vehicle/sensors")
            self.client.subscribe("boomapp/predictions/wear")
            self.client.subscribe("boomapp/predictions/alerts")
            print("✓ Suscrito a topics del vehículo y predicciones")
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
            elif msg.topic == "boomapp/predictions/wear" and self.on_prediction_data:
                self.on_prediction_data(data)
            elif msg.topic == "boomapp/predictions/alerts" and self.on_alert_data:
                self.on_alert_data(data)
                
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
