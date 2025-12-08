# Módulo MQTT Bridge

Módulo de mensajería MQTT para conectar el digital twin con clientes externos (apps móviles, dashboards, etc.).

## Arquitectura

```
can_twin → MQTT Bridge → MQTT Broker → Clientes (App Android, etc.)
```

## Topics MQTT

- `boomapp/vehicle/telemetry` - Datos completos del vehículo
- `boomapp/vehicle/obd` - Datos OBD-II (RPM, velocidad, temperatura, etc.)
- `boomapp/vehicle/sensors` - Datos de sensores (temperatura, presión, vibración)
- `boomapp/vehicle/commands` - Comandos desde clientes (pause, resume, stop)
- `boomapp/vehicle/status` - Estado general del sistema

## Instalación

Instalar dependencia MQTT:
```bash
pip install paho-mqtt
```

## Uso

### 1. Iniciar broker MQTT local (Mosquitto)

```bash
# Windows
mosquitto -v

# Linux/Mac
sudo systemctl start mosquitto
```

O usar un broker público: `test.mosquitto.org`, `broker.hivemq.com`

### 2. Ejecutar simulador con MQTT

```bash
python main.py
```

Selecciona un escenario y activa MQTT cuando se solicite.

### 3. Cliente de prueba

En otra terminal, ejecutar el cliente de prueba:

```bash
python mqtt_test_client.py
```

## Formato de mensajes

### OBD Data
```json
{
  "rpm": 2500,
  "speed": 80,
  "coolant_temp": 92,
  "throttle": 45,
  "fuel_level": 75
}
```

### Sensor Data
```json
{
  "temperature": 26.5,
  "pressure": 101.2,
  "humidity": 50.3,
  "vibration": 0.8
}
```

### Commands (publicar en `boomapp/vehicle/commands`)
```json
{"type": "pause"}
{"type": "resume"}
{"type": "stop"}
```

## Integración con App Android

La app Android debe:
1. Conectarse al broker MQTT
2. Suscribirse a `boomapp/vehicle/#`
3. Parsear mensajes JSON
4. Publicar comandos en `boomapp/vehicle/commands`
