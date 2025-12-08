# Configuración HiveMQ Cloud

## Paso 1: Obtener Credenciales de HiveMQ

En tu dashboard de HiveMQ Cloud, anota:
- **Host**: `xxxxx.s1.eu.hivemq.cloud` (o similar)
- **Port**: `8883`
- **Username**: El usuario que creaste
- **Password**: La contraseña que creaste

## Paso 2: Configurar Variables de Entorno en Railway

Ve a tu proyecto en Railway → Variables y añade:

```
MQTT_BROKER=tu-cluster.s1.eu.hivemq.cloud
MQTT_PORT=8883
MQTT_USERNAME=tu-usuario
MQTT_PASSWORD=tu-password
MQTT_USE_TLS=true
```

## Paso 3: Configurar Simulador Local

Crea un archivo `.env` en la raíz del proyecto:

```bash
# .env
MQTT_BROKER=tu-cluster.s1.eu.hivemq.cloud
MQTT_PORT=8883
MQTT_USERNAME=tu-usuario
MQTT_PASSWORD=tu-password
MQTT_USE_TLS=true
```

## Paso 4: Actualizar main.py para usar variables de entorno

El simulador necesita leer las credenciales. Ejecuta:

```bash
pip install python-dotenv
```

Luego ejecuta el simulador:

```bash
python main.py
# Cuando pregunte por el broker, pon: tu-cluster.s1.eu.hivemq.cloud
```

## Paso 5: Verificar Conexión

### Backend en Railway:
```bash
curl https://tu-app.railway.app/api/debug/mqtt
```

Deberías ver:
```json
{
  "broker": "tu-cluster.s1.eu.hivemq.cloud",
  "port": 8883,
  "connected": true
}
```

### Simulador Local:
Deberías ver:
```
Conectando a tu-cluster.s1.eu.hivemq.cloud:8883 (TLS) como tu-usuario...
✓ Conectado al broker MQTT: tu-cluster.s1.eu.hivemq.cloud:8883
```

## Troubleshooting

### Error: "SSL: CERTIFICATE_VERIFY_FAILED"
HiveMQ usa certificados válidos, pero si tienes problemas:
```python
# En mqtt_client.py, cambiar:
self.client.tls_set()
# Por:
import ssl
self.client.tls_set(cert_reqs=ssl.CERT_NONE)
```

### Error: "Not authorized"
- Verifica usuario y contraseña en HiveMQ dashboard
- Asegúrate de que las variables de entorno estén correctas

### No se conecta
- Verifica que el puerto sea 8883 (no 1883)
- Verifica que MQTT_USE_TLS=true esté configurado
- Prueba la conexión con MQTT Explorer: http://mqtt-explorer.com/

## Alternativa: Probar con MQTT Explorer

1. Descarga MQTT Explorer
2. Conecta con tus credenciales de HiveMQ
3. Suscríbete a `boomapp/vehicle/#`
4. Ejecuta el simulador
5. Deberías ver los mensajes llegando

Esto confirma que las credenciales funcionan.
