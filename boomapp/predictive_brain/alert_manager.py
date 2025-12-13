"""
Gestor de alertas para mantenimiento predictivo.
Genera alertas basadas en umbrales y predicciones de desgaste.
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from enum import Enum
from .config import THRESHOLDS, ALERT_LEVELS


class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class Alert:
    """Representa una alerta del sistema"""
    id: str
    level: AlertLevel
    component: str
    message: str
    timestamp: float = field(default_factory=time.time)
    data: Dict = field(default_factory=dict)
    acknowledged: bool = False
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "level": self.level.value,
            "component": self.component,
            "message": self.message,
            "timestamp": self.timestamp,
            "data": self.data,
            "acknowledged": self.acknowledged
        }


class AlertManager:
    """
    Gestor de alertas de mantenimiento predictivo.
    Evalúa condiciones y genera alertas cuando se superan umbrales.
    """
    
    def __init__(self):
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.alert_counter = 0
        self.cooldown_times: Dict[str, float] = {}  # Evitar spam de alertas
        self.cooldown_duration = 30  # segundos entre alertas del mismo tipo
        
        # Callbacks para notificaciones
        self.on_new_alert: Optional[Callable[[Alert], None]] = None
        self.on_alert_cleared: Optional[Callable[[str], None]] = None
    
    def _generate_alert_id(self) -> str:
        self.alert_counter += 1
        return f"ALT-{int(time.time())}-{self.alert_counter:04d}"
    
    def _can_send_alert(self, alert_key: str) -> bool:
        """Verifica si se puede enviar alerta (cooldown)"""
        if alert_key not in self.cooldown_times:
            return True
        return time.time() - self.cooldown_times[alert_key] > self.cooldown_duration
    
    def _create_alert(self, level: AlertLevel, component: str, message: str, data: Dict = None) -> Optional[Alert]:
        """Crea una nueva alerta si no está en cooldown"""
        alert_key = f"{component}:{level.value}"
        
        if not self._can_send_alert(alert_key):
            return None
        
        alert = Alert(
            id=self._generate_alert_id(),
            level=level,
            component=component,
            message=message,
            data=data or {}
        )
        
        self.active_alerts[alert.id] = alert
        self.alert_history.append(alert)
        self.cooldown_times[alert_key] = time.time()
        
        if self.on_new_alert:
            self.on_new_alert(alert)
        
        return alert
    
    def evaluate_obd_data(self, obd_data: Dict) -> List[Alert]:
        """Evalúa datos OBD y genera alertas si es necesario"""
        alerts = []
        
        rpm = obd_data.get("rpm", 0)
        coolant_temp = obd_data.get("coolant_temp", 90)
        throttle = obd_data.get("throttle", 0)
        fuel_level = obd_data.get("fuel_level", 100)
        speed = obd_data.get("speed", 0)
        
        engine_thresholds = THRESHOLDS["engine"]
        
        # Alertas de motor - RPM
        if rpm > engine_thresholds["rpm_critical"]:
            alert = self._create_alert(
                AlertLevel.EMERGENCY,
                "engine",
                f"RPM crítico: {rpm:.0f} RPM. Riesgo de daño al motor.",
                {"rpm": rpm, "threshold": engine_thresholds["rpm_critical"]}
            )
            if alert:
                alerts.append(alert)
        elif rpm > engine_thresholds["rpm_max"]:
            alert = self._create_alert(
                AlertLevel.WARNING,
                "engine",
                f"RPM elevado: {rpm:.0f} RPM. Reducir revoluciones.",
                {"rpm": rpm, "threshold": engine_thresholds["rpm_max"]}
            )
            if alert:
                alerts.append(alert)
        
        # Alertas de temperatura
        if coolant_temp > engine_thresholds["coolant_temp_critical"]:
            alert = self._create_alert(
                AlertLevel.EMERGENCY,
                "engine",
                f"¡SOBRECALENTAMIENTO! Temperatura: {coolant_temp:.1f}°C. Detener vehículo.",
                {"coolant_temp": coolant_temp, "threshold": engine_thresholds["coolant_temp_critical"]}
            )
            if alert:
                alerts.append(alert)
        elif coolant_temp > engine_thresholds["coolant_temp_warning"]:
            alert = self._create_alert(
                AlertLevel.WARNING,
                "engine",
                f"Temperatura elevada: {coolant_temp:.1f}°C. Monitorear.",
                {"coolant_temp": coolant_temp, "threshold": engine_thresholds["coolant_temp_warning"]}
            )
            if alert:
                alerts.append(alert)
        
        # Alerta de combustible bajo
        if fuel_level < 15:
            alert = self._create_alert(
                AlertLevel.WARNING,
                "fuel",
                f"Combustible bajo: {fuel_level:.0f}%. Repostar pronto.",
                {"fuel_level": fuel_level}
            )
            if alert:
                alerts.append(alert)
        elif fuel_level < 5:
            alert = self._create_alert(
                AlertLevel.CRITICAL,
                "fuel",
                f"¡Combustible crítico! {fuel_level:.0f}%. Riesgo de quedarse sin combustible.",
                {"fuel_level": fuel_level}
            )
            if alert:
                alerts.append(alert)
        
        return alerts
    
    def evaluate_sensor_data(self, sensor_data: Dict) -> List[Alert]:
        """Evalúa datos de sensores y genera alertas"""
        alerts = []
        
        vibration = sensor_data.get("vibration", 0)
        pressure = sensor_data.get("pressure", 101)
        temperature = sensor_data.get("temperature", 25)
        
        # Alertas de vibración (frenos/neumáticos)
        brake_thresholds = THRESHOLDS["brakes"]
        if vibration > brake_thresholds["vibration_critical"]:
            alert = self._create_alert(
                AlertLevel.CRITICAL,
                "brakes",
                f"Vibración crítica: {vibration:.1f}. Revisar frenos y neumáticos.",
                {"vibration": vibration, "threshold": brake_thresholds["vibration_critical"]}
            )
            if alert:
                alerts.append(alert)
        elif vibration > brake_thresholds["vibration_warning"]:
            alert = self._create_alert(
                AlertLevel.WARNING,
                "brakes",
                f"Vibración elevada: {vibration:.1f}. Posible desgaste.",
                {"vibration": vibration, "threshold": brake_thresholds["vibration_warning"]}
            )
            if alert:
                alerts.append(alert)
        
        # Alertas de presión (neumáticos)
        tire_thresholds = THRESHOLDS["tires"]
        if pressure < tire_thresholds["pressure_min"]:
            alert = self._create_alert(
                AlertLevel.WARNING,
                "tires",
                f"Presión baja: {pressure:.1f} kPa. Revisar neumáticos.",
                {"pressure": pressure, "threshold": tire_thresholds["pressure_min"]}
            )
            if alert:
                alerts.append(alert)
        elif pressure > tire_thresholds["pressure_max"]:
            alert = self._create_alert(
                AlertLevel.WARNING,
                "tires",
                f"Presión alta: {pressure:.1f} kPa. Ajustar presión.",
                {"pressure": pressure, "threshold": tire_thresholds["pressure_max"]}
            )
            if alert:
                alerts.append(alert)
        
        # Alertas de temperatura ambiente (batería)
        battery_thresholds = THRESHOLDS["battery"]
        if temperature > battery_thresholds["temp_max"]:
            alert = self._create_alert(
                AlertLevel.INFO,
                "battery",
                f"Temperatura ambiente alta: {temperature:.1f}°C. Puede afectar batería.",
                {"temperature": temperature}
            )
            if alert:
                alerts.append(alert)
        
        return alerts
    
    def evaluate_wear_state(self, wear_state: Dict) -> List[Alert]:
        """Evalúa estado de desgaste y genera alertas de mantenimiento"""
        alerts = []
        components = wear_state.get("components", {})
        
        for comp_name, comp_data in components.items():
            health = comp_data.get("health_score", 100)
            hours_until = comp_data.get("hours_until_maintenance", 999)
            status = comp_data.get("status", "good")
            
            # Alerta por salud baja
            if status == "failure":
                alert = self._create_alert(
                    AlertLevel.EMERGENCY,
                    comp_name,
                    f"¡FALLO EN {comp_name.upper()}! Salud: {health:.0f}%. Servicio inmediato requerido.",
                    {"health_score": health, "component": comp_name}
                )
                if alert:
                    alerts.append(alert)
            elif status == "critical":
                alert = self._create_alert(
                    AlertLevel.CRITICAL,
                    comp_name,
                    f"{comp_name.capitalize()} en estado crítico. Salud: {health:.0f}%. Programar servicio.",
                    {"health_score": health, "component": comp_name}
                )
                if alert:
                    alerts.append(alert)
            elif status == "warning":
                alert = self._create_alert(
                    AlertLevel.WARNING,
                    comp_name,
                    f"{comp_name.capitalize()} requiere atención. Salud: {health:.0f}%.",
                    {"health_score": health, "component": comp_name}
                )
                if alert:
                    alerts.append(alert)
            
            # Alerta por mantenimiento próximo
            if hours_until <= 0:
                alert = self._create_alert(
                    AlertLevel.CRITICAL,
                    comp_name,
                    f"Mantenimiento de {comp_name} VENCIDO. Programar servicio inmediatamente.",
                    {"hours_overdue": abs(hours_until), "component": comp_name}
                )
                if alert:
                    alerts.append(alert)
            elif hours_until < 10:
                alert = self._create_alert(
                    AlertLevel.WARNING,
                    comp_name,
                    f"Mantenimiento de {comp_name} próximo: {hours_until:.1f} horas restantes.",
                    {"hours_until_maintenance": hours_until, "component": comp_name}
                )
                if alert:
                    alerts.append(alert)
        
        return alerts
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Marca una alerta como reconocida"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].acknowledged = True
            return True
        return False
    
    def clear_alert(self, alert_id: str) -> bool:
        """Elimina una alerta activa"""
        if alert_id in self.active_alerts:
            del self.active_alerts[alert_id]
            if self.on_alert_cleared:
                self.on_alert_cleared(alert_id)
            return True
        return False
    
    def get_active_alerts(self) -> List[Dict]:
        """Retorna todas las alertas activas"""
        return [alert.to_dict() for alert in self.active_alerts.values()]
    
    def get_alerts_by_level(self, level: AlertLevel) -> List[Dict]:
        """Retorna alertas filtradas por nivel"""
        return [
            alert.to_dict() 
            for alert in self.active_alerts.values() 
            if alert.level == level
        ]
    
    def get_alert_summary(self) -> Dict:
        """Retorna resumen de alertas activas"""
        summary = {
            "total": len(self.active_alerts),
            "by_level": {
                "emergency": 0,
                "critical": 0,
                "warning": 0,
                "info": 0
            },
            "unacknowledged": 0
        }
        
        for alert in self.active_alerts.values():
            summary["by_level"][alert.level.value] += 1
            if not alert.acknowledged:
                summary["unacknowledged"] += 1
        
        return summary
