# Guía de Uso del API - BoomApp

Documentación completa para consumir el API REST y WebSocket del backend desplegado en Railway.

## 🌐 URL Base

```
https://boomap-production.up.railway.app
```

---

## 📡 API REST

### 1. Información del API

**Endpoint:** `GET /`

**Descripción:** Información básica del API

**Ejemplo:**
```bash
curl https://boomap-production.up.railway.app/
```

**Respuesta:**
```json
{
  "message": "BoomApp Backend API",
  "version": "1.0.0"
}
```

---

### 2. Debug MQTT

**Endpoint:** `GET /api/debug/mqtt`

**Descripción:** Verifica el estado de conexión con el broker MQTT

**Ejemplo:**
```bash
curl https://boomap-production.up.railway.app/api/debug/mqtt
```

**Respuesta:**
```json
{
  "broker": "d9c7356a58394727a868b97158e7abb5.s1.eu.hivemq.cloud",
  "port": 8883,
  "connected": true,
  "vehicle_state": {
    "obd": {...},
    "sensors": {...},
    "last_update": "2024-01-15T10:30:45"
  }
}
```

---

### 3. Estado Completo del Vehículo

**Endpoint:** `GET /api/vehicle/status`

**Descripción:** Obtiene todos los datos del vehículo (OBD + Sensores)

**Ejemplo:**
```bash
curl https://boomap-production.up.railway.app/api/vehicle/status
```

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

---

### 4. Datos OBD-II

**Endpoint:** `GET /api/vehicle/obd`

**Descripción:** Solo datos del sistema OBD-II del vehículo

**Ejemplo:**
```bash
curl https://boomap-production.up.railway.app/api/vehicle/obd
```

**Respuesta:**
```json
{
  "rpm": 2500,
  "speed": 80,
  "coolant_temp": 92,
  "throttle": 45,
  "fuel_level": 75
}
```

**Campos:**
- `rpm`: Revoluciones por minuto del motor
- `speed`: Velocidad del vehículo (km/h)
- `coolant_temp`: Temperatura del refrigerante (°C)
- `throttle`: Posición del acelerador (%)
- `fuel_level`: Nivel de combustible (%)

---

### 5. Datos de Sensores

**Endpoint:** `GET /api/vehicle/sensors`

**Descripción:** Solo datos de sensores ambientales

**Ejemplo:**
```bash
curl https://boomap-production.up.railway.app/api/vehicle/sensors
```

**Respuesta:**
```json
{
  "temperature": 26.5,
  "pressure": 101.2,
  "humidity": 50.3,
  "vibration": 0.8
}
```

**Campos:**
- `temperature`: Temperatura ambiente (°C)
- `pressure`: Presión atmosférica (kPa)
- `humidity`: Humedad relativa (%)
- `vibration`: Nivel de vibración (0-10)

---

### 6. Documentación Interactiva

**Swagger UI:** `https://boomap-production.up.railway.app/docs`

**ReDoc:** `https://boomap-production.up.railway.app/redoc`

---

## 🔌 WebSocket

### Conexión

**URL:** `wss://boomap-production.up.railway.app/ws/vehicle`

**Protocolo:** WebSocket Secure (WSS)

### Tipos de Mensajes

El servidor envía mensajes en formato JSON con la siguiente estructura:

```json
{
  "type": "tipo_de_mensaje",
  "data": {...}
}
```

#### Mensaje Inicial

Al conectarse, el servidor envía el estado actual:

```json
{
  "type": "initial",
  "data": {
    "obd": {...},
    "sensors": {...},
    "last_update": "2024-01-15T10:30:45"
  }
}
```

#### Actualización OBD

Cada vez que llegan datos OBD del vehículo:

```json
{
  "type": "obd",
  "data": {
    "rpm": 2500,
    "speed": 80,
    "coolant_temp": 92,
    "throttle": 45,
    "fuel_level": 75
  }
}
```

#### Actualización Sensores

Cada vez que llegan datos de sensores:

```json
{
  "type": "sensors",
  "data": {
    "temperature": 26.5,
    "pressure": 101.2,
    "humidity": 50.3,
    "vibration": 0.8
  }
}
```

---

## 💻 Ejemplos de Código

### Python - REST API

```python
import requests

BASE_URL = "https://boomap-production.up.railway.app"

# Obtener estado del vehículo
response = requests.get(f"{BASE_URL}/api/vehicle/status")
data = response.json()

print(f"RPM: {data['obd']['rpm']}")
print(f"Velocidad: {data['obd']['speed']} km/h")
print(f"Temperatura: {data['sensors']['temperature']}°C")
```

### Python - WebSocket (Simple)

```python
import websocket
import json

def on_message(ws, message):
    data = json.loads(message)
    print(f"[{data['type']}]", data['data'])

ws = websocket.WebSocketApp(
    "wss://boomap-production.up.railway.app/ws/vehicle",
    on_message=on_message
)

ws.run_forever()
```

**Instalar:** `pip install websocket-client`

**Ejecutar:** `python test_websocket_simple.py`

### Python - WebSocket (Async)

```python
import asyncio
import websockets
import json

async def connect():
    uri = "wss://boomap-production.up.railway.app/ws/vehicle"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"[{data['type']}]", data['data'])

asyncio.run(connect())
```

**Instalar:** `pip install websockets`

**Ejecutar:** `python test_websocket_client.py`

### JavaScript - REST API

```javascript
// Fetch API
fetch('https://boomap-production.up.railway.app/api/vehicle/status')
  .then(response => response.json())
  .then(data => {
    console.log('RPM:', data.obd.rpm);
    console.log('Velocidad:', data.obd.speed);
  });

// Axios
const axios = require('axios');

axios.get('https://boomap-production.up.railway.app/api/vehicle/status')
  .then(response => {
    console.log(response.data);
  });
```

### JavaScript - WebSocket

```javascript
const ws = new WebSocket('wss://boomap-production.up.railway.app/ws/vehicle');

ws.onopen = () => {
  console.log('✓ Conectado');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(`[${data.type}]`, data.data);
  
  if (data.type === 'obd') {
    console.log('RPM:', data.data.rpm);
    console.log('Velocidad:', data.data.speed);
  }
};

ws.onerror = (error) => {
  console.error('Error:', error);
};

ws.onclose = () => {
  console.log('✗ Desconectado');
};
```

### Kotlin (Android) - REST API

```kotlin
// Retrofit
interface VehicleApi {
    @GET("/api/vehicle/status")
    suspend fun getVehicleStatus(): VehicleStatus
}

val retrofit = Retrofit.Builder()
    .baseUrl("https://boomap-production.up.railway.app/")
    .addConverterFactory(GsonConverterFactory.create())
    .build()

val api = retrofit.create(VehicleApi::class.java)

// Uso
lifecycleScope.launch {
    val status = api.getVehicleStatus()
    println("RPM: ${status.obd.rpm}")
}
```

### Kotlin (Android) - WebSocket

```kotlin
// OkHttp WebSocket
val client = OkHttpClient()

val request = Request.Builder()
    .url("wss://boomap-production.up.railway.app/ws/vehicle")
    .build()

val listener = object : WebSocketListener() {
    override fun onOpen(webSocket: WebSocket, response: Response) {
        println("✓ Conectado")
    }
    
    override fun onMessage(webSocket: WebSocket, text: String) {
        val data = JSONObject(text)
        val type = data.getString("type")
        val payload = data.getJSONObject("data")
        
        when (type) {
            "obd" -> {
                val rpm = payload.getDouble("rpm")
                val speed = payload.getDouble("speed")
                println("RPM: $rpm, Velocidad: $speed")
            }
            "sensors" -> {
                val temp = payload.getDouble("temperature")
                println("Temperatura: $temp°C")
            }
        }
    }
    
    override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
        println("✗ Error: ${t.message}")
    }
}

val ws = client.newWebSocket(request, listener)
```

---

## 🧪 Scripts de Prueba

### Bash - Probar todos los endpoints

```bash
#!/bin/bash
BASE_URL="https://boomap-production.up.railway.app"

echo "1. Info API:"
curl $BASE_URL/

echo -e "\n2. Debug MQTT:"
curl $BASE_URL/api/debug/mqtt

echo -e "\n3. Vehicle Status:"
curl $BASE_URL/api/vehicle/status

echo -e "\n4. OBD Data:"
curl $BASE_URL/api/vehicle/obd

echo -e "\n5. Sensor Data:"
curl $BASE_URL/api/vehicle/sensors
```

**Ejecutar:** `bash test_all_endpoints.sh`

### Python - Probar WebSocket

```bash
# Instalar dependencias
pip install websocket-client

# Ejecutar cliente
python test_websocket_simple.py
```

---

## 📊 Frecuencia de Actualización

- **OBD Data**: Cada ~0.5 segundos
- **Sensor Data**: Cada ~0.1 segundos
- **WebSocket**: Tiempo real (push inmediato)
- **REST API**: Bajo demanda (pull)

---

## ⚠️ Notas Importantes

1. **CORS**: El API tiene CORS habilitado para todos los orígenes (`*`)
2. **Autenticación**: Actualmente no requiere autenticación (añadir JWT en producción)
3. **Rate Limiting**: No implementado (considerar para producción)
4. **HTTPS**: Todas las conexiones deben usar HTTPS/WSS
5. **Datos en Tiempo Real**: Para obtener datos, el simulador debe estar corriendo y publicando a HiveMQ

---

## 🔍 Troubleshooting

### No hay datos (status: "offline")

**Causa:** El simulador no está corriendo o no está publicando a HiveMQ

**Solución:**
```bash
# Ejecutar simulador
python main.py
# Configurar con HiveMQ Cloud
```

### WebSocket se desconecta

**Causa:** Timeout de inactividad o error de red

**Solución:** Implementar reconexión automática en el cliente

### Error CORS en navegador

**Causa:** Petición desde origen no permitido

**Solución:** El backend ya tiene CORS habilitado, verificar que uses HTTPS

---

## 📚 Recursos Adicionales

- **Swagger UI**: https://boomap-production.up.railway.app/docs
- **ReDoc**: https://boomap-production.up.railway.app/redoc
- **Repositorio**: https://github.com/tu-usuario/boomapp
- **HiveMQ Dashboard**: https://console.hivemq.cloud/

---

## 🚀 Próximos Pasos

1. Implementar autenticación JWT
2. Añadir endpoints para histórico de datos
3. Implementar rate limiting
4. Añadir webhooks para notificaciones
5. Crear SDK para Android/iOS
