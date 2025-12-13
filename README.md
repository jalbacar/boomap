# BoomApp - Monorepo

Sistema completo de gemelo digital vehicular con arquitectura IoT.

## Estructura del Monorepo

```
BOOMApp/
├── boomapp/              # Paquete Python principal
│   ├── can_twin/         # Módulo Digital Twin (ESP32 + CAN + OBD)
│   ├── mqtt_bridge/      # Módulo MQTT Bridge
│   └── predictive_brain/ # Módulo Cerebro Predictivo (IA)
├── backend-api/          # Backend API REST + WebSocket
├── data/                 # Escenarios CSV de simulación
├── main.py               # Simulador principal
└── run_predictive_brain.py  # Ejecutar cerebro predictivo
```

## Arquitectura Completa

```
┌─────────────────┐
│  Digital Twin   │ (can_twin)
│   ESP32 + CAN   │
└────────┬────────┘
         │ publica
         ↓
┌─────────────────┐
│  MQTT Broker    │ (Mosquitto)
└────────┬────────┘
         │ suscribe
         ↓
┌─────────────────┐
│  Backend API    │ (FastAPI)
│  REST + WS      │
└────────┬────────┘
         │ consume
         ↓
┌─────────────────┐
│    Clientes     │
│ App Android/Web │
└─────────────────┘
```

## Instalación

```bash
# Instalar paquete principal
pip install -e .

# Instalar backend API
cd backend-api
pip install -r requirements.txt
```

## Instalación Completa

### Requisitos Previos
- Python 3.7+
- MQTT Broker (Mosquitto local o HiveMQ Cloud)

### Opción A: Mosquitto Local (Desarrollo)

**Windows:**
```bash
choco install mosquitto
```

**Linux:**
```bash
sudo apt-get install mosquitto mosquitto-clients
```

**macOS:**
```bash
brew install mosquitto
```

### Opción B: HiveMQ Cloud (Producción)

1. Crear cuenta en https://console.hivemq.cloud/
2. Crear cluster gratuito
3. Anotar credenciales:
   - Host: `xxxxx.s1.eu.hivemq.cloud`
   - Port: `8883`
   - Usuario y contraseña

### Instalar Dependencias Python

```bash
# Paquete principal (can_twin + mqtt_bridge)
pip install -e .

# Backend API
cd backend-api
pip install -r requirements.txt
cd ..
```

## Uso Paso a Paso

### Paso 1: Configurar MQTT Broker

**Opción A: Mosquitto Local**

Abrir una terminal y ejecutar:

```bash
mosquitto -v
```

Deberías ver:
```
1234567890: mosquitto version 2.x starting
1234567890: Opening ipv4 listen socket on port 1883.
```

**Opción B: HiveMQ Cloud**

Configurar variables de entorno en Railway (ver Paso 2)

### Paso 2: Configurar Backend en Railway

1. Subir código a GitHub
2. Conectar Railway con el repositorio
3. Configurar Root Directory: `backend-api`
4. Configurar Variables de Entorno:

**Para HiveMQ Cloud:**
```
MQTT_BROKER=tu-cluster.s1.eu.hivemq.cloud
MQTT_PORT=8883
MQTT_USERNAME=tu-usuario
MQTT_PASSWORD=tu-password
MQTT_USE_TLS=true
```

**Para Mosquitto Local (testing):**
```
MQTT_BROKER=localhost
MQTT_PORT=1883
```

5. Railway desplegará automáticamente
6. Obtener URL: `https://tu-app.railway.app`

### Paso 3: Iniciar Digital Twin (Simulador)

Ejecutar:

```bash
python main.py
```

Seguir las instrucciones:
1. Seleccionar un escenario (1-6)
2. Activar MQTT (s)
3. Configurar broker:

**Para HiveMQ Cloud:**
```
Broker: tu-cluster.s1.eu.hivemq.cloud
TLS: s
Usuario: tu-usuario
Contraseña: ****
```

**Para Mosquitto Local:**
```
Broker: localhost
```

Deberías ver:
```
✓ Conectado al broker MQTT: tu-broker:8883 (TLS) como tu-usuario
Starting ESP32 Digital Twin...
=== Simulación iniciada ===
→ OBD publicado: 0 | RPM: 2500
→ Sensores publicados: 0 | Temp: 26.5
```

### Paso 4: Probar el Sistema

#### Opción A: API REST (Railway)

```bash
# Verificar conexión MQTT
curl https://tu-app.railway.app/api/debug/mqtt

# Estado completo del vehículo
curl https://tu-app.railway.app/api/vehicle/status

# Solo datos OBD
curl https://tu-app.railway.app/api/vehicle/obd

# Solo sensores
curl https://tu-app.railway.app/api/vehicle/sensors

# Documentación interactiva
# Abrir en navegador: https://tu-app.railway.app/docs
```

#### Opción B: WebSocket (Tiempo Real)

Editar `backend-api/test_websocket.html` y cambiar:
```javascript
ws = new WebSocket('wss://tu-app.railway.app/ws/vehicle');
```

Abrir en navegador y click en "Conectar".

#### Opción C: Cliente MQTT de Prueba

```bash
python mqtt_test_client.py
# Broker: tu-cluster.s1.eu.hivemq.cloud
```

## Resumen de Componentes

```
1. MQTT Broker: HiveMQ Cloud (o Mosquitto local)
2. Backend API: Railway (https://tu-app.railway.app)
3. Simulador: Local (python main.py)
4. Cliente Test: python mqtt_test_client.py (opcional)
```

## Verificación

Si todo funciona correctamente:

✅ HiveMQ Dashboard: Muestra clientes conectados  
✅ Railway Logs: "✓ Backend conectado al MQTT Broker"  
✅ Simulador: "→ OBD publicado: 0 | RPM: 2500"  
✅ `/api/debug/mqtt`: `"connected": true`  
✅ `/api/vehicle/status`: Devuelve datos del vehículo  
✅ WebSocket: Muestra datos en tiempo real

## Módulos

### 🚗 can_twin
Gemelo digital del ESP32 con simulación de:
- Bus CAN
- Protocolo OBD-II
- Sensores (temperatura, presión, vibración)

### 📡 mqtt_bridge
Puente MQTT para comunicación IoT:
- Publicación de telemetría
- Recepción de comandos
- Topics organizados

### 🧠 predictive_brain
Cerebro de mantenimiento predictivo:
- Análisis de desgaste de componentes
- Predicciones de problemas futuros
- Alertas multinivel (info, warning, critical, emergency)
- Estimación de costes de reparación (€)

### 🌐 backend-api
API REST + WebSocket:
- Endpoints REST para consultas
- WebSocket para streaming en tiempo real
- Suscriptor MQTT
- Endpoints de predicciones y costes
- CORS habilitado

## Escenarios de Simulación

1. **normal.csv** - Uso normal y correcto
2. **extreme.csv** - Uso extremo
3. **stressed.csv** - Uso tensionado
4. **limit.csv** - Al límite
5. **faulty.csv** - Problemas en componentes
6. **overheating.csv** - Sobrecalentamiento

## Troubleshooting

### Error: "Connection refused" o Timeout en MQTT

**Verificar que Mosquitto esté corriendo:**
```bash
mosquitto -v
```

**Verificar puerto 1883:**
```bash
# Windows
netstat -an | findstr 1883

# Linux/Mac
netstat -an | grep 1883
```

**Probar conexión:**
```bash
# Windows (instalar telnet primero)
telnet localhost 1883

# Linux/Mac
telnet localhost 1883
```

**Si el firewall bloquea:**
- Windows: Permitir puerto 1883 en Windows Defender
- Antivirus: Añadir excepción para Mosquitto

### Error: "Address already in use" en Backend
- Puerto 8000 ocupado, usar otro: `uvicorn app.main:app --port 8001`

### No llegan datos al Backend
- Verificar que el simulador tenga MQTT activado
- Verificar que todos usen el mismo broker (localhost)

## Próximos Pasos

- [x] ~~Backend IA (PaaS)~~ → Implementado como `predictive_brain`
- [ ] App Android
- [ ] Base de datos para histórico
- [ ] Autenticación JWT
- [ ] Dashboard Web
- [ ] Notificaciones push

## Documentación

- [Uso del API REST y WebSocket](API_USAGE.md) ⭐ **Nuevo**
- [Cerebro Predictivo](README_PREDICTIVE.md) 🧠 **Nuevo**
- [MQTT Bridge](README_MQTT.md)
- [Backend API](backend-api/README.md)
- [Configuración HiveMQ](HIVEMQ_SETUP.md)
- [Despliegue en Railway](backend-api/DEPLOY_RAILWAY.md)
- [Troubleshooting](TROUBLESHOOTING.md)
