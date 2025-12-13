# Configuración del módulo de mantenimiento predictivo

# Topics MQTT
TOPICS = {
    "obd_input": "boomapp/vehicle/obd",
    "sensors_input": "boomapp/vehicle/sensors",
    "predictions_output": "boomapp/predictions/wear",
    "alerts_output": "boomapp/predictions/alerts",
}

# Umbrales de alerta para componentes
THRESHOLDS = {
    "engine": {
        "rpm_max": 6500,
        "rpm_critical": 7000,
        "coolant_temp_warning": 100,
        "coolant_temp_critical": 110,
    },
    "brakes": {
        "vibration_warning": 5.0,
        "vibration_critical": 8.0,
    },
    "transmission": {
        "rpm_speed_ratio_warning": 100,  # RPM/velocidad anómalo
    },
    "battery": {
        "temp_min": -10,
        "temp_max": 45,
    },
    "tires": {
        "pressure_min": 95,
        "pressure_max": 110,
        "vibration_warning": 6.0,
    },
}

# Pesos para cálculo de desgaste (0-1)
WEAR_WEIGHTS = {
    "engine": {
        "high_rpm_time": 0.4,
        "overheating_time": 0.4,
        "cold_starts": 0.2,
    },
    "brakes": {
        "hard_braking_count": 0.5,
        "high_vibration_time": 0.3,
        "high_speed_braking": 0.2,
    },
    "transmission": {
        "gear_stress": 0.4,
        "rpm_fluctuation": 0.3,
        "high_load_time": 0.3,
    },
    "tires": {
        "high_speed_time": 0.3,
        "pressure_anomaly_time": 0.4,
        "vibration_time": 0.3,
    },
}

# Intervalos de mantenimiento base (en horas de uso)
MAINTENANCE_INTERVALS = {
    "oil_change": 250,
    "brake_inspection": 500,
    "tire_rotation": 300,
    "coolant_check": 400,
    "transmission_service": 1000,
}

# Niveles de alerta
ALERT_LEVELS = {
    "info": 0,
    "warning": 1,
    "critical": 2,
    "emergency": 3,
}
