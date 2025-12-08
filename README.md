# BoomApp - Monorepo

Sistema completo de gemelo digital vehicular con arquitectura IoT.

## Estructura del Monorepo

```
BOOMApp/
├── boomapp/              # Paquete Python principal
│   ├── can_twin/         # Módulo Digital Twin (ESP32 + CAN + OBD)
│   └── mqtt_bridge/      # Módulo MQTT Bridge
├── backend-api/          # Backend API REST + WebSocket
├── data/                 # Escenarios CSV de simulación
└── main.py              # Simulador principal
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
- Mosquitto MQTT Broker

### Instalar Mosquitto

**Windows:**
```bash
# Descargar desde: https://mosquitto.org/download/
# O con chocolatey:
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

### Paso 1: Iniciar MQTT Broker

Abrir una terminal y ejecutar:

```bash
mosquitto -v
```

Deberías ver:
```
1234567890: mosquitto version 2.x starting
1234567890: Opening ipv4 listen socket on port 1883.
```

### Paso 2: Iniciar Backend API

Abrir una **segunda terminal** y ejecutar:

```bash
cd backend-api
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Deberías ver:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
✓ Backend conectado al MQTT Broker: localhost:1883
✓ Backend API iniciado
```

### Paso 3: Iniciar Digital Twin (Simulador)

Abrir una **tercera terminal** y ejecutar:

```bash
python main.py
```

Seguir las instrucciones:
1. Seleccionar un escenario (1-6)
2. Activar MQTT cuando pregunte (s)
3. Usar broker: `localhost`

Deberías ver:
```
✓ Conectado al broker MQTT: localhost:1883
Starting ESP32 Digital Twin...
=== Simulación iniciada ===
```

### Paso 4: Probar el Sistema

#### Opción A: API REST

Abrir navegador o usar curl:

```bash
# Estado completo del vehículo
curl http://localhost:8000/api/vehicle/status

# Solo datos OBD
curl http://localhost:8000/api/vehicle/obd

# Solo sensores
curl http://localhost:8000/api/vehicle/sensors

# Documentación interactiva
# Abrir en navegador: http://localhost:8000/docs
```

#### Opción B: WebSocket (Tiempo Real)

Abrir en navegador:
```
backend-api/test_websocket.html
```

Click en "Conectar" y verás los datos actualizándose en tiempo real.

#### Opción C: Cliente MQTT de Prueba

Abrir una **cuarta terminal**:

```bash
python mqtt_test_client.py
```

Verás todos los mensajes MQTT publicados por el digital twin.

#### Opción D: Test Automatizado REST

```bash
cd backend-api
python test_api.py
```

## Resumen de Terminales

```
Terminal 1: mosquitto -v
Terminal 2: cd backend-api && uvicorn app.main:app --reload
Terminal 3: python main.py
Terminal 4: python mqtt_test_client.py  (opcional)
```

## Verificación

Si todo funciona correctamente:

✅ Terminal 1: Mosquitto muestra conexiones de clientes  
✅ Terminal 2: Backend muestra "✓ Suscrito a topics del vehículo"  
✅ Terminal 3: Simulador muestra datos del vehículo cada 2 segundos  
✅ Terminal 4: Cliente MQTT muestra mensajes entrantes  
✅ Navegador: API REST devuelve datos JSON  
✅ Navegador: WebSocket muestra datos en tiempo real

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

### 🌐 backend-api
API REST + WebSocket:
- Endpoints REST para consultas
- WebSocket para streaming en tiempo real
- Suscriptor MQTT
- CORS habilitado

## Escenarios de Simulación

1. **normal.csv** - Uso normal y correcto
2. **extreme.csv** - Uso extremo
3. **stressed.csv** - Uso tensionado
4. **limit.csv** - Al límite
5. **faulty.csv** - Problemas en componentes
6. **overheating.csv** - Sobrecalentamiento

## Troubleshooting

### Error: "Connection refused" en MQTT
- Verificar que Mosquitto esté corriendo: `mosquitto -v`
- Verificar puerto 1883 disponible: `netstat -an | findstr 1883`

### Error: "Address already in use" en Backend
- Puerto 8000 ocupado, usar otro: `uvicorn app.main:app --port 8001`

### No llegan datos al Backend
- Verificar que el simulador tenga MQTT activado
- Verificar que todos usen el mismo broker (localhost)

## Próximos Pasos

- [ ] App Android
- [ ] Backend IA (PaaS)
- [ ] Base de datos para histórico
- [ ] Autenticación JWT
- [ ] Dashboard Web

## Documentación

- [MQTT Bridge](README_MQTT.md)
- [Backend API](backend-api/README.md)
