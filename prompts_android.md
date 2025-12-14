# 🤖 Prompts para Desarrollo App Android BOOMApp

Prompts estructurados para construir la app Android con **Kotlin**, **Clean Architecture**, **MVVM**, **Jetpack Compose** y **Koin**.

---

## 📋 Índice de Prompts

1. [Configuración inicial del proyecto](#prompt-1-configuración-inicial)
2. [Estructura Clean Architecture](#prompt-2-estructura-clean-architecture)
3. [Capa Domain - Modelos y casos de uso](#prompt-3-capa-domain)
4. [Capa Data - Repositorios y fuentes de datos](#prompt-4-capa-data)
5. [Configuración Koin (DI)](#prompt-5-configuración-koin)
6. [Cliente REST con Retrofit](#prompt-6-cliente-rest)
7. [Cliente MQTT con Paho](#prompt-7-cliente-mqtt)
8. [Pantalla Dashboard](#prompt-8-pantalla-dashboard)
9. [Pantalla Alertas](#prompt-9-pantalla-alertas)
10. [Pantalla Predicciones](#prompt-10-pantalla-predicciones)
11. [Pantalla Costes](#prompt-11-pantalla-costes)
12. [Sistema de Notificaciones](#prompt-12-notificaciones)
13. [Navegación](#prompt-13-navegación)
14. [Testing](#prompt-14-testing)

---

## Prompt 1: Configuración Inicial

```
Crea un proyecto Android con las siguientes características:

- Nombre: BOOMApp
- Package: com.boomapp.android
- Min SDK: 26 (Android 8.0)
- Target SDK: 34
- Lenguaje: Kotlin
- UI: Jetpack Compose con Material 3
- Arquitectura: Clean Architecture + MVVM
- Inyección de dependencias: Koin

Configura el build.gradle.kts (project y app) con las siguientes dependencias:

1. Jetpack Compose (BOM 2024.01.00)
2. Material 3
3. Navigation Compose
4. Retrofit 2.9.0 + OkHttp 4.12.0 + Gson converter
5. Koin 3.5.0 (koin-android, koin-androidx-compose)
6. Coroutines 1.7.3
7. ViewModel Compose
8. Eclipse Paho MQTT Android 1.2.5
9. Coil para imágenes (opcional)

Incluye los permisos necesarios en AndroidManifest.xml:
- INTERNET
- ACCESS_NETWORK_STATE
- FOREGROUND_SERVICE (para MQTT)
- POST_NOTIFICATIONS (Android 13+)

Crea la clase Application con inicialización de Koin.
```

---

## Prompt 2: Estructura Clean Architecture

```
Crea la estructura de carpetas siguiendo Clean Architecture para la app BOOMApp:

com.boomapp.android/
├── app/
│   ├── BOOMApplication.kt
│   └── MainActivity.kt
├── di/
│   ├── AppModule.kt
│   ├── NetworkModule.kt
│   ├── RepositoryModule.kt
│   └── ViewModelModule.kt
├── domain/
│   ├── model/
│   │   ├── VehicleStatus.kt
│   │   ├── OBDData.kt
│   │   ├── SensorData.kt
│   │   ├── Alert.kt
│   │   ├── Prediction.kt
│   │   ├── Forecast.kt
│   │   ├── CostEstimate.kt
│   │   └── ComponentHealth.kt
│   ├── repository/
│   │   ├── VehicleRepository.kt
│   │   ├── PredictionRepository.kt
│   │   └── CostRepository.kt
│   └── usecase/
│       ├── GetVehicleStatusUseCase.kt
│       ├── GetAlertsUseCase.kt
│       ├── GetForecastsUseCase.kt
│       ├── GetCostEstimateUseCase.kt
│       └── SubscribeToMqttUseCase.kt
├── data/
│   ├── remote/
│   │   ├── api/
│   │   │   └── BoomApiService.kt
│   │   ├── mqtt/
│   │   │   └── MqttDataSource.kt
│   │   └── dto/
│   │       ├── VehicleStatusDto.kt
│   │       ├── AlertDto.kt
│   │       ├── ForecastDto.kt
│   │       └── CostEstimateDto.kt
│   ├── repository/
│   │   ├── VehicleRepositoryImpl.kt
│   │   ├── PredictionRepositoryImpl.kt
│   │   └── CostRepositoryImpl.kt
│   └── mapper/
│       └── DtoMappers.kt
├── presentation/
│   ├── navigation/
│   │   └── NavGraph.kt
│   ├── theme/
│   │   ├── Color.kt
│   │   ├── Theme.kt
│   │   └── Type.kt
│   ├── components/
│   │   ├── GaugeComponent.kt
│   │   ├── AlertCard.kt
│   │   ├── HealthIndicator.kt
│   │   └── CostCard.kt
│   ├── dashboard/
│   │   ├── DashboardScreen.kt
│   │   └── DashboardViewModel.kt
│   ├── alerts/
│   │   ├── AlertsScreen.kt
│   │   └── AlertsViewModel.kt
│   ├── predictions/
│   │   ├── PredictionsScreen.kt
│   │   └── PredictionsViewModel.kt
│   ├── costs/
│   │   ├── CostsScreen.kt
│   │   └── CostsViewModel.kt
│   └── settings/
│       ├── SettingsScreen.kt
│       └── SettingsViewModel.kt
└── util/
    ├── Constants.kt
    ├── Resource.kt
    └── Extensions.kt

Crea los archivos base vacíos con la estructura de paquetes correcta.
```

---

## Prompt 3: Capa Domain

```
Crea los modelos de dominio y casos de uso para BOOMApp.

MODELOS (domain/model/):

1. VehicleStatus.kt:
   - obd: OBDData
   - sensors: SensorData
   - status: String (online/offline)
   - lastUpdate: String

2. OBDData.kt:
   - rpm: Int
   - speed: Int
   - engineTemp: Double
   - throttle: Double
   - fuelLevel: Double

3. SensorData.kt:
   - ambientTemp: Double
   - vibration: Double
   - pressure: Double

4. Alert.kt:
   - id: String
   - component: String
   - severity: AlertSeverity (enum: INFO, WARNING, CRITICAL, EMERGENCY)
   - message: String
   - timestamp: Long
   - isAcknowledged: Boolean

5. Prediction.kt:
   - component: String
   - problemType: String
   - riskLevel: RiskLevel (enum: LOW, MODERATE, HIGH, CRITICAL)
   - confidence: Double
   - estimatedTimeToFailure: Double? (horas)
   - description: String

6. CostEstimate.kt:
   - totalMin: Double
   - totalMax: Double
   - totalAverage: Double
   - potentialSavings: Double
   - repairs: List<RepairCost>
   - currency: String = "EUR"

7. RepairCost.kt:
   - component: String
   - repairType: String
   - description: String
   - costMin: Double
   - costMax: Double
   - costAverage: Double
   - urgency: String
   - savingsIfPreventive: Double

8. ComponentHealth.kt:
   - name: String
   - health: Double (0-100)
   - trend: String (improving, stable, degrading)
   - predictions: List<Prediction>

INTERFACES REPOSITORY (domain/repository/):

1. VehicleRepository:
   - getVehicleStatus(): Flow<Resource<VehicleStatus>>
   - getOBDData(): Flow<Resource<OBDData>>
   - getSensorData(): Flow<Resource<SensorData>>

2. PredictionRepository:
   - getAlerts(): Flow<Resource<List<Alert>>>
   - getForecasts(): Flow<Resource<List<ComponentHealth>>>
   - getHighRiskPredictions(): Flow<Resource<List<Prediction>>>
   - getRecommendations(): Flow<Resource<List<String>>>
   - subscribeToAlerts(): Flow<Alert>

3. CostRepository:
   - getCostEstimate(): Flow<Resource<CostEstimate>>
   - getCostByComponent(component: String): Flow<Resource<CostEstimate>>
   - getCostByUrgency(): Flow<Resource<Map<String, CostEstimate>>>
   - getPotentialSavings(): Flow<Resource<Double>>

CASOS DE USO (domain/usecase/):
Crea casos de uso simples que encapsulen las llamadas al repositorio.
Usa el patrón invoke() operator para llamarlos como funciones.
```

---

## Prompt 4: Capa Data

```
Implementa la capa Data para BOOMApp.

DTOs (data/remote/dto/):
Crea los DTOs que mapean las respuestas JSON del backend.
Usa @SerializedName para mapear campos con nombres diferentes.

Ejemplo VehicleStatusDto:
{
  "obd": { "rpm": 3500, "speed": 120, ... },
  "sensors": { "ambient_temp": 25.5, ... },
  "status": "online",
  "last_update": "2024-01-15T10:30:00"
}

MAPPERS (data/mapper/DtoMappers.kt):
Crea funciones de extensión para convertir DTOs a modelos de dominio:
- VehicleStatusDto.toDomain(): VehicleStatus
- AlertDto.toDomain(): Alert
- ForecastDto.toDomain(): ComponentHealth
- CostEstimateDto.toDomain(): CostEstimate

API SERVICE (data/remote/api/BoomApiService.kt):
Interface Retrofit con los endpoints:

@GET("api/vehicle/status")
suspend fun getVehicleStatus(): Response<VehicleStatusDto>

@GET("api/predictions/alerts")
suspend fun getAlerts(): Response<List<AlertDto>>

@GET("api/forecasts/status")
suspend fun getForecasts(): Response<ForecastsDto>

@GET("api/forecasts/high-risk")
suspend fun getHighRiskPredictions(): Response<List<PredictionDto>>

@GET("api/forecasts/recommendations")
suspend fun getRecommendations(): Response<RecommendationsDto>

@GET("api/costs/estimate")
suspend fun getCostEstimate(): Response<CostEstimateDto>

@GET("api/costs/by-component/{component}")
suspend fun getCostByComponent(@Path("component") component: String): Response<CostEstimateDto>

@GET("api/costs/summary")
suspend fun getCostSummary(): Response<CostSummaryDto>

REPOSITORY IMPL (data/repository/):
Implementa los repositorios usando:
- Try-catch para manejar errores de red
- Resource sealed class (Success, Error, Loading)
- Flow para emisión reactiva
- Mappers para convertir DTOs a dominio
```

---

## Prompt 5: Configuración Koin

```
Configura Koin como framework de inyección de dependencias para BOOMApp.

di/NetworkModule.kt:
- Provee OkHttpClient con logging interceptor
- Provee Retrofit con base URL: "https://boomap-production.up.railway.app/"
- Provee BoomApiService

di/RepositoryModule.kt:
- Provee VehicleRepositoryImpl como VehicleRepository
- Provee PredictionRepositoryImpl como PredictionRepository
- Provee CostRepositoryImpl como CostRepository

di/ViewModelModule.kt:
- Provee DashboardViewModel
- Provee AlertsViewModel
- Provee PredictionsViewModel
- Provee CostsViewModel
- Provee SettingsViewModel

di/AppModule.kt:
- Provee MqttDataSource con configuración:
  - Broker: "ssl://d9c7356a58394727a868b97158e7abb5.s1.eu.hivemq.cloud:8883"
  - Topics: boomapp/vehicle/obd, boomapp/predictions/alerts, etc.
- Provee CoroutineDispatchers

app/BOOMApplication.kt:
Inicializa Koin con startKoin {} incluyendo todos los módulos:
- androidContext(this)
- modules(networkModule, repositoryModule, viewModelModule, appModule)

Usa las siguientes convenciones de Koin:
- single { } para singletons
- factory { } para instancias nuevas
- viewModel { } para ViewModels
- get() para resolver dependencias
```

---

## Prompt 6: Cliente REST

```
Implementa el cliente REST completo con Retrofit para BOOMApp.

1. Crea NetworkModule.kt con:

val networkModule = module {
    single {
        HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }
    }
    
    single {
        OkHttpClient.Builder()
            .addInterceptor(get<HttpLoggingInterceptor>())
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build()
    }
    
    single {
        Retrofit.Builder()
            .baseUrl(Constants.BASE_URL)
            .client(get())
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }
    
    single { get<Retrofit>().create(BoomApiService::class.java) }
}

2. Crea util/Resource.kt:

sealed class Resource<T>(
    val data: T? = null,
    val message: String? = null
) {
    class Success<T>(data: T) : Resource<T>(data)
    class Error<T>(message: String, data: T? = null) : Resource<T>(data, message)
    class Loading<T>(data: T? = null) : Resource<T>(data)
}

3. Crea util/Constants.kt:

object Constants {
    const val BASE_URL = "https://boomap-production.up.railway.app/"
    
    object MqttConfig {
        const val BROKER = "ssl://d9c7356a58394727a868b97158e7abb5.s1.eu.hivemq.cloud:8883"
        const val CLIENT_ID = "boomapp-android-"
    }
    
    object Topics {
        const val OBD = "boomapp/vehicle/obd"
        const val SENSORS = "boomapp/vehicle/sensors"
        const val PREDICTIONS = "boomapp/predictions/output"
        const val ALERTS = "boomapp/predictions/alerts"
    }
}

4. Implementa VehicleRepositoryImpl con manejo de errores:

class VehicleRepositoryImpl(
    private val api: BoomApiService
) : VehicleRepository {
    
    override fun getVehicleStatus(): Flow<Resource<VehicleStatus>> = flow {
        emit(Resource.Loading())
        try {
            val response = api.getVehicleStatus()
            if (response.isSuccessful) {
                response.body()?.let {
                    emit(Resource.Success(it.toDomain()))
                } ?: emit(Resource.Error("Respuesta vacía"))
            } else {
                emit(Resource.Error("Error: ${response.code()}"))
            }
        } catch (e: Exception) {
            emit(Resource.Error(e.message ?: "Error desconocido"))
        }
    }
}
```

---

## Prompt 7: Cliente MQTT

```
Implementa el cliente MQTT con Eclipse Paho para BOOMApp.

Crea data/remote/mqtt/MqttDataSource.kt:

class MqttDataSource(private val context: Context) {
    
    private var mqttClient: MqttAndroidClient? = null
    private val _connectionState = MutableStateFlow(MqttConnectionState.DISCONNECTED)
    val connectionState: StateFlow<MqttConnectionState> = _connectionState
    
    private val _alerts = MutableSharedFlow<Alert>()
    val alerts: SharedFlow<Alert> = _alerts
    
    private val _vehicleData = MutableSharedFlow<VehicleStatus>()
    val vehicleData: SharedFlow<VehicleStatus> = _vehicleData
    
    fun connect(username: String, password: String) {
        val clientId = Constants.MqttConfig.CLIENT_ID + System.currentTimeMillis()
        mqttClient = MqttAndroidClient(context, Constants.MqttConfig.BROKER, clientId)
        
        val options = MqttConnectOptions().apply {
            isAutomaticReconnect = true
            isCleanSession = false
            userName = username
            password = password.toCharArray()
            // Configurar SSL para HiveMQ Cloud
            socketFactory = SSLSocketFactory.getDefault() as SSLSocketFactory
        }
        
        mqttClient?.connect(options, null, object : IMqttActionListener {
            override fun onSuccess(asyncActionToken: IMqttToken?) {
                _connectionState.value = MqttConnectionState.CONNECTED
                subscribeToTopics()
            }
            
            override fun onFailure(asyncActionToken: IMqttToken?, exception: Throwable?) {
                _connectionState.value = MqttConnectionState.ERROR
            }
        })
        
        mqttClient?.setCallback(object : MqttCallback {
            override fun messageArrived(topic: String?, message: MqttMessage?) {
                message?.let { handleMessage(topic, String(it.payload)) }
            }
            
            override fun connectionLost(cause: Throwable?) {
                _connectionState.value = MqttConnectionState.DISCONNECTED
            }
            
            override fun deliveryComplete(token: IMqttDeliveryToken?) {}
        })
    }
    
    private fun subscribeToTopics() {
        val topics = arrayOf(
            Constants.Topics.OBD,
            Constants.Topics.SENSORS,
            Constants.Topics.ALERTS,
            Constants.Topics.PREDICTIONS
        )
        mqttClient?.subscribe(topics, intArrayOf(1, 1, 1, 1))
    }
    
    private fun handleMessage(topic: String?, payload: String) {
        // Parsear JSON según el topic y emitir al Flow correspondiente
        when (topic) {
            Constants.Topics.ALERTS -> {
                val alert = Gson().fromJson(payload, AlertDto::class.java)
                CoroutineScope(Dispatchers.IO).launch {
                    _alerts.emit(alert.toDomain())
                }
            }
            // ... otros topics
        }
    }
    
    fun disconnect() {
        mqttClient?.disconnect()
        _connectionState.value = MqttConnectionState.DISCONNECTED
    }
}

enum class MqttConnectionState {
    CONNECTED, DISCONNECTED, CONNECTING, ERROR
}

Añade MqttDataSource al módulo Koin y úsalo en los repositorios para datos en tiempo real.
```

---

## Prompt 8: Pantalla Dashboard

```
Crea la pantalla Dashboard con Jetpack Compose para BOOMApp.

presentation/dashboard/DashboardViewModel.kt:

class DashboardViewModel(
    private val getVehicleStatusUseCase: GetVehicleStatusUseCase,
    private val getAlertsUseCase: GetAlertsUseCase,
    private val getCostEstimateUseCase: GetCostEstimateUseCase
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(DashboardUiState())
    val uiState: StateFlow<DashboardUiState> = _uiState.asStateFlow()
    
    init {
        loadDashboardData()
    }
    
    private fun loadDashboardData() {
        viewModelScope.launch {
            // Combinar flows de datos
            combine(
                getVehicleStatusUseCase(),
                getAlertsUseCase(),
                getCostEstimateUseCase()
            ) { vehicle, alerts, costs ->
                // Actualizar estado
            }.collect { ... }
        }
    }
    
    fun refresh() { ... }
}

data class DashboardUiState(
    val isLoading: Boolean = true,
    val vehicleStatus: VehicleStatus? = null,
    val activeAlerts: List<Alert> = emptyList(),
    val overallHealth: Double = 100.0,
    val estimatedCosts: Double = 0.0,
    val error: String? = null
)

presentation/dashboard/DashboardScreen.kt:

@Composable
fun DashboardScreen(
    viewModel: DashboardViewModel = koinViewModel(),
    onNavigateToAlerts: () -> Unit,
    onNavigateToCosts: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    
    Scaffold(
        topBar = { DashboardTopBar() }
    ) { padding ->
        if (uiState.isLoading) {
            LoadingIndicator()
        } else {
            LazyColumn(modifier = Modifier.padding(padding)) {
                // Sección: Estado de conexión
                item { ConnectionStatusCard(uiState.vehicleStatus?.status) }
                
                // Sección: Gauges principales (RPM, Velocidad, Temp)
                item {
                    Row(horizontalArrangement = Arrangement.SpaceEvenly) {
                        GaugeComponent(
                            value = uiState.vehicleStatus?.obd?.rpm ?: 0,
                            maxValue = 8000,
                            label = "RPM"
                        )
                        GaugeComponent(
                            value = uiState.vehicleStatus?.obd?.speed ?: 0,
                            maxValue = 220,
                            label = "km/h"
                        )
                        GaugeComponent(
                            value = uiState.vehicleStatus?.obd?.engineTemp?.toInt() ?: 0,
                            maxValue = 130,
                            label = "°C"
                        )
                    }
                }
                
                // Sección: Salud general
                item {
                    HealthIndicator(
                        health = uiState.overallHealth,
                        label = "Salud del Vehículo"
                    )
                }
                
                // Sección: Alertas activas (resumen)
                item {
                    AlertsSummaryCard(
                        alerts = uiState.activeAlerts.take(3),
                        onSeeAll = onNavigateToAlerts
                    )
                }
                
                // Sección: Costes estimados
                item {
                    CostSummaryCard(
                        estimatedCost = uiState.estimatedCosts,
                        onClick = onNavigateToCosts
                    )
                }
            }
        }
    }
}

Crea los componentes reutilizables:
- GaugeComponent: Indicador circular animado
- HealthIndicator: Barra de progreso con colores (verde/amarillo/rojo)
- AlertsSummaryCard: Card con lista de alertas
- CostSummaryCard: Card con coste total y botón "Ver detalles"
```

---

## Prompt 9: Pantalla Alertas

```
Crea la pantalla de Alertas con Jetpack Compose para BOOMApp.

presentation/alerts/AlertsViewModel.kt:

class AlertsViewModel(
    private val getAlertsUseCase: GetAlertsUseCase,
    private val mqttDataSource: MqttDataSource
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(AlertsUiState())
    val uiState: StateFlow<AlertsUiState> = _uiState.asStateFlow()
    
    private val _selectedFilter = MutableStateFlow<AlertSeverity?>(null)
    
    init {
        loadAlerts()
        observeMqttAlerts()
    }
    
    private fun loadAlerts() { ... }
    
    private fun observeMqttAlerts() {
        viewModelScope.launch {
            mqttDataSource.alerts.collect { newAlert ->
                // Añadir nueva alerta a la lista y mostrar notificación si es crítica
            }
        }
    }
    
    fun setFilter(severity: AlertSeverity?) {
        _selectedFilter.value = severity
    }
    
    fun acknowledgeAlert(alertId: String) { ... }
}

data class AlertsUiState(
    val isLoading: Boolean = true,
    val alerts: List<Alert> = emptyList(),
    val filteredAlerts: List<Alert> = emptyList(),
    val selectedFilter: AlertSeverity? = null,
    val error: String? = null
)

presentation/alerts/AlertsScreen.kt:

@Composable
fun AlertsScreen(
    viewModel: AlertsViewModel = koinViewModel(),
    onNavigateBack: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Alertas") },
                navigationIcon = { BackButton(onNavigateBack) }
            )
        }
    ) { padding ->
        Column(modifier = Modifier.padding(padding)) {
            // Filtros por severidad
            FilterChipsRow(
                filters = AlertSeverity.values().toList(),
                selectedFilter = uiState.selectedFilter,
                onFilterSelected = viewModel::setFilter
            )
            
            // Lista de alertas
            LazyColumn {
                items(uiState.filteredAlerts) { alert ->
                    AlertCard(
                        alert = alert,
                        onAcknowledge = { viewModel.acknowledgeAlert(alert.id) }
                    )
                }
            }
        }
    }
}

presentation/components/AlertCard.kt:

@Composable
fun AlertCard(
    alert: Alert,
    onAcknowledge: () -> Unit
) {
    Card(
        colors = CardDefaults.cardColors(
            containerColor = when (alert.severity) {
                AlertSeverity.EMERGENCY -> Color(0xFFFFCDD2)
                AlertSeverity.CRITICAL -> Color(0xFFFFE0B2)
                AlertSeverity.WARNING -> Color(0xFFFFF9C4)
                AlertSeverity.INFO -> Color(0xFFE3F2FD)
            }
        )
    ) {
        Row {
            // Icono según severidad
            Icon(
                imageVector = when (alert.severity) {
                    AlertSeverity.EMERGENCY -> Icons.Filled.Error
                    AlertSeverity.CRITICAL -> Icons.Filled.Warning
                    else -> Icons.Filled.Info
                },
                tint = severityColor(alert.severity)
            )
            
            Column {
                Text(alert.component, style = MaterialTheme.typography.titleMedium)
                Text(alert.message, style = MaterialTheme.typography.bodyMedium)
                Text(formatTimestamp(alert.timestamp), style = MaterialTheme.typography.bodySmall)
            }
            
            if (!alert.isAcknowledged) {
                IconButton(onClick = onAcknowledge) {
                    Icon(Icons.Filled.Check, "Marcar como leída")
                }
            }
        }
    }
}
```

---

## Prompt 10: Pantalla Predicciones

```
Crea la pantalla de Predicciones con Jetpack Compose para BOOMApp.

presentation/predictions/PredictionsViewModel.kt:

class PredictionsViewModel(
    private val getForecastsUseCase: GetForecastsUseCase,
    private val getHighRiskPredictionsUseCase: GetHighRiskPredictionsUseCase,
    private val getRecommendationsUseCase: GetRecommendationsUseCase
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(PredictionsUiState())
    val uiState: StateFlow<PredictionsUiState> = _uiState.asStateFlow()
    
    init {
        loadPredictions()
    }
    
    private fun loadPredictions() {
        viewModelScope.launch {
            combine(
                getForecastsUseCase(),
                getHighRiskPredictionsUseCase(),
                getRecommendationsUseCase()
            ) { forecasts, highRisk, recommendations ->
                PredictionsUiState(
                    isLoading = false,
                    componentHealth = forecasts.data ?: emptyList(),
                    highRiskPredictions = highRisk.data ?: emptyList(),
                    recommendations = recommendations.data ?: emptyList()
                )
            }.collect { _uiState.value = it }
        }
    }
    
    fun selectComponent(component: ComponentHealth) {
        _uiState.update { it.copy(selectedComponent = component) }
    }
}

data class PredictionsUiState(
    val isLoading: Boolean = true,
    val componentHealth: List<ComponentHealth> = emptyList(),
    val highRiskPredictions: List<Prediction> = emptyList(),
    val recommendations: List<String> = emptyList(),
    val selectedComponent: ComponentHealth? = null,
    val error: String? = null
)

presentation/predictions/PredictionsScreen.kt:

@Composable
fun PredictionsScreen(
    viewModel: PredictionsViewModel = koinViewModel(),
    onNavigateBack: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    
    Scaffold(
        topBar = { TopAppBar(title = { Text("Predicciones") }) }
    ) { padding ->
        LazyColumn(modifier = Modifier.padding(padding)) {
            // Sección: Predicciones de alto riesgo
            if (uiState.highRiskPredictions.isNotEmpty()) {
                item {
                    Text(
                        "⚠️ Alto Riesgo",
                        style = MaterialTheme.typography.titleLarge,
                        color = MaterialTheme.colorScheme.error
                    )
                }
                items(uiState.highRiskPredictions) { prediction ->
                    HighRiskPredictionCard(prediction)
                }
            }
            
            // Sección: Salud por componente
            item {
                Text("Salud de Componentes", style = MaterialTheme.typography.titleLarge)
            }
            items(uiState.componentHealth) { component ->
                ComponentHealthCard(
                    component = component,
                    onClick = { viewModel.selectComponent(component) }
                )
            }
            
            // Sección: Recomendaciones
            item {
                Text("Recomendaciones", style = MaterialTheme.typography.titleLarge)
            }
            items(uiState.recommendations) { recommendation ->
                RecommendationItem(recommendation)
            }
        }
    }
    
    // Bottom Sheet con detalles del componente seleccionado
    uiState.selectedComponent?.let { component ->
        ComponentDetailBottomSheet(
            component = component,
            onDismiss = { viewModel.selectComponent(null) }
        )
    }
}

@Composable
fun ComponentHealthCard(component: ComponentHealth, onClick: () -> Unit) {
    Card(onClick = onClick) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            // Icono del componente
            ComponentIcon(component.name)
            
            Column(modifier = Modifier.weight(1f)) {
                Text(component.name.capitalize())
                Text(
                    "Tendencia: ${component.trend}",
                    color = trendColor(component.trend)
                )
            }
            
            // Indicador circular de salud
            CircularHealthIndicator(health = component.health)
        }
    }
}

@Composable
fun HighRiskPredictionCard(prediction: Prediction) {
    Card(colors = CardDefaults.cardColors(containerColor = Color(0xFFFFEBEE))) {
        Column {
            Row {
                Icon(Icons.Filled.Warning, tint = Color.Red)
                Text(prediction.component, fontWeight = FontWeight.Bold)
            }
            Text(prediction.description)
            prediction.estimatedTimeToFailure?.let { hours ->
                Text(
                    "Tiempo estimado: ${formatHours(hours)}",
                    color = Color.Red
                )
            }
            LinearProgressIndicator(
                progress = prediction.confidence.toFloat(),
                color = Color.Red
            )
            Text("Confianza: ${(prediction.confidence * 100).toInt()}%")
        }
    }
}
```

---

## Prompt 11: Pantalla Costes

```
Crea la pantalla de Costes con Jetpack Compose para BOOMApp.

presentation/costs/CostsViewModel.kt:

class CostsViewModel(
    private val getCostEstimateUseCase: GetCostEstimateUseCase,
    private val getCostByUrgencyUseCase: GetCostByUrgencyUseCase,
    private val getPotentialSavingsUseCase: GetPotentialSavingsUseCase
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(CostsUiState())
    val uiState: StateFlow<CostsUiState> = _uiState.asStateFlow()
    
    init {
        loadCosts()
    }
    
    private fun loadCosts() {
        viewModelScope.launch {
            getCostEstimateUseCase().collect { result ->
                when (result) {
                    is Resource.Success -> {
                        _uiState.update {
                            it.copy(
                                isLoading = false,
                                costEstimate = result.data,
                                error = null
                            )
                        }
                    }
                    is Resource.Error -> {
                        _uiState.update {
                            it.copy(isLoading = false, error = result.message)
                        }
                    }
                    is Resource.Loading -> {
                        _uiState.update { it.copy(isLoading = true) }
                    }
                }
            }
        }
    }
    
    fun toggleExpandRepair(repairId: String) { ... }
}

data class CostsUiState(
    val isLoading: Boolean = true,
    val costEstimate: CostEstimate? = null,
    val expandedRepairs: Set<String> = emptySet(),
    val error: String? = null
)

presentation/costs/CostsScreen.kt:

@Composable
fun CostsScreen(
    viewModel: CostsViewModel = koinViewModel(),
    onNavigateBack: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    
    Scaffold(
        topBar = { TopAppBar(title = { Text("Costes Estimados") }) }
    ) { padding ->
        LazyColumn(modifier = Modifier.padding(padding)) {
            uiState.costEstimate?.let { estimate ->
                // Card principal con total
                item {
                    TotalCostCard(
                        min = estimate.totalMin,
                        max = estimate.totalMax,
                        average = estimate.totalAverage,
                        currency = estimate.currency
                    )
                }
                
                // Card de ahorro potencial
                if (estimate.potentialSavings > 0) {
                    item {
                        SavingsCard(
                            savings = estimate.potentialSavings,
                            currency = estimate.currency
                        )
                    }
                }
                
                // Lista de reparaciones
                item {
                    Text(
                        "Desglose de Reparaciones",
                        style = MaterialTheme.typography.titleLarge
                    )
                }
                
                items(estimate.repairs) { repair ->
                    RepairCostCard(
                        repair = repair,
                        isExpanded = repair.component in uiState.expandedRepairs,
                        onToggleExpand = { viewModel.toggleExpandRepair(repair.component) }
                    )
                }
            }
        }
    }
}

@Composable
fun TotalCostCard(min: Double, max: Double, average: Double, currency: String) {
    Card(
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer
        )
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            modifier = Modifier.padding(24.dp)
        ) {
            Text("Coste Total Estimado", style = MaterialTheme.typography.titleMedium)
            
            Text(
                "${average.formatCurrency()} $currency",
                style = MaterialTheme.typography.displayMedium,
                fontWeight = FontWeight.Bold
            )
            
            Text(
                "Rango: ${min.formatCurrency()} - ${max.formatCurrency()} $currency",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Composable
fun SavingsCard(savings: Double, currency: String) {
    Card(
        colors = CardDefaults.cardColors(
            containerColor = Color(0xFFE8F5E9)
        )
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.padding(16.dp)
        ) {
            Icon(
                Icons.Filled.Savings,
                contentDescription = null,
                tint = Color(0xFF4CAF50),
                modifier = Modifier.size(48.dp)
            )
            Column(modifier = Modifier.padding(start = 16.dp)) {
                Text("Ahorro Potencial", fontWeight = FontWeight.Bold)
                Text(
                    "${savings.formatCurrency()} $currency",
                    style = MaterialTheme.typography.titleLarge,
                    color = Color(0xFF4CAF50)
                )
                Text(
                    "Con mantenimiento preventivo",
                    style = MaterialTheme.typography.bodySmall
                )
            }
        }
    }
}

@Composable
fun RepairCostCard(repair: RepairCost, isExpanded: Boolean, onToggleExpand: () -> Unit) {
    Card(onClick = onToggleExpand) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                ComponentIcon(repair.component)
                Column(modifier = Modifier.weight(1f)) {
                    Text(repair.component.capitalize(), fontWeight = FontWeight.Bold)
                    Text(repair.repairType)
                }
                UrgencyChip(repair.urgency)
                Text(
                    "${repair.costAverage.formatCurrency()} €",
                    fontWeight = FontWeight.Bold
                )
            }
            
            AnimatedVisibility(visible = isExpanded) {
                Column {
                    Divider()
                    Text(repair.description)
                    Text("Rango: ${repair.costMin.formatCurrency()} - ${repair.costMax.formatCurrency()} €")
                    if (repair.savingsIfPreventive > 0) {
                        Text(
                            "💡 Ahorro preventivo: ${repair.savingsIfPreventive.formatCurrency()} €",
                            color = Color(0xFF4CAF50)
                        )
                    }
                }
            }
        }
    }
}
```

---

## Prompt 12: Sistema de Notificaciones

```
Implementa el sistema de notificaciones push para BOOMApp.

1. Crea util/NotificationHelper.kt:

class NotificationHelper(private val context: Context) {
    
    companion object {
        const val CHANNEL_ALERTS = "alerts_channel"
        const val CHANNEL_PREDICTIONS = "predictions_channel"
    }
    
    init {
        createNotificationChannels()
    }
    
    private fun createNotificationChannels() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val alertsChannel = NotificationChannel(
                CHANNEL_ALERTS,
                "Alertas del Vehículo",
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "Alertas críticas del vehículo"
                enableVibration(true)
            }
            
            val predictionsChannel = NotificationChannel(
                CHANNEL_PREDICTIONS,
                "Predicciones",
                NotificationManager.IMPORTANCE_DEFAULT
            ).apply {
                description = "Predicciones de mantenimiento"
            }
            
            val notificationManager = context.getSystemService(NotificationManager::class.java)
            notificationManager.createNotificationChannels(listOf(alertsChannel, predictionsChannel))
        }
    }
    
    fun showAlertNotification(alert: Alert) {
        val intent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            putExtra("navigate_to", "alerts")
        }
        val pendingIntent = PendingIntent.getActivity(
            context, 0, intent, PendingIntent.FLAG_IMMUTABLE
        )
        
        val (icon, color) = when (alert.severity) {
            AlertSeverity.EMERGENCY -> R.drawable.ic_emergency to Color.RED
            AlertSeverity.CRITICAL -> R.drawable.ic_warning to Color(0xFFFF9800)
            AlertSeverity.WARNING -> R.drawable.ic_warning to Color(0xFFFFC107)
            AlertSeverity.INFO -> R.drawable.ic_info to Color(0xFF2196F3)
        }
        
        val notification = NotificationCompat.Builder(context, CHANNEL_ALERTS)
            .setSmallIcon(icon)
            .setContentTitle("⚠️ ${alert.component}")
            .setContentText(alert.message)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setColor(color.toArgb())
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .build()
        
        NotificationManagerCompat.from(context).notify(alert.id.hashCode(), notification)
    }
    
    fun showCostWarningNotification(totalCost: Double) {
        if (totalCost > 500) {
            val notification = NotificationCompat.Builder(context, CHANNEL_PREDICTIONS)
                .setSmallIcon(R.drawable.ic_money)
                .setContentTitle("💰 Costes de mantenimiento")
                .setContentText("Tienes reparaciones pendientes por ${totalCost.formatCurrency()}€")
                .setPriority(NotificationCompat.PRIORITY_DEFAULT)
                .build()
            
            NotificationManagerCompat.from(context).notify(1001, notification)
        }
    }
}

2. Integra con MqttDataSource para mostrar notificaciones automáticas:

// En MqttDataSource.handleMessage()
if (topic == Constants.Topics.ALERTS) {
    val alert = parseAlert(payload)
    if (alert.severity in listOf(AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY)) {
        notificationHelper.showAlertNotification(alert)
    }
}

3. Solicita permisos en Android 13+:

// En MainActivity o SettingsScreen
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        // Manejar resultado
    }
    
    LaunchedEffect(Unit) {
        permissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
    }
}
```

---

## Prompt 13: Navegación

```
Implementa la navegación con Navigation Compose para BOOMApp.

presentation/navigation/NavGraph.kt:

sealed class Screen(val route: String) {
    object Dashboard : Screen("dashboard")
    object Alerts : Screen("alerts")
    object Predictions : Screen("predictions")
    object Costs : Screen("costs")
    object Settings : Screen("settings")
}

@Composable
fun BOOMNavGraph(
    navController: NavHostController,
    modifier: Modifier = Modifier
) {
    NavHost(
        navController = navController,
        startDestination = Screen.Dashboard.route,
        modifier = modifier
    ) {
        composable(Screen.Dashboard.route) {
            DashboardScreen(
                onNavigateToAlerts = { navController.navigate(Screen.Alerts.route) },
                onNavigateToCosts = { navController.navigate(Screen.Costs.route) }
            )
        }
        
        composable(Screen.Alerts.route) {
            AlertsScreen(
                onNavigateBack = { navController.popBackStack() }
            )
        }
        
        composable(Screen.Predictions.route) {
            PredictionsScreen(
                onNavigateBack = { navController.popBackStack() }
            )
        }
        
        composable(Screen.Costs.route) {
            CostsScreen(
                onNavigateBack = { navController.popBackStack() }
            )
        }
        
        composable(Screen.Settings.route) {
            SettingsScreen(
                onNavigateBack = { navController.popBackStack() }
            )
        }
    }
}

app/MainActivity.kt:

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            BOOMAppTheme {
                MainScreen()
            }
        }
    }
}

@Composable
fun MainScreen() {
    val navController = rememberNavController()
    val currentBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = currentBackStackEntry?.destination?.route
    
    Scaffold(
        bottomBar = {
            NavigationBar {
                NavigationBarItem(
                    icon = { Icon(Icons.Filled.Dashboard, contentDescription = null) },
                    label = { Text("Dashboard") },
                    selected = currentRoute == Screen.Dashboard.route,
                    onClick = { navController.navigate(Screen.Dashboard.route) }
                )
                NavigationBarItem(
                    icon = { Icon(Icons.Filled.Warning, contentDescription = null) },
                    label = { Text("Alertas") },
                    selected = currentRoute == Screen.Alerts.route,
                    onClick = { navController.navigate(Screen.Alerts.route) }
                )
                NavigationBarItem(
                    icon = { Icon(Icons.Filled.Analytics, contentDescription = null) },
                    label = { Text("Predicciones") },
                    selected = currentRoute == Screen.Predictions.route,
                    onClick = { navController.navigate(Screen.Predictions.route) }
                )
                NavigationBarItem(
                    icon = { Icon(Icons.Filled.Euro, contentDescription = null) },
                    label = { Text("Costes") },
                    selected = currentRoute == Screen.Costs.route,
                    onClick = { navController.navigate(Screen.Costs.route) }
                )
                NavigationBarItem(
                    icon = { Icon(Icons.Filled.Settings, contentDescription = null) },
                    label = { Text("Ajustes") },
                    selected = currentRoute == Screen.Settings.route,
                    onClick = { navController.navigate(Screen.Settings.route) }
                )
            }
        }
    ) { padding ->
        BOOMNavGraph(
            navController = navController,
            modifier = Modifier.padding(padding)
        )
    }
}
```

---

## Prompt 14: Testing

```
Crea tests unitarios y de UI para BOOMApp.

1. Test de ViewModel (test/presentation/dashboard/DashboardViewModelTest.kt):

@OptIn(ExperimentalCoroutinesApi::class)
class DashboardViewModelTest {
    
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()
    
    private lateinit var viewModel: DashboardViewModel
    private lateinit var getVehicleStatusUseCase: GetVehicleStatusUseCase
    private lateinit var getAlertsUseCase: GetAlertsUseCase
    
    @Before
    fun setup() {
        getVehicleStatusUseCase = mockk()
        getAlertsUseCase = mockk()
        
        coEvery { getVehicleStatusUseCase() } returns flowOf(
            Resource.Success(mockVehicleStatus())
        )
        coEvery { getAlertsUseCase() } returns flowOf(
            Resource.Success(listOf(mockAlert()))
        )
        
        viewModel = DashboardViewModel(getVehicleStatusUseCase, getAlertsUseCase, mockk())
    }
    
    @Test
    fun `initial state is loading`() = runTest {
        val state = viewModel.uiState.first()
        assertTrue(state.isLoading)
    }
    
    @Test
    fun `state updates with vehicle data`() = runTest {
        advanceUntilIdle()
        val state = viewModel.uiState.first()
        assertFalse(state.isLoading)
        assertNotNull(state.vehicleStatus)
    }
    
    @Test
    fun `alerts are loaded correctly`() = runTest {
        advanceUntilIdle()
        val state = viewModel.uiState.first()
        assertEquals(1, state.activeAlerts.size)
    }
}

2. Test de Repository (test/data/repository/VehicleRepositoryImplTest.kt):

class VehicleRepositoryImplTest {
    
    private lateinit var repository: VehicleRepositoryImpl
    private lateinit var api: BoomApiService
    
    @Before
    fun setup() {
        api = mockk()
        repository = VehicleRepositoryImpl(api)
    }
    
    @Test
    fun `getVehicleStatus returns success when api succeeds`() = runTest {
        coEvery { api.getVehicleStatus() } returns Response.success(mockVehicleStatusDto())
        
        val result = repository.getVehicleStatus().toList()
        
        assertTrue(result.last() is Resource.Success)
    }
    
    @Test
    fun `getVehicleStatus returns error when api fails`() = runTest {
        coEvery { api.getVehicleStatus() } throws IOException("Network error")
        
        val result = repository.getVehicleStatus().toList()
        
        assertTrue(result.last() is Resource.Error)
    }
}

3. Test de UI con Compose (androidTest/presentation/dashboard/DashboardScreenTest.kt):

@HiltAndroidTest
class DashboardScreenTest {
    
    @get:Rule
    val composeTestRule = createComposeRule()
    
    @Test
    fun dashboardDisplaysGauges() {
        composeTestRule.setContent {
            BOOMAppTheme {
                DashboardScreen(
                    viewModel = mockDashboardViewModel(),
                    onNavigateToAlerts = {},
                    onNavigateToCosts = {}
                )
            }
        }
        
        composeTestRule.onNodeWithText("RPM").assertIsDisplayed()
        composeTestRule.onNodeWithText("km/h").assertIsDisplayed()
        composeTestRule.onNodeWithText("°C").assertIsDisplayed()
    }
    
    @Test
    fun alertsCardNavigatesToAlerts() {
        var navigated = false
        
        composeTestRule.setContent {
            BOOMAppTheme {
                DashboardScreen(
                    viewModel = mockDashboardViewModel(),
                    onNavigateToAlerts = { navigated = true },
                    onNavigateToCosts = {}
                )
            }
        }
        
        composeTestRule.onNodeWithText("Ver todas").performClick()
        assertTrue(navigated)
    }
}

4. Dependencias de test en build.gradle.kts:

testImplementation("junit:junit:4.13.2")
testImplementation("io.mockk:mockk:1.13.8")
testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3")
testImplementation("app.cash.turbine:turbine:1.0.0")

androidTestImplementation("androidx.compose.ui:ui-test-junit4")
androidTestImplementation("io.mockk:mockk-android:1.13.8")
debugImplementation("androidx.compose.ui:ui-test-manifest")
```

---

## 🚀 Orden de Ejecución Recomendado

1. **Prompt 1**: Configuración inicial del proyecto
2. **Prompt 2**: Estructura de carpetas
3. **Prompt 3**: Modelos de dominio
4. **Prompt 5**: Configuración Koin
5. **Prompt 6**: Cliente REST
6. **Prompt 4**: Implementación de repositorios
7. **Prompt 13**: Navegación básica
8. **Prompt 8**: Dashboard (pantalla principal)
9. **Prompt 9**: Pantalla Alertas
10. **Prompt 10**: Pantalla Predicciones
11. **Prompt 11**: Pantalla Costes
12. **Prompt 7**: Cliente MQTT (tiempo real)
13. **Prompt 12**: Notificaciones
14. **Prompt 14**: Testing

---

## 📝 Notas

- Cada prompt está diseñado para ser autocontenido
- Ajusta los prompts según el asistente de IA que uses
- Los prompts asumen conocimiento previo del contexto del proyecto
- Puedes combinar varios prompts en uno si el asistente lo permite
