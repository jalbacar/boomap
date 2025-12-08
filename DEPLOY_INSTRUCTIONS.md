# Instrucciones de Despliegue

## Paso 1: Subir a GitHub

```bash
# Inicializar Git (si no lo has hecho)
git init

# Añadir todos los archivos
git add .

# Commit
git commit -m "Backend con MQTT configurado"

# Crear repo en GitHub y conectar
git remote add origin https://github.com/TU-USUARIO/boomapp.git
git branch -M main
git push -u origin main
```

## Paso 2: Configurar Railway

1. Ve a [railway.app](https://railway.app)
2. Click "New Project"
3. Selecciona "Deploy from GitHub repo"
4. Selecciona tu repositorio `boomapp`
5. Railway detectará el proyecto

## Paso 3: Configurar Root Directory

1. En el dashboard de Railway, click en tu servicio
2. Ve a "Settings"
3. En "Root Directory" pon: `backend-api`
4. Guarda

## Paso 4: Configurar Variables de Entorno

1. Ve a la pestaña "Variables"
2. Añade estas variables:

```
MQTT_BROKER=test.mosquitto.org
MQTT_PORT=1883
```

3. Railway redesplegará automáticamente

## Paso 5: Verificar Despliegue

Espera a que termine el despliegue (1-2 minutos).

Luego verifica:

```bash
# 1. Verificar que el API responde
curl https://tu-app.railway.app/

# 2. Verificar conexión MQTT
curl https://tu-app.railway.app/api/debug/mqtt

# Deberías ver:
# {
#   "broker": "test.mosquitto.org",
#   "port": 1883,
#   "connected": true,
#   "vehicle_state": {...}
# }
```

## Paso 6: Ejecutar Simulador

```bash
python main.py
# Escenario: 1
# MQTT: s
# Broker: test.mosquitto.org
```

## Paso 7: Verificar Datos

Espera 10-15 segundos y verifica:

```bash
curl https://tu-app.railway.app/api/vehicle/status
```

Deberías ver datos del vehículo.

## Troubleshooting

### Si "connected": false en /api/debug/mqtt

1. Verifica variables de entorno en Railway
2. Revisa logs: `railway logs`
3. Busca errores de conexión MQTT

### Si no llegan datos

1. Ejecuta `python quick_test.py` mientras el simulador corre
2. Si quick_test.py recibe mensajes pero Railway no:
   - Verifica que ambos usen el mismo broker
   - Verifica que los topics coincidan
3. Si quick_test.py NO recibe mensajes:
   - El simulador no está publicando
   - Verifica logs del simulador

### Ver logs de Railway

```bash
# Instalar CLI
npm install -g @railway/cli

# Login
railway login

# Ver logs
railway logs --follow
```

## Alternativa: Desplegar con Railway CLI

```bash
cd backend-api
railway login
railway init
railway variables set MQTT_BROKER=test.mosquitto.org
railway variables set MQTT_PORT=1883
railway up
```
