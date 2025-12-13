# Cerebro Predictivo - BoomApp

Módulo de mantenimiento predictivo que analiza datos de sensores vehiculares y predice el desgaste de componentes.

## Arquitectura

```
┌─────────────────┐
│  Digital Twin   │ publica datos
│   (Simulador)   │────────────┐
└─────────────────┘            │
                               ↓
                    ┌─────────────────┐
                    │   MQTT Broker   │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ↓                   ↓                   ↓
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Cerebro         │ │  Backend API    │ │  Otros          │
│ Predictivo      │ │  (FastAPI)      │ │  Suscriptores   │
└────────┬────────┘ └────────┬────────┘ └─────────────────┘
         │                   │
         │ publica           │ suscribe
         │ predicciones      │ predicciones
         ↓                   ↓
┌─────────────────┐ ┌─────────────────┐
│ MQTT Topics:    │ │  REST API +     │
│ predictions/*   │→│  WebSocket      │
└─────────────────┘ └────────┬────────┘
                             │
                             ↓
                    ┌─────────────────┐
                    │    Clientes     │
                    │  (Android/Web)  │
                    └─────────────────┘
```

## Componentes

### 1. WearAnalyzer (`wear_models.py`)
Analiza el desgaste de componentes basado en patrones de uso:
- **Motor**: RPM alto, sobrecalentamiento, arranques en frío
- **Frenos**: Frenados bruscos, vibración alta
- **Transmisión**: Estrés de marchas, fluctuación RPM
- **Neumáticos**: Presión anómala, velocidad alta
- **Batería**: Temperatura ambiente extrema

### 2. AlertManager (`alert_manager.py`)
Genera alertas basadas en umbrales:
- **INFO**: Información general
- **WARNING**: Atención requerida
- **CRITICAL**: Acción necesaria pronto
- **EMERGENCY**: Acción inmediata

### 3. PredictiveEngine (`predictor.py`)
Motor principal que:
- Se suscribe a topics MQTT de sensores
- Procesa datos en tiempo real
- Publica predicciones y alertas

## Topics MQTT

### Entrada (suscripción)
- `boomapp/vehicle/obd` - Datos OBD-II
- `boomapp/vehicle/sensors` - Datos de sensores

### Salida (publicación)
- `boomapp/predictions/wear` - Estado de desgaste
- `boomapp/predictions/alerts` - Alertas activas

## Instalación

```bash
# Desde la raíz del proyecto
pip install -e .
```

## Uso

### Ejecutar el Cerebro Predictivo

```bash
python run_predictive_brain.py
```

Seguir las instrucciones para configurar el broker MQTT.

### Uso Programático

```python
from boomapp.predictive_brain import PredictiveEngine

engine = PredictiveEngine(
    broker="localhost",  # o tu-cluster.hivemq.cloud
    port=1883,           # o 8883 para TLS
    username=None,       # usuario HiveMQ
    password=None,       # contraseña HiveMQ
    use_tls=False        # True para HiveMQ Cloud
)

# Callbacks opcionales
engine.on_prediction = lambda data: print(f"Predicción: {data}")
engine.on_alert = lambda alert: print(f"Alerta: {alert}")

# Conectar e iniciar
if engine.connect():
    # El motor procesa datos automáticamente
    # ...
    engine.disconnect()
```

## API REST (Backend)

### Nuevos Endpoints

| Endpoint | Descripción |
|----------|-------------|
| `GET /api/predictions/status` | Estado completo de predicciones |
| `GET /api/predictions/wear` | Estado de desgaste de componentes |
| `GET /api/predictions/alerts` | Alertas activas |
| `GET /api/predictions/component/{name}` | Desgaste de componente específico |

### Ejemplos

```bash
# Estado de predicciones
curl https://boomap-production.up.railway.app/api/predictions/status

# Alertas activas
curl https://boomap-production.up.railway.app/api/predictions/alerts

# Desgaste del motor
curl https://boomap-production.up.railway.app/api/predictions/component/engine
```

## WebSocket

El WebSocket ahora envía mensajes adicionales:

```json
{
  "type": "predictions",
  "data": {
    "wear_state": {...},
    "alert_summary": {...},
    "active_alerts": [...]
  }
}
```

```json
{
  "type": "alert",
  "data": {
    "id": "ALT-1234567890-0001",
    "level": "warning",
    "component": "engine",
    "message": "RPM elevado: 6800 RPM. Reducir revoluciones."
  }
}
```

## Estructura de Datos

### Estado de Desgaste

```json
{
  "components": {
    "engine": {
      "name": "engine",
      "wear_percentage": 15.5,
      "health_score": 84.5,
      "hours_until_maintenance": 235.5,
      "status": "good"
    },
    "brakes": {...},
    "transmission": {...},
    "tires": {...},
    "battery": {...}
  },
  "runtime_hours": 2.5,
  "overall_health": 87.3
}
```

### Alerta

```json
{
  "id": "ALT-1734130800-0001",
  "level": "warning",
  "component": "engine",
  "message": "Temperatura elevada: 102.5°C. Monitorear.",
  "timestamp": 1734130800.123,
  "data": {
    "coolant_temp": 102.5,
    "threshold": 100
  },
  "acknowledged": false
}
```

## Configuración de Umbrales

Editar `boomapp/predictive_brain/config.py`:

```python
THRESHOLDS = {
    "engine": {
        "rpm_max": 6500,
        "rpm_critical": 7000,
        "coolant_temp_warning": 100,
        "coolant_temp_critical": 110,
    },
    # ...
}
```

## Flujo Completo

1. **Iniciar MQTT Broker** (Mosquitto o HiveMQ)
2. **Iniciar Cerebro Predictivo**: `python run_predictive_brain.py`
3. **Iniciar Backend API**: `cd backend-api && uvicorn app.main:app`
4. **Iniciar Simulador**: `python main.py`
5. **Consumir datos**:
   - REST: `/api/predictions/status`
   - WebSocket: `ws://host/ws/vehicle`

## Pronósticos Futuros (FuturePredictor)

El sistema ahora incluye **predicciones a futuro** que analizan tendencias y pronostican problemas potenciales.

### Tipos de Predicciones

| Componente | Problemas Detectados |
|------------|---------------------|
| **Motor** | Sobrecalentamiento, desgaste excesivo por RPM alto |
| **Frenos** | Desgaste por vibración, frenados bruscos frecuentes |
| **Transmisión** | Estrés de marchas, conducción agresiva |
| **Neumáticos** | Pérdida de presión, desgaste por velocidad alta |
| **Batería** | Degradación por temperatura extrema |

### Niveles de Riesgo

- **LOW**: Sin acción inmediata requerida
- **MODERATE**: Monitorear y planificar revisión
- **HIGH**: Programar servicio pronto
- **CRITICAL**: Acción inmediata necesaria

### Datos de Pronóstico

```json
{
  "component": "engine",
  "current_health": 85.5,
  "forecast": {
    "health_in_1h": 85.3,
    "health_in_24h": 82.1,
    "health_in_7d": 70.5
  },
  "estimated_remaining_life_hours": 450.5,
  "trend": "degrading",
  "risk_factors": ["Uso frecuente en RPM alto"],
  "predictions": [
    {
      "problem_type": "excessive_wear",
      "risk_level": "moderate",
      "estimated_time_to_failure_hours": 350,
      "description": "Uso frecuente en RPM elevado...",
      "recommendation": "Reducir revoluciones durante la conducción..."
    }
  ]
}
```

### Nuevos Endpoints API

| Endpoint | Descripción |
|----------|-------------|
| `GET /api/forecasts/status` | Estado completo de pronósticos |
| `GET /api/forecasts/predictions` | Todas las predicciones futuras |
| `GET /api/forecasts/component/{name}` | Pronóstico de componente específico |
| `GET /api/forecasts/high-risk` | Solo predicciones de alto riesgo |
| `GET /api/forecasts/recommendations` | Recomendaciones de mantenimiento |

### WebSocket

Nuevos tipos de mensajes:

```json
{
  "type": "forecast",
  "data": {
    "component_forecasts": {...},
    "all_predictions": [...],
    "summary": {...}
  }
}
```

## Próximos Pasos

- [ ] Modelos ML para predicción avanzada
- [ ] Histórico de alertas en base de datos
- [ ] Notificaciones push a móviles
- [ ] Dashboard de mantenimiento
- [ ] Integración con talleres/servicios
