import time
import csv
from boomapp.can_twin import ESP32DigitalTwin
from boomapp.mqtt_bridge import MQTTBridge

class VehicleSimulator:
    def __init__(self, scenario_file, use_mqtt=True, broker="localhost", 
                 port=1883, username=None, password=None, use_tls=False):
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
    
    print("=== SIMULADOR DE VEHÍCULO - BoomApp ===\n")
    print("Seleccione un escenario:")
    for key, (_, desc) in scenarios.items():
        print(f"{key}. {desc}")
    
    choice = input("\nOpción: ")
    
    if choice in scenarios:
        file, desc = scenarios[choice]
        print(f"\nCargando escenario: {desc}")
        
        # Configurar broker MQTT
        print("\n¿Usar broker MQTT? (s/n): ", end="")
        use_mqtt = input().lower() == 's'
        
        broker = "localhost"
        port = 1883
        username = None
        password = None
        use_tls = False
        
        if use_mqtt:
            print("Broker (localhost/HiveMQ): ", end="")
            broker_input = input().strip()
            if broker_input:
                broker = broker_input
            
            # Si no es localhost, preguntar por credenciales
            if broker != "localhost":
                print("¿Usar TLS? (s/n): ", end="")
                use_tls = input().lower() == 's'
                
                if use_tls:
                    port = 8883
                
                print("Usuario (Enter para omitir): ", end="")
                username = input().strip() or None
                
                if username:
                    print("Contraseña: ", end="")
                    import getpass
                    password = getpass.getpass("")
        
        sim = VehicleSimulator(
            file, 
            use_mqtt=use_mqtt, 
            broker=broker,
            port=port,
            username=username,
            password=password,
            use_tls=use_tls
        )
        sim.run(duration=30)
    else:
        print("Opción inválida")
