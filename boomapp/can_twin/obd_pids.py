import random

OBD_PIDS = {
    0x0C: {"name": "RPM", "formula": lambda a, b: ((a * 256) + b) / 4, "unit": "rpm"},
    0x0D: {"name": "Speed", "formula": lambda a: a, "unit": "km/h"},
    0x05: {"name": "Coolant Temp", "formula": lambda a: a - 40, "unit": "°C"},
    0x0F: {"name": "Intake Temp", "formula": lambda a: a - 40, "unit": "°C"},
    0x11: {"name": "Throttle", "formula": lambda a: (a * 100) / 255, "unit": "%"},
    0x2F: {"name": "Fuel Level", "formula": lambda a: (a * 100) / 255, "unit": "%"},
}

class OBDSimulator:
    def __init__(self):
        self.rpm = 800
        self.speed = 0
        self.coolant_temp = 90
        self.intake_temp = 25
        self.throttle = 0
        self.fuel_level = 75
    
    def update(self):
        self.rpm = max(800, min(6000, self.rpm + random.randint(-100, 100)))
        self.speed = max(0, min(180, self.speed + random.randint(-5, 5)))
        self.coolant_temp = max(70, min(110, self.coolant_temp + random.uniform(-1, 1)))
        self.intake_temp = max(20, min(50, self.intake_temp + random.uniform(-0.5, 0.5)))
        self.throttle = max(0, min(100, self.throttle + random.randint(-10, 10)))
        self.fuel_level = max(0, min(100, self.fuel_level - random.uniform(0, 0.01)))
    
    def get_pid_response(self, pid):
        if pid == 0x0C:
            val = int(self.rpm * 4)
            return [0x41, 0x0C, (val >> 8) & 0xFF, val & 0xFF]
        elif pid == 0x0D:
            return [0x41, 0x0D, int(self.speed)]
        elif pid == 0x05:
            return [0x41, 0x05, int(self.coolant_temp + 40)]
        elif pid == 0x0F:
            return [0x41, 0x0F, int(self.intake_temp + 40)]
        elif pid == 0x11:
            return [0x41, 0x11, int((self.throttle * 255) / 100)]
        elif pid == 0x2F:
            return [0x41, 0x2F, int((self.fuel_level * 255) / 100)]
        return None
