import json
import time
import threading
import socket
import paho.mqtt.client as mqtt

class MQTTBridge:
    def __init__(self, broker="localhost", port=1883, client_id="boomapp_twin", 
                 username=None, password=None, use_tls=False):
        self.broker = broker
        self.port = port
        self.client_id = client_id
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.client = mqtt.Client(client_id=client_id)
        self.connected = False
        self.running = False
        
        # Configurar autenticación si se proporciona
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
        
        # Configurar TLS si se requiere
        if self.use_tls:
            self.client.tls_set()
        
        # Topics
        self.topic_telemetry = "boomapp/vehicle/telemetry"
        self.topic_obd = "boomapp/vehicle/obd"
        self.topic_sensors = "boomapp/vehicle/sensors"
        self.topic_commands = "boomapp/vehicle/commands"
        self.topic_status = "boomapp/vehicle/status"
        
        # Callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        self.command_callback = None
    
    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            print(f"✓ Conectado al broker MQTT: {self.broker}:{self.port}")
            self.client.subscribe(self.topic_commands)
            print(f"✓ Suscrito a: {self.topic_commands}")
        else:
            error_messages = {
                1: "Versión de protocolo incorrecta",
                2: "Identificador de cliente inválido",
                3: "Servidor no disponible",
                4: "Usuario/contraseña incorrectos",
                5: "No autorizado"
            }
            print(f"✗ Error de conexión MQTT (código {rc}): {error_messages.get(rc, 'Error desconocido')}")
    
    def _on_disconnect(self, client, userdata, rc):
        self.connected = False
        print(f"✗ Desconectado del broker MQTT")
    
    def _on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            print(f"← Comando recibido: {payload}")
            if self.command_callback:
                self.command_callback(payload)
        except Exception as e:
            print(f"Error procesando mensaje: {e}")
    
    def connect(self):
        try:
            tls_str = " (TLS)" if self.use_tls else ""
            auth_str = f" como {self.username}" if self.username else ""
            print(f"Conectando a {self.broker}:{self.port}{tls_str}{auth_str}...")
            self.client.connect(self.broker, self.port, 60)
            self.running = True
            threading.Thread(target=self.client.loop_forever, daemon=True).start()
            
            # Esperar hasta que se conecte (máximo 10 segundos)
            timeout = 10
            start = time.time()
            while not self.connected and (time.time() - start) < timeout:
                time.sleep(0.1)
            
            if not self.connected:
                print(f"✗ Timeout conectando al broker después de {timeout}s")
                print(f"\nPosibles causas:")
                print(f"  1. Mosquitto no está corriendo (ejecuta: mosquitto -v)")
                print(f"  2. Firewall bloqueando puerto 1883")
                print(f"  3. Broker incorrecto (verifica: {self.broker})")
                print(f"\nPrueba: telnet {self.broker} {self.port}")
        except ConnectionRefusedError:
            print(f"✗ Conexión rechazada: El broker no está escuchando en {self.broker}:{self.port}")
            print(f"  → Asegúrate de que Mosquitto esté corriendo: mosquitto -v")
        except socket.gaierror:
            print(f"✗ No se puede resolver el host: {self.broker}")
            print(f"  → Verifica que el nombre del broker sea correcto")
        except socket.timeout:
            print(f"✗ Timeout de conexión: No se puede alcanzar {self.broker}:{self.port}")
            print(f"  → Verifica tu conexión a internet o firewall")
        except Exception as e:
            print(f"✗ Error conectando al broker: {type(e).__name__}: {e}")
    
    def disconnect(self):
        self.running = False
        self.client.disconnect()
    
    def publish_telemetry(self, data):
        if self.connected:
            payload = json.dumps(data)
            self.client.publish(self.topic_telemetry, payload, qos=1)
    
    def publish_obd_data(self, obd_data):
        if self.connected:
            payload = json.dumps(obd_data)
            result = self.client.publish(self.topic_obd, payload, qos=1)
            print(f"→ OBD publicado: {result.rc} | RPM: {obd_data.get('rpm', 'N/A')}")
        else:
            print("✗ No conectado, no se puede publicar OBD")
    
    def publish_sensor_data(self, sensor_data):
        if self.connected:
            payload = json.dumps(sensor_data)
            result = self.client.publish(self.topic_sensors, payload, qos=1)
            print(f"→ Sensores publicados: {result.rc} | Temp: {sensor_data.get('temperature', 'N/A')}")
        else:
            print("✗ No conectado, no se puede publicar sensores")
    
    def publish_status(self, status):
        if self.connected:
            payload = json.dumps(status)
            self.client.publish(self.topic_status, payload, qos=1)
    
    def set_command_callback(self, callback):
        self.command_callback = callback
