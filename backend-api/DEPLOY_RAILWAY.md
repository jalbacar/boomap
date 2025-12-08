# Desplegar Backend en Railway

Guía para desplegar el backend API en Railway.app

## Opción 1: Desplegar desde GitHub (Recomendado)

### 1. Preparar el Repositorio

```bash
# Desde la raíz de BOOMApp
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/tu-usuario/boomapp.git
git push -u origin main
```

### 2. Crear Proyecto en Railway

1. Ir a [railway.app](https://railway.app)
2. Click en "New Project"
3. Seleccionar "Deploy from GitHub repo"
4. Seleccionar tu repositorio `boomapp`
5. Railway detectará automáticamente el backend

### 3. Configurar Variables de Entorno

En el dashboard de Railway, ir a "Variables" y añadir:

```
MQTT_BROKER=test.mosquitto.org
MQTT_PORT=1883
```

**Opciones de MQTT Broker:**

- **Broker público (testing):**
  - `test.mosquitto.org`
  - `broker.hivemq.com`
  - `mqtt.eclipseprojects.io`

- **Broker propio (producción):**
  - CloudMQTT (ahora CloudAMQP)
  - HiveMQ Cloud
  - AWS IoT Core
  - Azure IoT Hub

### 4. Configurar Root Directory

Si Railway no detecta automáticamente el backend:

1. Ir a "Settings"
2. En "Root Directory" poner: `backend-api`
3. Guardar cambios

### 5. Deploy

Railway desplegará automáticamente. Verás:
```
✓ Building...
✓ Deploying...
✓ Live at: https://tu-app.railway.app
```

## Opción 2: Desplegar con Railway CLI

### 1. Instalar Railway CLI

```bash
npm install -g @railway/cli
```

### 2. Login

```bash
railway login
```

### 3. Inicializar Proyecto

```bash
cd backend-api
railway init
```

### 4. Configurar Variables

```bash
railway variables set MQTT_BROKER=test.mosquitto.org
railway variables set MQTT_PORT=1883
```

### 5. Deploy

```bash
railway up
```

## Configuración del Digital Twin

Una vez desplegado, actualizar el simulador para conectarse al backend en Railway:

```python
# En main.py, cuando se solicite el broker:
# Usar: test.mosquitto.org (o el broker que configuraste)
```

## Probar el Despliegue

```bash
# Obtener la URL de Railway
railway domain

# Probar el API
curl https://tu-app.railway.app/api/vehicle/status

# Ver logs
railway logs
```

## Arquitectura en Producción

```
Digital Twin (Local/ESP32)
    ↓
MQTT Broker Público (test.mosquitto.org)
    ↓
Backend API (Railway)
    ↓
App Android/Web
```

## Consideraciones

### MQTT Broker Público
- ✅ Fácil de configurar
- ✅ Sin costo
- ⚠️ Sin autenticación
- ⚠️ No recomendado para producción

### MQTT Broker Privado (Recomendado para Producción)
- ✅ Seguro (TLS + autenticación)
- ✅ Escalable
- ✅ Monitoreo
- 💰 Costo mensual

### Opciones de Broker Privado

**HiveMQ Cloud (Recomendado):**
```
MQTT_BROKER=tu-cluster.hivemq.cloud
MQTT_PORT=8883
MQTT_USERNAME=tu-usuario
MQTT_PASSWORD=tu-password
```

**CloudAMQP:**
```
MQTT_BROKER=tu-instancia.cloudamqp.com
MQTT_PORT=1883
```

## Monitoreo

Ver logs en tiempo real:
```bash
railway logs --follow
```

Ver métricas:
- CPU, RAM, Network en el dashboard de Railway

## Troubleshooting

### Error: "Connection refused" al MQTT
- Verificar que `MQTT_BROKER` esté configurado correctamente
- Probar conexión: `mosquitto_sub -h test.mosquitto.org -t test`

### Error: "Port already in use"
- Railway asigna el puerto automáticamente vía `$PORT`
- No hardcodear el puerto en el código

### Backend no recibe datos
- Verificar que el digital twin use el mismo broker
- Verificar topics MQTT: `boomapp/vehicle/#`

## Costos

- **Railway:** $5/mes (plan Hobby) - 500 horas de ejecución
- **MQTT Broker público:** Gratis
- **HiveMQ Cloud:** Desde $0 (plan gratuito limitado)

## Próximos Pasos

1. Configurar dominio personalizado
2. Añadir autenticación JWT
3. Conectar base de datos (PostgreSQL en Railway)
4. Configurar CI/CD
5. Monitoreo con Sentry
