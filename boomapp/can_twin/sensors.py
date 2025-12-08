import random
import time

class Sensor:
    def __init__(self, name, min_val, max_val, initial_val):
        self.name = name
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
    
    def read(self):
        drift = random.uniform(-0.5, 0.5)
        self.value = max(self.min_val, min(self.max_val, self.value + drift))
        return self.value

class SensorHub:
    def __init__(self):
        self.sensors = {
            "temperature": Sensor("Temperature", -40, 125, 25),
            "pressure": Sensor("Pressure", 0, 200, 101.3),
            "humidity": Sensor("Humidity", 0, 100, 50),
            "vibration": Sensor("Vibration", 0, 10, 0.5),
        }
    
    def read_all(self):
        return {name: sensor.read() for name, sensor in self.sensors.items()}
    
    def get_sensor(self, name):
        return self.sensors.get(name)
