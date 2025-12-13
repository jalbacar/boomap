"""
Predictor de problemas futuros basado en análisis de tendencias.
Analiza el historial de datos para predecir fallos y necesidades de mantenimiento.
"""

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import statistics

from .config import THRESHOLDS, MAINTENANCE_INTERVALS


class RiskLevel(Enum):
    """Nivel de riesgo de un problema futuro"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class TrendDirection(Enum):
    """Dirección de la tendencia"""
    IMPROVING = "improving"
    STABLE = "stable"
    DEGRADING = "degrading"
    CRITICAL_DEGRADATION = "critical_degradation"


@dataclass
class FuturePrediction:
    """Predicción de un problema futuro"""
    component: str
    problem_type: str
    risk_level: RiskLevel
    estimated_time_to_failure: Optional[float]  # horas hasta fallo potencial
    confidence: float  # 0-100%
    trend: TrendDirection
    description: str
    recommendation: str
    data_points: Dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> dict:
        return {
            "component": self.component,
            "problem_type": self.problem_type,
            "risk_level": self.risk_level.value,
            "estimated_time_to_failure_hours": self.estimated_time_to_failure,
            "confidence_percent": round(self.confidence, 1),
            "trend": self.trend.value,
            "description": self.description,
            "recommendation": self.recommendation,
            "data_points": self.data_points,
            "timestamp": self.timestamp
        }


@dataclass
class ComponentForecast:
    """Pronóstico completo de un componente"""
    name: str
    current_health: float
    predicted_health_1h: float
    predicted_health_24h: float
    predicted_health_7d: float
    estimated_remaining_life_hours: float
    trend: TrendDirection
    risk_factors: List[str]
    predictions: List[FuturePrediction]
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "current_health": round(self.current_health, 1),
            "forecast": {
                "health_in_1h": round(self.predicted_health_1h, 1),
                "health_in_24h": round(self.predicted_health_24h, 1),
                "health_in_7d": round(self.predicted_health_7d, 1),
            },
            "estimated_remaining_life_hours": round(self.estimated_remaining_life_hours, 1),
            "trend": self.trend.value,
            "risk_factors": self.risk_factors,
            "predictions": [p.to_dict() for p in self.predictions]
        }


class DataBuffer:
    """Buffer circular para almacenar historial de datos"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.data: deque = deque(maxlen=max_size)
        self.timestamps: deque = deque(maxlen=max_size)
    
    def add(self, value: float, timestamp: float = None):
        self.data.append(value)
        self.timestamps.append(timestamp or time.time())
    
    def get_recent(self, count: int) -> List[float]:
        return list(self.data)[-count:]
    
    def get_average(self, count: int = None) -> Optional[float]:
        data = list(self.data)[-count:] if count else list(self.data)
        return statistics.mean(data) if data else None
    
    def get_trend_slope(self, count: int = 50) -> Optional[float]:
        """Calcula la pendiente de la tendencia (positivo = aumentando)"""
        data = list(self.data)[-count:]
        if len(data) < 10:
            return None
        
        # Regresión lineal simple
        n = len(data)
        x_mean = (n - 1) / 2
        y_mean = statistics.mean(data)
        
        numerator = sum((i - x_mean) * (data[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0
        
        return numerator / denominator
    
    def get_rate_of_change(self) -> Optional[float]:
        """Tasa de cambio por segundo"""
        if len(self.data) < 2:
            return None
        
        data = list(self.data)
        timestamps = list(self.timestamps)
        
        time_diff = timestamps[-1] - timestamps[0]
        if time_diff == 0:
            return 0
        
        value_diff = data[-1] - data[0]
        return value_diff / time_diff
    
    def __len__(self):
        return len(self.data)


class FuturePredictor:
    """
    Motor de predicción de problemas futuros.
    Analiza tendencias históricas para pronosticar fallos.
    """
    
    def __init__(self, history_size: int = 1000):
        # Buffers de historial para cada métrica
        self.history = {
            # OBD
            "rpm": DataBuffer(history_size),
            "speed": DataBuffer(history_size),
            "coolant_temp": DataBuffer(history_size),
            "throttle": DataBuffer(history_size),
            "fuel_level": DataBuffer(history_size),
            # Sensores
            "temperature": DataBuffer(history_size),
            "pressure": DataBuffer(history_size),
            "vibration": DataBuffer(history_size),
            "humidity": DataBuffer(history_size),
        }
        
        # Contadores de eventos críticos
        self.event_counters = {
            "high_rpm_events": 0,
            "overheating_events": 0,
            "high_vibration_events": 0,
            "hard_braking_events": 0,
            "pressure_anomaly_events": 0,
            "high_throttle_events": 0,
        }
        
        # Historial de salud por componente
        self.health_history = {
            "engine": DataBuffer(500),
            "brakes": DataBuffer(500),
            "transmission": DataBuffer(500),
            "tires": DataBuffer(500),
            "battery": DataBuffer(500),
        }
        
        self.start_time = time.time()
        self.last_speed = 0
    
    def record_obd_data(self, obd_data: Dict) -> None:
        """Registra datos OBD en el historial"""
        timestamp = time.time()
        
        for key in ["rpm", "speed", "coolant_temp", "throttle", "fuel_level"]:
            if key in obd_data:
                self.history[key].add(obd_data[key], timestamp)
        
        # Detectar eventos críticos
        rpm = obd_data.get("rpm", 0)
        coolant_temp = obd_data.get("coolant_temp", 90)
        throttle = obd_data.get("throttle", 0)
        speed = obd_data.get("speed", 0)
        
        if rpm > THRESHOLDS["engine"]["rpm_max"]:
            self.event_counters["high_rpm_events"] += 1
        
        if coolant_temp > THRESHOLDS["engine"]["coolant_temp_warning"]:
            self.event_counters["overheating_events"] += 1
        
        if throttle > 85:
            self.event_counters["high_throttle_events"] += 1
        
        # Detectar frenado brusco
        if self.last_speed - speed > 15:
            self.event_counters["hard_braking_events"] += 1
        
        self.last_speed = speed
    
    def record_sensor_data(self, sensor_data: Dict) -> None:
        """Registra datos de sensores en el historial"""
        timestamp = time.time()
        
        for key in ["temperature", "pressure", "vibration", "humidity"]:
            if key in sensor_data:
                self.history[key].add(sensor_data[key], timestamp)
        
        # Detectar eventos críticos
        vibration = sensor_data.get("vibration", 0)
        pressure = sensor_data.get("pressure", 101)
        
        if vibration > THRESHOLDS["brakes"]["vibration_warning"]:
            self.event_counters["high_vibration_events"] += 1
        
        tire_thresh = THRESHOLDS["tires"]
        if pressure < tire_thresh["pressure_min"] or pressure > tire_thresh["pressure_max"]:
            self.event_counters["pressure_anomaly_events"] += 1
    
    def record_component_health(self, component: str, health: float) -> None:
        """Registra la salud de un componente"""
        if component in self.health_history:
            self.health_history[component].add(health, time.time())
    
    def _calculate_trend(self, buffer: DataBuffer) -> TrendDirection:
        """Determina la dirección de la tendencia"""
        slope = buffer.get_trend_slope()
        
        if slope is None:
            return TrendDirection.STABLE
        
        if slope < -0.5:
            return TrendDirection.CRITICAL_DEGRADATION
        elif slope < -0.1:
            return TrendDirection.DEGRADING
        elif slope > 0.1:
            return TrendDirection.IMPROVING
        else:
            return TrendDirection.STABLE
    
    def _estimate_time_to_threshold(self, current: float, threshold: float, 
                                     rate: float, increasing: bool = True) -> Optional[float]:
        """Estima tiempo hasta alcanzar un umbral (en horas)"""
        if rate is None or rate == 0:
            return None
        
        if increasing:
            if current >= threshold or rate <= 0:
                return None
            time_seconds = (threshold - current) / rate
        else:
            if current <= threshold or rate >= 0:
                return None
            time_seconds = (current - threshold) / abs(rate)
        
        return max(0, time_seconds / 3600)  # Convertir a horas
    
    def predict_engine_issues(self) -> List[FuturePrediction]:
        """Predice problemas futuros del motor"""
        predictions = []
        
        # Análisis de temperatura del refrigerante
        coolant_avg = self.history["coolant_temp"].get_average(100)
        coolant_trend = self.history["coolant_temp"].get_trend_slope()
        coolant_rate = self.history["coolant_temp"].get_rate_of_change()
        
        if coolant_avg and coolant_trend:
            warning_thresh = THRESHOLDS["engine"]["coolant_temp_warning"]
            critical_thresh = THRESHOLDS["engine"]["coolant_temp_critical"]
            
            # Tendencia de sobrecalentamiento
            if coolant_trend > 0.05 and coolant_avg > 85:
                time_to_warning = self._estimate_time_to_threshold(
                    coolant_avg, warning_thresh, coolant_rate, increasing=True
                )
                
                risk = RiskLevel.MODERATE
                if coolant_avg > 95:
                    risk = RiskLevel.HIGH
                if coolant_avg > 100:
                    risk = RiskLevel.CRITICAL
                
                predictions.append(FuturePrediction(
                    component="engine",
                    problem_type="overheating",
                    risk_level=risk,
                    estimated_time_to_failure=time_to_warning,
                    confidence=min(90, 50 + len(self.history["coolant_temp"]) / 10),
                    trend=TrendDirection.DEGRADING if coolant_trend > 0 else TrendDirection.STABLE,
                    description=f"Tendencia de aumento de temperatura del motor detectada. "
                               f"Temperatura promedio: {coolant_avg:.1f}°C, tendencia: +{coolant_trend:.2f}°C/muestra.",
                    recommendation="Revisar nivel de refrigerante, termostato y radiador. "
                                  "Evitar conducción agresiva hasta inspección.",
                    data_points={
                        "current_temp": coolant_avg,
                        "trend_slope": coolant_trend,
                        "warning_threshold": warning_thresh,
                        "overheating_events": self.event_counters["overheating_events"]
                    }
                ))
        
        # Análisis de RPM excesivo
        rpm_avg = self.history["rpm"].get_average(100)
        high_rpm_ratio = self.event_counters["high_rpm_events"] / max(1, len(self.history["rpm"]))
        
        if high_rpm_ratio > 0.1:  # Más del 10% del tiempo en RPM alto
            wear_rate_per_hour = high_rpm_ratio * 2  # Factor de desgaste acelerado
            estimated_extra_wear = wear_rate_per_hour * 100  # % de desgaste extra por 100h
            
            predictions.append(FuturePrediction(
                component="engine",
                problem_type="excessive_wear",
                risk_level=RiskLevel.HIGH if high_rpm_ratio > 0.2 else RiskLevel.MODERATE,
                estimated_time_to_failure=500 / (1 + wear_rate_per_hour),  # Vida útil reducida
                confidence=min(85, 40 + high_rpm_ratio * 200),
                trend=TrendDirection.DEGRADING,
                description=f"Uso frecuente en RPM elevado ({high_rpm_ratio*100:.1f}% del tiempo). "
                           f"Esto acelera el desgaste del motor significativamente.",
                recommendation="Reducir revoluciones durante la conducción. Cambiar marchas antes. "
                              "Considerar revisión de aceite más frecuente.",
                data_points={
                    "high_rpm_ratio": high_rpm_ratio,
                    "avg_rpm": rpm_avg,
                    "high_rpm_events": self.event_counters["high_rpm_events"],
                    "estimated_extra_wear_per_100h": estimated_extra_wear
                }
            ))
        
        return predictions
    
    def predict_brake_issues(self) -> List[FuturePrediction]:
        """Predice problemas futuros de frenos"""
        predictions = []
        
        vibration_avg = self.history["vibration"].get_average(100)
        vibration_trend = self.history["vibration"].get_trend_slope()
        hard_braking_count = self.event_counters["hard_braking_events"]
        
        if vibration_avg:
            warning_thresh = THRESHOLDS["brakes"]["vibration_warning"]
            
            # Vibración en aumento
            if vibration_trend and vibration_trend > 0.02:
                time_to_warning = None
                if vibration_avg < warning_thresh:
                    rate = self.history["vibration"].get_rate_of_change()
                    time_to_warning = self._estimate_time_to_threshold(
                        vibration_avg, warning_thresh, rate, increasing=True
                    )
                
                risk = RiskLevel.LOW
                if vibration_avg > 3:
                    risk = RiskLevel.MODERATE
                if vibration_avg > 5:
                    risk = RiskLevel.HIGH
                
                predictions.append(FuturePrediction(
                    component="brakes",
                    problem_type="wear_degradation",
                    risk_level=risk,
                    estimated_time_to_failure=time_to_warning,
                    confidence=min(80, 45 + len(self.history["vibration"]) / 15),
                    trend=TrendDirection.DEGRADING,
                    description=f"Aumento progresivo de vibración detectado (promedio: {vibration_avg:.2f}). "
                               f"Puede indicar desgaste de pastillas o discos de freno.",
                    recommendation="Inspeccionar pastillas y discos de freno. "
                                  "Si la vibración persiste, revisar suspensión y alineación.",
                    data_points={
                        "current_vibration": vibration_avg,
                        "trend_slope": vibration_trend,
                        "hard_braking_events": hard_braking_count
                    }
                ))
        
        # Frenados bruscos frecuentes
        runtime_hours = (time.time() - self.start_time) / 3600
        if runtime_hours > 0.01:  # Al menos algo de tiempo
            braking_rate = hard_braking_count / runtime_hours
            
            if braking_rate > 10:  # Más de 10 frenados bruscos por hora
                predictions.append(FuturePrediction(
                    component="brakes",
                    problem_type="accelerated_wear",
                    risk_level=RiskLevel.MODERATE if braking_rate < 20 else RiskLevel.HIGH,
                    estimated_time_to_failure=MAINTENANCE_INTERVALS["brake_inspection"] / (1 + braking_rate/20),
                    confidence=70,
                    trend=TrendDirection.DEGRADING,
                    description=f"Frecuencia alta de frenados bruscos: {braking_rate:.1f}/hora. "
                               f"Esto reduce significativamente la vida útil de los frenos.",
                    recommendation="Mantener mayor distancia de seguridad. Anticipar frenadas. "
                                  "Programar inspección de frenos antes de lo habitual.",
                    data_points={
                        "hard_braking_rate_per_hour": braking_rate,
                        "total_hard_brakings": hard_braking_count
                    }
                ))
        
        return predictions
    
    def predict_tire_issues(self) -> List[FuturePrediction]:
        """Predice problemas futuros de neumáticos"""
        predictions = []
        
        pressure_avg = self.history["pressure"].get_average(100)
        pressure_trend = self.history["pressure"].get_trend_slope()
        anomaly_count = self.event_counters["pressure_anomaly_events"]
        
        if pressure_avg:
            tire_thresh = THRESHOLDS["tires"]
            
            # Presión baja en tendencia
            if pressure_trend and pressure_trend < -0.01:
                time_to_low = self._estimate_time_to_threshold(
                    pressure_avg, tire_thresh["pressure_min"], 
                    self.history["pressure"].get_rate_of_change(), 
                    increasing=False
                )
                
                predictions.append(FuturePrediction(
                    component="tires",
                    problem_type="pressure_loss",
                    risk_level=RiskLevel.MODERATE if pressure_avg > 98 else RiskLevel.HIGH,
                    estimated_time_to_failure=time_to_low,
                    confidence=min(75, 50 + abs(pressure_trend) * 100),
                    trend=TrendDirection.DEGRADING,
                    description=f"Tendencia de pérdida de presión detectada. "
                               f"Presión actual: {pressure_avg:.1f} kPa, tendencia: {pressure_trend:.3f}/muestra.",
                    recommendation="Verificar presión de neumáticos. Inspeccionar posibles pinchazos o fugas. "
                                  "Revisar válvulas de inflado.",
                    data_points={
                        "current_pressure": pressure_avg,
                        "trend_slope": pressure_trend,
                        "anomaly_events": anomaly_count,
                        "min_threshold": tire_thresh["pressure_min"]
                    }
                ))
        
        # Desgaste por velocidad alta
        speed_avg = self.history["speed"].get_average(100)
        if speed_avg and speed_avg > 100:
            wear_factor = (speed_avg - 80) / 40  # Factor de desgaste por velocidad
            
            predictions.append(FuturePrediction(
                component="tires",
                problem_type="high_speed_wear",
                risk_level=RiskLevel.MODERATE if speed_avg < 130 else RiskLevel.HIGH,
                estimated_time_to_failure=MAINTENANCE_INTERVALS["tire_rotation"] / (1 + wear_factor),
                confidence=65,
                trend=TrendDirection.DEGRADING,
                description=f"Velocidad media elevada: {speed_avg:.0f} km/h. "
                           f"El desgaste de neumáticos se acelera exponencialmente con la velocidad.",
                recommendation="Reducir velocidad media de conducción. "
                              "Rotar neumáticos más frecuentemente. Verificar profundidad del dibujo.",
                data_points={
                    "avg_speed": speed_avg,
                    "wear_factor": wear_factor
                }
            ))
        
        return predictions
    
    def predict_transmission_issues(self) -> List[FuturePrediction]:
        """Predice problemas futuros de transmisión"""
        predictions = []
        
        rpm_avg = self.history["rpm"].get_average(100)
        speed_avg = self.history["speed"].get_average(100)
        throttle_avg = self.history["throttle"].get_average(100)
        
        if rpm_avg and speed_avg and speed_avg > 0:
            # Ratio RPM/velocidad anómalo
            ratio = rpm_avg / speed_avg
            
            if ratio > THRESHOLDS["transmission"]["rpm_speed_ratio_warning"]:
                predictions.append(FuturePrediction(
                    component="transmission",
                    problem_type="gear_stress",
                    risk_level=RiskLevel.MODERATE,
                    estimated_time_to_failure=800,  # Estimación conservadora
                    confidence=60,
                    trend=TrendDirection.DEGRADING,
                    description=f"Ratio RPM/velocidad elevado: {ratio:.1f}. "
                               f"Indica posible uso inadecuado de marchas o estrés en transmisión.",
                    recommendation="Cambiar a marchas más altas antes. Evitar forzar el motor en marchas bajas. "
                                  "Revisar estado del embrague si es manual.",
                    data_points={
                        "rpm_speed_ratio": ratio,
                        "avg_rpm": rpm_avg,
                        "avg_speed": speed_avg
                    }
                ))
        
        # Uso agresivo del acelerador
        if throttle_avg and throttle_avg > 60:
            high_throttle_ratio = self.event_counters["high_throttle_events"] / max(1, len(self.history["throttle"]))
            
            if high_throttle_ratio > 0.15:
                predictions.append(FuturePrediction(
                    component="transmission",
                    problem_type="aggressive_driving_wear",
                    risk_level=RiskLevel.MODERATE,
                    estimated_time_to_failure=MAINTENANCE_INTERVALS["transmission_service"] * 0.7,
                    confidence=55,
                    trend=TrendDirection.DEGRADING,
                    description=f"Estilo de conducción agresivo detectado. "
                               f"Acelerador alto {high_throttle_ratio*100:.0f}% del tiempo.",
                    recommendation="Suavizar aceleraciones. Conducción más progresiva. "
                                  "Considerar revisión de transmisión anticipada.",
                    data_points={
                        "high_throttle_ratio": high_throttle_ratio,
                        "avg_throttle": throttle_avg
                    }
                ))
        
        return predictions
    
    def predict_battery_issues(self) -> List[FuturePrediction]:
        """Predice problemas futuros de batería"""
        predictions = []
        
        temp_avg = self.history["temperature"].get_average(100)
        
        if temp_avg:
            battery_thresh = THRESHOLDS["battery"]
            
            # Temperatura extrema afecta batería
            if temp_avg > battery_thresh["temp_max"] - 5:
                degradation_rate = (temp_avg - 35) / 10  # Factor de degradación
                
                predictions.append(FuturePrediction(
                    component="battery",
                    problem_type="heat_degradation",
                    risk_level=RiskLevel.MODERATE if temp_avg < 40 else RiskLevel.HIGH,
                    estimated_time_to_failure=2000 / (1 + degradation_rate),
                    confidence=50,
                    trend=TrendDirection.DEGRADING,
                    description=f"Temperatura ambiente elevada: {temp_avg:.1f}°C. "
                               f"Las altas temperaturas aceleran la degradación de la batería.",
                    recommendation="Aparcar en sombra cuando sea posible. "
                                  "Verificar estado de batería si el vehículo tiene dificultades de arranque.",
                    data_points={
                        "avg_temperature": temp_avg,
                        "degradation_factor": degradation_rate
                    }
                ))
            
            elif temp_avg < battery_thresh["temp_min"] + 5:
                predictions.append(FuturePrediction(
                    component="battery",
                    problem_type="cold_performance",
                    risk_level=RiskLevel.LOW,
                    estimated_time_to_failure=None,
                    confidence=60,
                    trend=TrendDirection.STABLE,
                    description=f"Temperatura ambiente baja: {temp_avg:.1f}°C. "
                               f"El frío reduce la capacidad de la batería temporalmente.",
                    recommendation="Precalentar el vehículo antes de viajes largos. "
                                  "Verificar carga de batería en invierno.",
                    data_points={
                        "avg_temperature": temp_avg
                    }
                ))
        
        return predictions
    
    def get_component_forecast(self, component: str, current_health: float) -> ComponentForecast:
        """Genera pronóstico completo para un componente"""
        
        # Registrar salud actual
        self.record_component_health(component, current_health)
        
        # Obtener tendencia de salud
        health_buffer = self.health_history.get(component)
        trend = self._calculate_trend(health_buffer) if health_buffer else TrendDirection.STABLE
        
        # Calcular degradación por hora basada en tendencia
        health_slope = health_buffer.get_trend_slope() if health_buffer else 0
        degradation_per_hour = abs(health_slope) * 3600 / max(1, len(health_buffer)) if health_slope else 0.1
        
        # Predicciones de salud futura
        predicted_1h = max(0, current_health - degradation_per_hour * 1)
        predicted_24h = max(0, current_health - degradation_per_hour * 24)
        predicted_7d = max(0, current_health - degradation_per_hour * 168)
        
        # Vida útil restante estimada
        if degradation_per_hour > 0:
            remaining_life = current_health / degradation_per_hour
        else:
            remaining_life = 10000  # Muy alta si no hay degradación
        
        # Obtener predicciones específicas del componente
        predictions = []
        risk_factors = []
        
        if component == "engine":
            predictions = self.predict_engine_issues()
            if self.event_counters["high_rpm_events"] > 10:
                risk_factors.append("Uso frecuente en RPM alto")
            if self.event_counters["overheating_events"] > 5:
                risk_factors.append("Episodios de sobrecalentamiento")
        
        elif component == "brakes":
            predictions = self.predict_brake_issues()
            if self.event_counters["hard_braking_events"] > 20:
                risk_factors.append("Frenados bruscos frecuentes")
            if self.event_counters["high_vibration_events"] > 10:
                risk_factors.append("Vibración elevada detectada")
        
        elif component == "tires":
            predictions = self.predict_tire_issues()
            if self.event_counters["pressure_anomaly_events"] > 10:
                risk_factors.append("Anomalías de presión")
            speed_avg = self.history["speed"].get_average(50)
            if speed_avg and speed_avg > 110:
                risk_factors.append("Velocidad media alta")
        
        elif component == "transmission":
            predictions = self.predict_transmission_issues()
            if self.event_counters["high_throttle_events"] > 20:
                risk_factors.append("Conducción agresiva")
        
        elif component == "battery":
            predictions = self.predict_battery_issues()
            temp_avg = self.history["temperature"].get_average(50)
            if temp_avg and (temp_avg > 40 or temp_avg < 0):
                risk_factors.append("Temperatura ambiente extrema")
        
        return ComponentForecast(
            name=component,
            current_health=current_health,
            predicted_health_1h=predicted_1h,
            predicted_health_24h=predicted_24h,
            predicted_health_7d=predicted_7d,
            estimated_remaining_life_hours=remaining_life,
            trend=trend,
            risk_factors=risk_factors,
            predictions=predictions
        )
    
    def get_all_predictions(self) -> List[FuturePrediction]:
        """Obtiene todas las predicciones de todos los componentes"""
        all_predictions = []
        all_predictions.extend(self.predict_engine_issues())
        all_predictions.extend(self.predict_brake_issues())
        all_predictions.extend(self.predict_tire_issues())
        all_predictions.extend(self.predict_transmission_issues())
        all_predictions.extend(self.predict_battery_issues())
        
        # Ordenar por nivel de riesgo
        risk_order = {RiskLevel.CRITICAL: 0, RiskLevel.HIGH: 1, RiskLevel.MODERATE: 2, RiskLevel.LOW: 3}
        all_predictions.sort(key=lambda p: risk_order.get(p.risk_level, 4))
        
        return all_predictions
    
    def get_summary(self) -> Dict:
        """Resumen del estado predictivo"""
        all_predictions = self.get_all_predictions()
        
        risk_counts = {"critical": 0, "high": 0, "moderate": 0, "low": 0}
        for pred in all_predictions:
            risk_counts[pred.risk_level.value] += 1
        
        runtime_hours = (time.time() - self.start_time) / 3600
        
        return {
            "total_predictions": len(all_predictions),
            "risk_distribution": risk_counts,
            "event_counters": self.event_counters.copy(),
            "data_points_collected": {
                key: len(buffer) for key, buffer in self.history.items()
            },
            "runtime_hours": round(runtime_hours, 2),
            "highest_risk_predictions": [p.to_dict() for p in all_predictions[:3]]
        }
