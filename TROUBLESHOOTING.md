# Troubleshooting - BoomApp

## Problema: Backend en Railway no recibe datos del simulador

### Síntoma
```json
{
  "obd": {},
  "sensors": {},
  "last_update": null,
  "status": "offline"
}
```

### Causas y Soluciones

#### 1. Variables de entorno no configuradas en Railway

**Verificar:**
```bash
# En Railway dashboard → Variables
MQTT_BROKER=test.mosquitto.org
MQTT_PORT=1883
```

**Solución:**
1. Ir a tu proyecto en Railway
2. Click en "Variables"
3. Añadir:
   - `MQTT_BROKER` = `test.mosquitto.org`
   - `MQTT_PORT` = `1883`
4. Redeploy (automático)

#### 2. Verificar que el backend está conectado al broker

**Probar endpoint de debug:**
```bash
curl https://tu-app.railway.app/api/debug/mqtt
```

**Respuesta esperada:**
```json
{
  "broker": "test.mosquitto.org",
  "port": 1883,
  "connected": true,
  "vehicle_state": {...}
}
```

Si `connected: false`, el backend no puede conectarse al broker.

#### 3. Verificar que el simulador está publicando

**Ejecutar script de prueba:**
```bash
# Terminal 1: Ejecutar simulador
python main.py
# Seleccionar escenario
# Broker: test.mosquitto.org

# Terminal 2: Verificar mensajes
python test_mqtt_connection.py
# Broker: test.mosquitto.org
```

Deberías ver mensajes como:
```
[boomapp/vehicle/obd]
Payload: {"rpm": 2500, "speed": 80, ...}

[boomapp/vehicle/sensors]
Payload: {"temperature": 26.5, ...}
```

Si NO ves mensajes, el simulador no está publicando correctamente.

#### 4. Verificar topics MQTT

**El simulador publica en:**
- `boomapp/vehicle/obd`
- `boomapp/vehicle/sensors`
- `boomapp/vehicle/telemetry`

**El backend se suscribe a:**
- `boomapp/vehicle/obd`
- `boomapp/vehicle/sensors`

Deben coincidir exactamente.

#### 5. Broker público puede tener latencia

Los brokers públicos como `test.mosquitto.org` pueden tener:
- Latencia alta
- Mensajes perdidos
- Desconexiones temporales

**Solución:**
Probar con otro broker público:
```
broker.hivemq.com
mqtt.eclipseprojects.io
```

#### 6. Firewall o red corporativa

Si estás en una red corporativa, puede bloquear el puerto 1883.

**Verificar:**
```bash
telnet test.mosquitto.org 1883
```

Si no conecta, tu red bloquea MQTT.

**Solución:**
- Usar VPN
- Usar broker con puerto 80/443
- Usar broker con WebSocket

### Flujo de Verificación Completo

```bash
# 1. Verificar broker MQTT está accesible
telnet test.mosquitto.org 1883

# 2. Ejecutar test de conexión
python test_mqtt_connection.py

# 3. En otra terminal, ejecutar simulador
python main.py
# Broker: test.mosquitto.org

# 4. Verificar que test_mqtt_connection.py recibe mensajes

# 5. Verificar backend en Railway
curl https://tu-app.railway.app/api/debug/mqtt

# 6. Si connected=true pero no hay datos, esperar 30 segundos
# Los datos se actualizan cada 0.5s desde el simulador

# 7. Verificar endpoint de status
curl https://tu-app.railway.app/api/vehicle/status
```

### Logs en Railway

Ver logs del backend:
```bash
railway logs --follow
```

Buscar:
```
✓ Backend conectado al MQTT Broker: test.mosquitto.org:1883
✓ Suscrito a topics del vehículo
```

Si ves errores de conexión, verificar variables de entorno.

### Solución Rápida

Si nada funciona, usar broker local con túnel:

```bash
# 1. Instalar ngrok
# 2. Exponer Mosquitto local
ngrok tcp 1883

# 3. Usar URL de ngrok en Railway
MQTT_BROKER=0.tcp.ngrok.io
MQTT_PORT=12345  # Puerto que te da ngrok

# 4. Simulador también usa ngrok
Broker: 0.tcp.ngrok.io:12345
```

### Alternativa: Broker MQTT en Railway

Desplegar tu propio broker MQTT en Railway:

```bash
# Crear nuevo servicio en Railway
# Usar imagen Docker: eclipse-mosquitto
# Exponer puerto 1883
```

Luego configurar:
```
MQTT_BROKER=tu-mosquitto.railway.app
MQTT_PORT=1883
```

### Verificación Final

Si todo está bien configurado:

✅ `test_mqtt_connection.py` recibe mensajes del simulador  
✅ `/api/debug/mqtt` muestra `connected: true`  
✅ `/api/vehicle/status` muestra datos después de 30 segundos  
✅ Logs de Railway muestran "Suscrito a topics del vehículo"

### Contacto

Si el problema persiste, verificar:
1. Versión de paho-mqtt: `pip show paho-mqtt`
2. Logs completos de Railway
3. Captura de pantalla de variables de entorno en Railway
