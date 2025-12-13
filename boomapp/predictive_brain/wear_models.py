"""
Modelos de análisis de desgaste para componentes vehiculares.
Calcula el desgaste acumulado basado en patrones de uso.
"""

import time
from dataclasses import dataclass, field
from typing import Dict, Optional
from .config import THRESHOLDS, WEAR_WEIGHTS, MAINTENANCE_INTERVALS


@dataclass
class ComponentWear:
    """Estado de desgaste de un componente"""
    name: str
    wear_percentage: float = 0.0  # 0-100%
    health_score: float = 100.0   # 100 = perfecto, 0 = fallo
    hours_until_maintenance: float = 0.0
    last_maintenance: Optional[float] = None
    accumulated_stress: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "wear_percentage": round(self.wear_percentage, 2),
            "health_score": round(self.health_score, 2),
            "hours_until_maintenance": round(self.hours_until_maintenance, 1),
            "status": self._get_status()
        }
    
    def _get_status(self) -> str:
        if self.health_score >= 80:
            return "good"
        elif self.health_score >= 50:
            return "warning"
        elif self.health_score >= 20:
            return "critical"
        return "failure"


@dataclass
class VehicleWearState:
    """Estado de desgaste completo del vehículo"""
    engine: ComponentWear = field(default_factory=lambda: ComponentWear("engine"))
    brakes: ComponentWear = field(default_factory=lambda: ComponentWear("brakes"))
    transmission: ComponentWear = field(default_factory=lambda: ComponentWear("transmission"))
    tires: ComponentWear = field(default_factory=lambda: ComponentWear("tires"))
    battery: ComponentWear = field(default_factory=lambda: ComponentWear("battery"))
    
    # Contadores de eventos
    high_rpm_seconds: float = 0.0
    overheating_seconds: float = 0.0
    hard_braking_count: int = 0
    high_vibration_seconds: float = 0.0
    pressure_anomaly_seconds: float = 0.0
    
    # Timestamps
    start_time: float = field(default_factory=time.time)
    total_runtime_hours: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            "components": {
                "engine": self.engine.to_dict(),
                "brakes": self.brakes.to_dict(),
                "transmission": self.transmission.to_dict(),
                "tires": self.tires.to_dict(),
                "battery": self.battery.to_dict(),
            },
            "runtime_hours": round(self.total_runtime_hours, 2),
            "overall_health": self._calculate_overall_health()
        }
    
    def _calculate_overall_health(self) -> float:
        components = [self.engine, self.brakes, self.transmission, self.tires, self.battery]
        return round(sum(c.health_score for c in components) / len(components), 2)


class WearAnalyzer:
    """
    Analizador de desgaste vehicular.
    Procesa datos de sensores y calcula el desgaste de componentes.
    """
    
    def __init__(self):
        self.state = VehicleWearState()
        self.last_update = time.time()
        self.last_obd_data: Dict = {}
        self.last_sensor_data: Dict = {}
        
        # Inicializar horas hasta mantenimiento
        self.state.engine.hours_until_maintenance = MAINTENANCE_INTERVALS["oil_change"]
        self.state.brakes.hours_until_maintenance = MAINTENANCE_INTERVALS["brake_inspection"]
        self.state.transmission.hours_until_maintenance = MAINTENANCE_INTERVALS["transmission_service"]
        self.state.tires.hours_until_maintenance = MAINTENANCE_INTERVALS["tire_rotation"]
        self.state.battery.hours_until_maintenance = MAINTENANCE_INTERVALS["coolant_check"]
    
    def process_obd_data(self, obd_data: Dict) -> None:
        """Procesa datos OBD y actualiza estado de desgaste"""
        current_time = time.time()
        delta_seconds = current_time - self.last_update
        delta_hours = delta_seconds / 3600
        
        rpm = obd_data.get("rpm", 0)
        speed = obd_data.get("speed", 0)
        coolant_temp = obd_data.get("coolant_temp", 90)
        throttle = obd_data.get("throttle", 0)
        
        # Actualizar tiempo de ejecución
        self.state.total_runtime_hours += delta_hours
        
        # Análisis de motor
        self._analyze_engine(rpm, coolant_temp, throttle, delta_seconds)
        
        # Análisis de transmisión
        self._analyze_transmission(rpm, speed, throttle, delta_seconds)
        
        # Detectar frenado brusco
        if self.last_obd_data:
            prev_speed = self.last_obd_data.get("speed", 0)
            if prev_speed - speed > 20:  # Reducción brusca de velocidad
                self.state.hard_braking_count += 1
        
        # Actualizar contadores de mantenimiento
        self._update_maintenance_counters(delta_hours)
        
        self.last_obd_data = obd_data.copy()
        self.last_update = current_time
    
    def process_sensor_data(self, sensor_data: Dict) -> None:
        """Procesa datos de sensores ambientales"""
        current_time = time.time()
        delta_seconds = current_time - self.last_update
        
        temperature = sensor_data.get("temperature", 25)
        pressure = sensor_data.get("pressure", 101)
        vibration = sensor_data.get("vibration", 0)
        
        # Análisis de frenos (vibración)
        self._analyze_brakes(vibration, delta_seconds)
        
        # Análisis de neumáticos
        self._analyze_tires(pressure, vibration, delta_seconds)
        
        # Análisis de batería (temperatura ambiente)
        self._analyze_battery(temperature)
        
        self.last_sensor_data = sensor_data.copy()
    
    def _analyze_engine(self, rpm: float, coolant_temp: float, throttle: float, delta_s: float) -> None:
        """Analiza desgaste del motor"""
        thresholds = THRESHOLDS["engine"]
        stress = 0.0
        
        # RPM alto
        if rpm > thresholds["rpm_max"]:
            self.state.high_rpm_seconds += delta_s
            stress += 0.5
        if rpm > thresholds["rpm_critical"]:
            stress += 0.5
        
        # Sobrecalentamiento
        if coolant_temp > thresholds["coolant_temp_warning"]:
            self.state.overheating_seconds += delta_s
            stress += 0.3
        if coolant_temp > thresholds["coolant_temp_critical"]:
            stress += 0.7
        
        # Aceleración agresiva
        if throttle > 80:
            stress += 0.2
        
        # Actualizar desgaste
        self.state.engine.accumulated_stress += stress * delta_s
        wear_rate = self.state.engine.accumulated_stress / 36000  # Normalizar a horas
        self.state.engine.wear_percentage = min(100, wear_rate)
        self.state.engine.health_score = max(0, 100 - self.state.engine.wear_percentage)
    
    def _analyze_brakes(self, vibration: float, delta_s: float) -> None:
        """Analiza desgaste de frenos"""
        thresholds = THRESHOLDS["brakes"]
        stress = 0.0
        
        if vibration > thresholds["vibration_warning"]:
            self.state.high_vibration_seconds += delta_s
            stress += 0.4
        if vibration > thresholds["vibration_critical"]:
            stress += 0.6
        
        # Factor de frenados bruscos
        braking_stress = self.state.hard_braking_count * 0.1
        
        self.state.brakes.accumulated_stress += stress * delta_s + braking_stress
        wear_rate = self.state.brakes.accumulated_stress / 36000
        self.state.brakes.wear_percentage = min(100, wear_rate)
        self.state.brakes.health_score = max(0, 100 - self.state.brakes.wear_percentage)
    
    def _analyze_transmission(self, rpm: float, speed: float, throttle: float, delta_s: float) -> None:
        """Analiza desgaste de transmisión"""
        stress = 0.0
        
        # Ratio RPM/velocidad anómalo (indica estrés en transmisión)
        if speed > 0:
            ratio = rpm / speed
            if ratio > THRESHOLDS["transmission"]["rpm_speed_ratio_warning"]:
                stress += 0.5
        
        # Alta carga (throttle alto + RPM alto)
        if throttle > 70 and rpm > 4000:
            stress += 0.3
        
        self.state.transmission.accumulated_stress += stress * delta_s
        wear_rate = self.state.transmission.accumulated_stress / 36000
        self.state.transmission.wear_percentage = min(100, wear_rate)
        self.state.transmission.health_score = max(0, 100 - self.state.transmission.wear_percentage)
    
    def _analyze_tires(self, pressure: float, vibration: float, delta_s: float) -> None:
        """Analiza desgaste de neumáticos"""
        thresholds = THRESHOLDS["tires"]
        stress = 0.0
        
        # Presión anómala
        if pressure < thresholds["pressure_min"] or pressure > thresholds["pressure_max"]:
            self.state.pressure_anomaly_seconds += delta_s
            stress += 0.4
        
        # Vibración alta
        if vibration > thresholds["vibration_warning"]:
            stress += 0.3
        
        # Velocidad alta (del último OBD)
        speed = self.last_obd_data.get("speed", 0)
        if speed > 120:
            stress += 0.3
        
        self.state.tires.accumulated_stress += stress * delta_s
        wear_rate = self.state.tires.accumulated_stress / 36000
        self.state.tires.wear_percentage = min(100, wear_rate)
        self.state.tires.health_score = max(0, 100 - self.state.tires.wear_percentage)
    
    def _analyze_battery(self, ambient_temp: float) -> None:
        """Analiza estado de batería"""
        thresholds = THRESHOLDS["battery"]
        
        # Temperatura extrema afecta batería
        if ambient_temp < thresholds["temp_min"] or ambient_temp > thresholds["temp_max"]:
            self.state.battery.accumulated_stress += 0.1
        
        wear_rate = self.state.battery.accumulated_stress / 1000
        self.state.battery.wear_percentage = min(100, wear_rate)
        self.state.battery.health_score = max(0, 100 - self.state.battery.wear_percentage)
    
    def _update_maintenance_counters(self, delta_hours: float) -> None:
        """Actualiza contadores de mantenimiento"""
        for component in [self.state.engine, self.state.brakes, 
                          self.state.transmission, self.state.tires, self.state.battery]:
            component.hours_until_maintenance = max(0, component.hours_until_maintenance - delta_hours)
    
    def get_wear_state(self) -> Dict:
        """Retorna estado actual de desgaste"""
        return self.state.to_dict()
    
    def reset_maintenance(self, component: str) -> None:
        """Resetea contador de mantenimiento para un componente"""
        intervals = {
            "engine": MAINTENANCE_INTERVALS["oil_change"],
            "brakes": MAINTENANCE_INTERVALS["brake_inspection"],
            "transmission": MAINTENANCE_INTERVALS["transmission_service"],
            "tires": MAINTENANCE_INTERVALS["tire_rotation"],
            "battery": MAINTENANCE_INTERVALS["coolant_check"],
        }
        
        if hasattr(self.state, component):
            comp = getattr(self.state, component)
            comp.hours_until_maintenance = intervals.get(component, 500)
            comp.last_maintenance = time.time()
