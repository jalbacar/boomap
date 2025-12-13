import time
import csv
import os
from dotenv import load_dotenv
from boomapp.can_twin import ESP32DigitalTwin
from boomapp.mqtt_bridge import MQTTBridge

# Cargar variables de entorno desde .env
load_dotenv()

class VehicleSimulator:
    def __init__(self, scenario_file, use_mqtt=True):
        # Leer configuración MQTT desde variables de entorno
        broker = os.getenv("MQTT_BROKER", "localhost")
        port = int(os.getenv("MQTT_PORT", "1883"))
        username = os.getenv("MQTT_USERNAME")
        password = os.getenv("MQTT_PASSWORD")
        use_tls = os.getenv("MQTT_USE_TLS", "false").lower() == "true"
        
        self.mqtt = None
        if use_mqtt:
            self.mqtt = MQTTBridge(
                broker=broker, 
                port=port,
                username=username,
                password=password,
                use_tls=use_tls
            )
            self.mqtt.connect()
            self.mqtt.set_command_callback(self._handle_command)
        
        self.twin = ESP32DigitalTwin(mqtt_bridge=self.mqtt)
        self.scenario_data = self._load_scenario(scenario_file)
        self.current_step = 0
    
    def _load_scenario(self, filename):
        data = []
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append({k: float(v) for k, v in row.items()})
        return data
    
    def run(self, duration=30):
        self.twin.start()
        print(f"\n=== Simulación iniciada ===")
        
        start_time = time.time()
        while time.time() - start_time < duration and self.current_step < len(self.scenario_data):
            # Aplicar datos del escenario
            step_data = self.scenario_data[self.current_step]
            self.twin.obd.rpm = step_data['rpm']
            self.twin.obd.speed = step_data['speed']
            self.twin.obd.coolant_temp = step_data['coolant_temp']
            self.twin.obd.throttle = step_data['throttle']
            self.twin.sensors.sensors['temperature'].value = step_data['temperature']
            self.twin.sensors.sensors['pressure'].value = step_data['pressure']
            self.twin.sensors.sensors['vibration'].value = step_data['vibration']
            
            # Mostrar estado
            status = self.twin.get_status()
            print(f"\n[Paso {self.current_step}]")
            print(f"RPM: {status['obd']['rpm']:.0f} | Velocidad: {status['obd']['speed']:.0f} km/h")
            print(f"Temp Motor: {status['obd']['coolant_temp']:.1f}°C | Acelerador: {self.twin.obd.throttle:.0f}%")
            print(f"Temp Ambiente: {status['sensors']['temperature']:.1f}°C | Vibración: {status['sensors']['vibration']:.2f}")
            
            self.current_step += 1
            time.sleep(2)
        
        self.twin.stop()
        if self.mqtt:
            self.mqtt.disconnect()
        print("\n=== Simulación finalizada ===\n")
    
    def _handle_command(self, command):
        cmd_type = command.get("type")
        if cmd_type == "pause":
            print("⏸ Pausa solicitada")
        elif cmd_type == "resume":
            print("▶ Reanudación solicitada")
        elif cmd_type == "stop":
            print("⏹ Detención solicitada")
            self.twin.stop()

if __name__ == "__main__":
    scenarios = {
        "1": ("data/normal.csv", "Uso normal y correcto"),
        "2": ("data/extreme.csv", "Uso extremo"),
        "3": ("data/stressed.csv", "Uso tensionado"),
        "4": ("data/limit.csv", "Al límite"),
        "5": ("data/faulty.csv", "Problemas en componentes"),
        "6": ("data/overheating.csv", "Sobrecalentamiento")
    }
    
    # Mostrar configuración MQTT desde .env
    broker = os.getenv("MQTT_BROKER", "localhost")
    port = os.getenv("MQTT_PORT", "1883")
    use_tls = os.getenv("MQTT_USE_TLS", "false").lower() == "true"
    
    print("=== SIMULADOR DE VEHÍCULO - BoomApp ===\n")
    print(f"MQTT Broker: {broker}:{port} (TLS: {'Sí' if use_tls else 'No'})")
    print("-" * 40)
    print("\nSeleccione un escenario:")
    for key, (_, desc) in scenarios.items():
        print(f"{key}. {desc}")
    
    choice = input("\nOpción: ")
    
    if choice in scenarios:
        file, desc = scenarios[choice]
        print(f"\nCargando escenario: {desc}")
        
        sim = VehicleSimulator(file, use_mqtt=True)
        sim.run(duration=30)
    else:
        print("Opción inválida")
