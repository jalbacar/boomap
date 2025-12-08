# BoomApp Backend API

Backend API REST + WebSocket que consume datos del MQTT Broker y los expone a clientes (apps móviles, web, etc.).

## Arquitectura

```
Digital Twin → MQTT Broker → Backend API → Clientes
                                ↓
                        REST + WebSocket
```

## Instalación

```bash
cd backend-api
pip install -r requirements.txt
```

## Ejecución

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints REST

### GET /
Información del API

### GET /api/vehicle/status
Estado completo del vehículo (OBD + Sensores)

**Respuesta:**
```json
{
  "obd": {
    "rpm": 2500,
    "speed": 80,
    "coolant_temp": 92,
    "throttle": 45,
    "fuel_level": 75
  },
  "sensors": {
    "temperature": 26.5,
    "pressure": 101.2,
    "humidity": 50.3,
    "vibration": 0.8
  },
  "last_update": "2024-01-15T10:30:45",
  "status": "online"
}
```

### GET /api/vehicle/obd
Solo datos OBD-II

### GET /api/vehicle/sensors
Solo datos de sensores

## WebSocket

### WS /ws/vehicle
Streaming en tiempo real de datos del vehículo

**Conexión:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/vehicle');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};
```

**Mensajes recibidos:**
```json
{
  "type": "obd",
  "data": { "rpm": 2500, ... }
}
```

```json
{
  "type": "sensors",
  "data": { "temperature": 26.5, ... }
}
```

## Flujo completo

1. **Iniciar MQTT Broker:**
   ```bash
   mosquitto -v
   ```

2. **Iniciar Backend API:**
   ```bash
   cd backend-api
   uvicorn app.main:app --reload
   ```

3. **Iniciar Digital Twin:**
   ```bash
   cd ..
   python main.py
   ```

4. **Probar API:**
   - REST: http://localhost:8000/api/vehicle/status
   - Docs: http://localhost:8000/docs
   - WebSocket: ws://localhost:8000/ws/vehicle

## Despliegue en Railway

Ver guía completa: [DEPLOY_RAILWAY.md](DEPLOY_RAILWAY.md)

**Resumen rápido:**

1. Push a GitHub
2. Conectar Railway con el repo
3. Configurar variables:
   ```
   MQTT_BROKER=test.mosquitto.org
   MQTT_PORT=1883
   ```
4. Deploy automático

## Integración con App Android

```kotlin
// REST API
val retrofit = Retrofit.Builder()
    .baseUrl("https://tu-app.railway.app/")
    .build()

// WebSocket
val client = OkHttpClient()
val request = Request.Builder()
    .url("wss://tu-app.railway.app/ws/vehicle")
    .build()
val ws = client.newWebSocket(request, listener)
```
