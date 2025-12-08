MQTT_CONFIG = {
    "broker": "localhost",
    "port": 1883,
    "keepalive": 60,
    "qos": 1,
    "topics": {
        "telemetry": "boomapp/vehicle/telemetry",
        "obd": "boomapp/vehicle/obd",
        "sensors": "boomapp/vehicle/sensors",
        "commands": "boomapp/vehicle/commands",
        "status": "boomapp/vehicle/status"
    }
}

# Brokers públicos para testing (opcional)
PUBLIC_BROKERS = {
    "mosquitto": {"broker": "test.mosquitto.org", "port": 1883},
    "hivemq": {"broker": "broker.hivemq.com", "port": 1883},
    "eclipse": {"broker": "mqtt.eclipseprojects.io", "port": 1883}
}
