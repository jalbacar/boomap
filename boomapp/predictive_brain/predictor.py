"""
Motor principal del cerebro predictivo.
Se suscribe a MQTT, procesa datos y publica predicciones/alertas.
"""

import json
import time
import threading
from typing import Dict, Optional, Callable, List
import paho.mqtt.client as mqtt

from .config import TOPICS
from .wear_models import WearAnalyzer
from .alert_manager import AlertManager, Alert
from .future_predictor import FuturePredictor
from .cost_estimator import CostEstimator


class PredictiveEngine:
    """
    Motor de mantenimiento predictivo.
    - Se suscribe a topics MQTT de sensores
    - Analiza datos y calcula desgaste
    - Publica predicciones y alertas a MQTT
    """
    
    def __init__(self, broker: str = "localhost", port: int = 1883,
                 username: str = None, password: str = None, use_tls: bool = False):
        self.broker = broker
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        
        # Cliente MQTT
        self.client = mqtt.Client(client_id="boomapp_predictive_brain")
        self.connected = False
        self.running = False
        
        # Configurar autenticación
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
        
        # Configurar TLS
        if self.use_tls:
            self.client.tls_set()
        
        # Callbacks MQTT
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        # Componentes de análisis
        self.wear_analyzer = WearAnalyzer()
        self.alert_manager = AlertManager()
        self.future_predictor = FuturePredictor()
        self.cost_estimator = CostEstimator()
        
        # Configurar callback de alertas
        self.alert_manager.on_new_alert = self._on_new_alert
        
        # Callbacks externos
        self.on_prediction: Optional[Callable[[Dict], None]] = None
        self.on_alert: Optional[Callable[[Dict], None]] = None
        
        # Control de publicación
        self.last_prediction_publish = 0
        self.prediction_publish_interval = 5  # segundos
        self.last_forecast_publish = 0
        self.forecast_publish_interval = 15  # segundos (predicciones futuras menos frecuentes)
        
        # Estadísticas
        self.stats = {
            "obd_messages_processed": 0,
            "sensor_messages_processed": 0,
            "predictions_published": 0,
            "alerts_published": 0,
            "forecasts_published": 0,
            "start_time": None
        }
    
    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            print(f"✓ [PredictiveBrain] Conectado a MQTT: {self.broker}:{self.port}")
            
            # Suscribirse a topics de entrada
            self.client.subscribe(TOPICS["obd_input"])
            self.client.subscribe(TOPICS["sensors_input"])
            print(f"✓ [PredictiveBrain] Suscrito a: {TOPICS['obd_input']}")
            print(f"✓ [PredictiveBrain] Suscrito a: {TOPICS['sensors_input']}")
        else:
            print(f"✗ [PredictiveBrain] Error de conexión MQTT: código {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        self.connected = False
        print(f"✗ [PredictiveBrain] Desconectado de MQTT")
    
    def _on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            topic = msg.topic
            
            if topic == TOPICS["obd_input"]:
                self._process_obd_data(payload)
            elif topic == TOPICS["sensors_input"]:
                self._process_sensor_data(payload)
                
        except json.JSONDecodeError as e:
            print(f"✗ [PredictiveBrain] Error decodificando JSON: {e}")
        except Exception as e:
            print(f"✗ [PredictiveBrain] Error procesando mensaje: {e}")
    
    def _process_obd_data(self, obd_data: Dict) -> None:
        """Procesa datos OBD recibidos"""
        self.stats["obd_messages_processed"] += 1
        
        # Actualizar modelo de desgaste
        self.wear_analyzer.process_obd_data(obd_data)
        
        # Registrar en predictor de futuro para análisis de tendencias
        self.future_predictor.record_obd_data(obd_data)
        
        # Evaluar alertas inmediatas
        alerts = self.alert_manager.evaluate_obd_data(obd_data)
        for alert in alerts:
            self._publish_alert(alert)
        
        # Publicar predicciones periódicamente
        self._maybe_publish_predictions()
        
        # Publicar pronósticos futuros periódicamente
        self._maybe_publish_forecasts()
    
    def _process_sensor_data(self, sensor_data: Dict) -> None:
        """Procesa datos de sensores recibidos"""
        self.stats["sensor_messages_processed"] += 1
        
        # Actualizar modelo de desgaste
        self.wear_analyzer.process_sensor_data(sensor_data)
        
        # Registrar en predictor de futuro para análisis de tendencias
        self.future_predictor.record_sensor_data(sensor_data)
        
        # Evaluar alertas inmediatas
        alerts = self.alert_manager.evaluate_sensor_data(sensor_data)
        for alert in alerts:
            self._publish_alert(alert)
    
    def _on_new_alert(self, alert: Alert) -> None:
        """Callback cuando se genera una nueva alerta"""
        self._publish_alert(alert)
    
    def _publish_alert(self, alert: Alert) -> None:
        """Publica una alerta a MQTT"""
        if not self.connected:
            return
        
        alert_data = alert.to_dict()
        payload = json.dumps(alert_data)
        
        self.client.publish(TOPICS["alerts_output"], payload, qos=1)
        self.stats["alerts_published"] += 1
        
        level_emoji = {
            "info": "ℹ️",
            "warning": "⚠️",
            "critical": "🔴",
            "emergency": "🚨"
        }
        emoji = level_emoji.get(alert.level.value, "📢")
        print(f"{emoji} [ALERTA] {alert.level.value.upper()}: {alert.message}")
        
        if self.on_alert:
            self.on_alert(alert_data)
    
    def _maybe_publish_predictions(self) -> None:
        """Publica predicciones si ha pasado el intervalo"""
        current_time = time.time()
        
        if current_time - self.last_prediction_publish >= self.prediction_publish_interval:
            self._publish_predictions()
            self.last_prediction_publish = current_time
    
    def _publish_predictions(self) -> None:
        """Publica estado de desgaste y predicciones"""
        if not self.connected:
            return
        
        # Obtener estado de desgaste
        wear_state = self.wear_analyzer.get_wear_state()
        
        # Evaluar alertas de desgaste
        wear_alerts = self.alert_manager.evaluate_wear_state(wear_state)
        for alert in wear_alerts:
            self._publish_alert(alert)
        
        # Construir payload de predicción
        prediction_data = {
            "timestamp": time.time(),
            "wear_state": wear_state,
            "alert_summary": self.alert_manager.get_alert_summary(),
            "active_alerts": self.alert_manager.get_active_alerts(),
            "stats": {
                "runtime_hours": wear_state.get("runtime_hours", 0),
                "overall_health": wear_state.get("overall_health", 100)
            }
        }
        
        payload = json.dumps(prediction_data)
        self.client.publish(TOPICS["predictions_output"], payload, qos=1)
        self.stats["predictions_published"] += 1
        
        print(f"📊 [PREDICCIÓN] Salud general: {wear_state.get('overall_health', 100):.1f}%")
        
        if self.on_prediction:
            self.on_prediction(prediction_data)
    
    def _maybe_publish_forecasts(self) -> None:
        """Publica pronósticos futuros si ha pasado el intervalo"""
        current_time = time.time()
        
        if current_time - self.last_forecast_publish >= self.forecast_publish_interval:
            self._publish_forecasts()
            self.last_forecast_publish = current_time
    
    def _publish_forecasts(self) -> None:
        """Publica pronósticos de problemas futuros"""
        if not self.connected:
            return
        
        # Obtener estado de desgaste actual para cada componente
        wear_state = self.wear_analyzer.get_wear_state()
        components = wear_state.get("components", {})
        
        # Generar pronósticos por componente
        forecasts = {}
        all_future_predictions = []
        
        for comp_name, comp_data in components.items():
            health = comp_data.get("health_score", 100)
            forecast = self.future_predictor.get_component_forecast(comp_name, health)
            forecasts[comp_name] = forecast.to_dict()
            all_future_predictions.extend(forecast.predictions)
        
        # Obtener resumen de predicciones
        prediction_summary = self.future_predictor.get_summary()
        
        # Construir payload de pronóstico
        forecast_data = {
            "timestamp": time.time(),
            "type": "future_forecast",
            "component_forecasts": forecasts,
            "all_predictions": [p.to_dict() for p in all_future_predictions],
            "summary": prediction_summary,
            "overall_health": wear_state.get("overall_health", 100)
        }
        
        # Calcular costes estimados
        predictions_dicts = [p.to_dict() for p in all_future_predictions]
        cost_summary = self.cost_estimator.estimate_from_predictions(predictions_dicts)
        
        # Añadir costes al payload
        forecast_data["cost_estimate"] = cost_summary.to_dict()
        
        # Publicar a topic de predicciones (con costes incluidos)
        payload = json.dumps(forecast_data)
        self.client.publish(TOPICS["predictions_output"], payload, qos=1)
        self.stats["forecasts_published"] += 1
        
        # Mostrar predicciones importantes
        high_risk = [p for p in all_future_predictions if p.risk_level.value in ["critical", "high"]]
        if high_risk:
            print(f"🔮 [PRONÓSTICO] {len(high_risk)} predicciones de riesgo alto/crítico detectadas:")
            for pred in high_risk[:3]:
                time_str = f"~{pred.estimated_time_to_failure:.0f}h" if pred.estimated_time_to_failure else "indeterminado"
                print(f"   ⚠️ {pred.component}: {pred.problem_type} - Tiempo estimado: {time_str}")
        else:
            print(f"🔮 [PRONÓSTICO] Sin predicciones de alto riesgo. {len(all_future_predictions)} predicciones totales.")
        
        # Mostrar costes estimados
        if cost_summary.total_avg > 0:
            print(f"💰 [COSTE ESTIMADO] {cost_summary.total_avg:.2f}€ (rango: {cost_summary.total_min:.2f}€ - {cost_summary.total_max:.2f}€)")
            if cost_summary.potential_savings > 0:
                print(f"   💡 Ahorro potencial con mantenimiento preventivo: {cost_summary.potential_savings:.2f}€")
    
    def connect(self) -> bool:
        """Conecta al broker MQTT"""
        try:
            tls_str = " (TLS)" if self.use_tls else ""
            auth_str = f" como {self.username}" if self.username else ""
            print(f"[PredictiveBrain] Conectando a {self.broker}:{self.port}{tls_str}{auth_str}...")
            
            self.client.connect(self.broker, self.port, 60)
            self.running = True
            self.stats["start_time"] = time.time()
            
            # Iniciar loop en thread separado
            threading.Thread(target=self.client.loop_forever, daemon=True).start()
            
            # Esperar conexión
            timeout = 10
            start = time.time()
            while not self.connected and (time.time() - start) < timeout:
                time.sleep(0.1)
            
            return self.connected
            
        except Exception as e:
            print(f"✗ [PredictiveBrain] Error conectando: {e}")
            return False
    
    def disconnect(self) -> None:
        """Desconecta del broker MQTT"""
        self.running = False
        self.client.disconnect()
        print("[PredictiveBrain] Desconectado")
    
    def get_current_predictions(self) -> Dict:
        """Retorna predicciones actuales sin publicar"""
        wear_state = self.wear_analyzer.get_wear_state()
        return {
            "timestamp": time.time(),
            "wear_state": wear_state,
            "alert_summary": self.alert_manager.get_alert_summary(),
            "active_alerts": self.alert_manager.get_active_alerts()
        }
    
    def get_future_forecasts(self) -> Dict:
        """Retorna pronósticos futuros sin publicar"""
        wear_state = self.wear_analyzer.get_wear_state()
        components = wear_state.get("components", {})
        
        forecasts = {}
        all_predictions = []
        
        for comp_name, comp_data in components.items():
            health = comp_data.get("health_score", 100)
            forecast = self.future_predictor.get_component_forecast(comp_name, health)
            forecasts[comp_name] = forecast.to_dict()
            all_predictions.extend([p.to_dict() for p in forecast.predictions])
        
        return {
            "timestamp": time.time(),
            "component_forecasts": forecasts,
            "all_predictions": all_predictions,
            "summary": self.future_predictor.get_summary()
        }
    
    def get_stats(self) -> Dict:
        """Retorna estadísticas del motor"""
        uptime = 0
        if self.stats["start_time"]:
            uptime = time.time() - self.stats["start_time"]
        
        return {
            **self.stats,
            "uptime_seconds": uptime,
            "connected": self.connected
        }
    
    def reset_component_maintenance(self, component: str) -> bool:
        """Resetea el mantenimiento de un componente"""
        try:
            self.wear_analyzer.reset_maintenance(component)
            print(f"✓ [PredictiveBrain] Mantenimiento de {component} reseteado")
            return True
        except Exception as e:
            print(f"✗ [PredictiveBrain] Error reseteando mantenimiento: {e}")
            return False


def run_predictive_engine(broker: str = "localhost", port: int = 1883,
                          username: str = None, password: str = None,
                          use_tls: bool = False) -> None:
    """Función de conveniencia para ejecutar el motor predictivo"""
    engine = PredictiveEngine(
        broker=broker,
        port=port,
        username=username,
        password=password,
        use_tls=use_tls
    )
    
    if engine.connect():
        print("\n" + "="*50)
        print("🧠 CEREBRO PREDICTIVO ACTIVO")
        print("="*50)
        print(f"Broker: {broker}:{port}")
        print(f"Suscrito a: {TOPICS['obd_input']}, {TOPICS['sensors_input']}")
        print(f"Publicando en: {TOPICS['predictions_output']}, {TOPICS['alerts_output']}")
        print("="*50 + "\n")
        
        try:
            while engine.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[PredictiveBrain] Deteniendo...")
            engine.disconnect()
    else:
        print("✗ No se pudo conectar al broker MQTT")
