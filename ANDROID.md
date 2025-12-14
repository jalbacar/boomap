# 📱 App Android BOOMApp

Guía para desarrollar la aplicación Android de mantenimiento predictivo de vehículos.

## Arquitectura General

```
┌─────────────────────────────────────────────────────────┐
│                    APP ANDROID                          │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │  Dashboard  │  │   Alertas   │  │    Costes       │  │
│  │  Principal  │  │   y Avisos  │  │   Reparación    │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
├─────────────────────────────────────────────────────────┤
│                 CAPA DE DATOS                           │
│  ┌─────────────────────┐  ┌─────────────────────────┐   │
│  │  REST API Client    │  │  MQTT Client (Paho)     │   │
│  │  (Retrofit)         │  │  (Tiempo real)          │   │
│  └─────────────────────┘  └─────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
              │                        │
              ▼                        ▼
     ┌─────────────────┐      ┌─────────────────┐
     │  Backend API    │      │   HiveMQ Cloud  │
     │  (Railway)      │      │   (MQTT Broker) │
     └─────────────────┘      └─────────────────┘
```

---

## 🎯 Funcionalidades Principales

### 1. Dashboard en Tiempo Real
- RPM, velocidad, temperatura motor
- Indicadores visuales (gauges)
- Estado de salud general del vehículo (%)

### 2. Sistema de Alertas
- Notificaciones push cuando hay alertas críticas
- Historial de alertas
- Niveles: info, warning, critical, emergency

### 3. Predicciones de Mantenimiento
- Componentes en riesgo
- Tiempo estimado hasta fallo
- Tendencias de desgaste

### 4. Estimación de Costes
- Coste estimado de reparaciones pendientes
- Ahorro potencial con mantenimiento preventivo
- Desglose por componente y urgencia

### 5. Recomendaciones
- Acciones sugeridas por el sistema
- Priorización por urgencia

---

## 🔗 Conexión con el Backend

### Opción A: REST API (Retrofit)

```kotlin
interface BoomApiService {
    @GET("api/vehicle/status")
    suspend fun getVehicleStatus(): VehicleStatus
    
    @GET("api/forecasts/status")
    suspend fun getForecasts(): ForecastsResponse
    
    @GET("api/costs/summary")
    suspend fun getCostSummary(): CostSummary
    
    @GET("api/predictions/alerts")
    suspend fun getAlerts(): List<Alert>
}
```

### Opción B: MQTT Directo (Eclipse Paho)

```kotlin
// Suscribirse a topics
mqttClient.subscribe("boomapp/predictions/alerts")
mqttClient.subscribe("boomapp/predictions/output")

// Recibir mensajes en tiempo real
mqttClient.setCallback(object : MqttCallback {
    override fun messageArrived(topic: String, message: MqttMessage) {
        // Actualizar UI con datos nuevos
    }
})
```

---

## 🌐 Endpoints del Backend

### Datos del Vehículo

| Endpoint | Descripción |
|----------|-------------|
| `GET /api/vehicle/status` | Estado completo del vehículo |
| `GET /api/vehicle/obd` | Datos OBD-II |
| `GET /api/vehicle/sensors` | Datos de sensores |

### Predicciones

| Endpoint | Descripción |
|----------|-------------|
| `GET /api/predictions/status` | Estado de predicciones y desgaste |
| `GET /api/predictions/wear` | Estado de desgaste de componentes |
| `GET /api/predictions/alerts` | Alertas activas |

### Pronósticos Futuros

| Endpoint | Descripción |
|----------|-------------|
| `GET /api/forecasts/status` | Estado completo de pronósticos |
| `GET /api/forecasts/high-risk` | Predicciones de alto riesgo |
| `GET /api/forecasts/recommendations` | Recomendaciones de mantenimiento |

### Costes (€)

| Endpoint | Descripción |
|----------|-------------|
| `GET /api/costs/estimate` | Estimación total de costes |
| `GET /api/costs/by-component/{name}` | Coste por componente |
| `GET /api/costs/by-urgency` | Costes por nivel de urgencia |
| `GET /api/costs/savings` | Ahorro potencial preventivo |
| `GET /api/costs/summary` | Resumen completo |

---

## 📲 Pantallas Sugeridas

| Pantalla | Contenido |
|----------|-----------|
| **Home** | Dashboard con gauges, salud general, alertas activas |
| **Alertas** | Lista de alertas con filtros por severidad |
| **Predicciones** | Componentes, tiempo hasta fallo, tendencias |
| **Costes** | Total estimado, desglose, ahorro preventivo |
| **Ajustes** | Configuración MQTT, notificaciones, perfil |

---

## 🔔 Notificaciones Push

```kotlin
// Cuando llega alerta crítica por MQTT
if (alert.severity == "critical" || alert.severity == "emergency") {
    showNotification(
        title = "⚠️ Alerta: ${alert.component}",
        body = alert.message,
        priority = HIGH
    )
}
```

---

## 📚 Stack Tecnológico Recomendado

| Componente | Tecnología |
|------------|------------|
| **Lenguaje** | Kotlin |
| **UI** | Jetpack Compose |
| **HTTP Client** | Ktor |
| **Serialización** | Kotlinx Serialization |
| **MQTT** | Eclipse Paho Android |
| **DI** | Koin |
| **Async** | Coroutines + Flow |
| **Notificaciones** | Firebase Cloud Messaging |

---

## 📦 Dependencias Gradle

```kotlin
// build.gradle.kts (app)
plugins {
    id("org.jetbrains.kotlin.plugin.serialization") version "1.9.21"
}

dependencies {
    // Jetpack Compose
    implementation("androidx.compose.ui:ui:1.5.4")
    implementation("androidx.compose.material3:material3:1.1.2")
    implementation("androidx.activity:activity-compose:1.8.1")
    
    // Ktor (REST API)
    implementation("io.ktor:ktor-client-android:2.3.7")
    implementation("io.ktor:ktor-client-content-negotiation:2.3.7")
    implementation("io.ktor:ktor-serialization-kotlinx-json:2.3.7")
    implementation("io.ktor:ktor-client-logging:2.3.7")
    
    // Kotlinx Serialization
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.2")
    
    // MQTT (Eclipse Paho)
    implementation("org.eclipse.paho:org.eclipse.paho.client.mqttv3:1.2.5")
    implementation("org.eclipse.paho:org.eclipse.paho.android.service:1.1.1")
    
    // Koin (Dependency Injection)
    implementation("io.insert-koin:koin-android:3.5.0")
    implementation("io.insert-koin:koin-androidx-compose:3.5.0")
    
    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
    
    // ViewModel
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.6.2")
    
    // Navigation
    implementation("androidx.navigation:navigation-compose:2.7.6")
}
```

---

## 🔧 Configuración MQTT

```kotlin
object MqttConfig {
    const val BROKER = "ssl://d9c7356a58394727a868b97158e7abb5.s1.eu.hivemq.cloud:8883"
    const val USERNAME = "tu_usuario"
    const val PASSWORD = "tu_password"
    
    object Topics {
        const val OBD = "boomapp/vehicle/obd"
        const val SENSORS = "boomapp/vehicle/sensors"
        const val PREDICTIONS = "boomapp/predictions/output"
        const val ALERTS = "boomapp/predictions/alerts"
    }
}
```

---

## 📊 Modelos de Datos

```kotlin
data class VehicleStatus(
    val obd: OBDData,
    val sensors: SensorData,
    val status: String,
    val lastUpdate: String
)

data class OBDData(
    val rpm: Int,
    val speed: Int,
    val engineTemp: Double,
    val throttle: Double,
    val fuelLevel: Double
)

data class Alert(
    val id: String,
    val component: String,
    val severity: String,  // info, warning, critical, emergency
    val message: String,
    val timestamp: Long
)

data class CostSummary(
    val totalEstimated: CostRange,
    val potentialSavings: Double,
    val repairCount: Int,
    val componentsAtRisk: List<ComponentRisk>,
    val immediateActionRequired: Boolean,
    val currency: String
)

data class CostRange(
    val min: Double,
    val max: Double,
    val average: Double
)
```

---

## ✅ Resumen: ¿Qué debe hacer la app?

1. **Conectar** al backend (REST) y/o MQTT (tiempo real)
2. **Mostrar** datos del vehículo en dashboard visual
3. **Alertar** al usuario con notificaciones push
4. **Informar** sobre predicciones y costes de mantenimiento
5. **Recomendar** acciones preventivas

---

## 🔗 URLs del Backend

- **API Base**: `https://boomap-production.up.railway.app`
- **Swagger UI**: `https://boomap-production.up.railway.app/docs`
- **WebSocket**: `wss://boomap-production.up.railway.app/ws/vehicle`
- **MQTT Broker**: `ssl://d9c7356a58394727a868b97158e7abb5.s1.eu.hivemq.cloud:8883`
