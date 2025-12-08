import time
import threading
from .can_bus import CANBusSimulator
from .sensors import SensorHub
from .obd_pids import OBDSimulator

class ESP32DigitalTwin:
    def __init__(self, mqtt_bridge=None):
        self.can_bus = CANBusSimulator()
        self.sensors = SensorHub()
        self.obd = OBDSimulator()
        self.mqtt_bridge = mqtt_bridge
        self.running = False
    
    def start(self):
        print("Starting ESP32 Digital Twin...")
        self.can_bus.start()
        self.running = True
        threading.Thread(target=self._main_loop, daemon=True).start()
        threading.Thread(target=self._obd_loop, daemon=True).start()
        print("ESP32 Digital Twin started")
    
    def _main_loop(self):
        while self.running:
            sensor_data = self.sensors.read_all()
            
            # Enviar datos de sensores por CAN
            temp_data = [int(sensor_data["temperature"] * 10) & 0xFF, 
                        int(sensor_data["pressure"]) & 0xFF]
            self.can_bus.send_message(0x100, temp_data)
            
            # Publicar datos de sensores por MQTT
            if self.mqtt_bridge:
                self.mqtt_bridge.publish_sensor_data(sensor_data)
            
            # Procesar mensajes CAN recibidos
            msg = self.can_bus.receive_message()
            if msg:
                self._process_can_message(msg)
            
            time.sleep(0.1)
    
    def _obd_loop(self):
        while self.running:
            self.obd.update()
            
            # Simular respuestas OBD en CAN ID 0x7E8
            for pid in [0x0C, 0x0D, 0x05]:
                response = self.obd.get_pid_response(pid)
                if response:
                    self.can_bus.send_message(0x7E8, response)
            
            # Publicar datos OBD por MQTT
            if self.mqtt_bridge:
                obd_data = {
                    "rpm": self.obd.rpm,
                    "speed": self.obd.speed,
                    "coolant_temp": self.obd.coolant_temp,
                    "throttle": self.obd.throttle,
                    "fuel_level": self.obd.fuel_level
                }
                self.mqtt_bridge.publish_obd_data(obd_data)
            
            time.sleep(0.5)
    
    def _process_can_message(self, msg):
        # Procesar solicitudes OBD (ID 0x7DF)
        if msg.arbitration_id == 0x7DF and len(msg.data) >= 2:
            if msg.data[1] == 0x01:  # Modo 01: datos en vivo
                pid = msg.data[2]
                response = self.obd.get_pid_response(pid)
                if response:
                    self.can_bus.send_message(0x7E8, response)
    
    def get_status(self):
        return {
            "sensors": self.sensors.read_all(),
            "obd": {
                "rpm": self.obd.rpm,
                "speed": self.obd.speed,
                "coolant_temp": self.obd.coolant_temp,
                "fuel_level": self.obd.fuel_level
            }
        }
    
    def stop(self):
        print("Stopping ESP32 Digital Twin...")
        self.running = False
        self.can_bus.stop()
        print("ESP32 Digital Twin stopped")
