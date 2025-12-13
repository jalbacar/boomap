from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json
import os
from .mqtt_subscriber import MQTTSubscriber
from .models import VehicleStatus, OBDData, SensorData

app = FastAPI(title="BoomApp Backend API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Estado global del vehículo
vehicle_state = {
    "obd": {},
    "sensors": {},
    "last_update": None
}

# Estado de predicciones del cerebro predictivo
predictions_state = {
    "wear_state": {},
    "alert_summary": {},
    "active_alerts": [],
    "last_update": None
}

# Estado de pronósticos futuros
forecasts_state = {
    "component_forecasts": {},
    "all_predictions": [],
    "summary": {},
    "cost_estimate": {},
    "last_update": None
}

# Clientes WebSocket activos
active_connections = []

# Inicializar suscriptor MQTT
mqtt_sub = MQTTSubscriber(
    broker=os.getenv("MQTT_BROKER", "localhost"),
    port=int(os.getenv("MQTT_PORT", "1883")),
    on_obd_data=lambda data: update_vehicle_state("obd", data),
    on_sensor_data=lambda data: update_vehicle_state("sensors", data),
    on_prediction_data=lambda data: update_predictions_state(data),
    on_alert_data=lambda data: handle_new_alert(data)
)

def update_vehicle_state(data_type, data):
    vehicle_state[data_type] = data
    vehicle_state["last_update"] = datetime.now().isoformat()
    # Notificar a todos los clientes WebSocket
    broadcast_to_websockets({"type": data_type, "data": data})

def update_predictions_state(data):
    # Detectar si es un pronóstico futuro o predicción de desgaste
    if data.get("type") == "future_forecast":
        update_forecasts_state(data)
        return
    
    predictions_state["wear_state"] = data.get("wear_state", {})
    predictions_state["alert_summary"] = data.get("alert_summary", {})
    predictions_state["active_alerts"] = data.get("active_alerts", [])
    predictions_state["last_update"] = datetime.now().isoformat()
    # Notificar a clientes WebSocket
    broadcast_to_websockets({"type": "predictions", "data": predictions_state})

def update_forecasts_state(data):
    """Actualiza estado de pronósticos futuros"""
    forecasts_state["component_forecasts"] = data.get("component_forecasts", {})
    forecasts_state["all_predictions"] = data.get("all_predictions", [])
    forecasts_state["summary"] = data.get("summary", {})
    forecasts_state["cost_estimate"] = data.get("cost_estimate", {})
    forecasts_state["overall_health"] = data.get("overall_health", 100)
    forecasts_state["last_update"] = datetime.now().isoformat()
    # Notificar a clientes WebSocket
    broadcast_to_websockets({"type": "forecast", "data": forecasts_state})

def handle_new_alert(alert_data):
    # Añadir alerta a la lista si no existe
    alert_id = alert_data.get("id")
    existing_ids = [a.get("id") for a in predictions_state["active_alerts"]]
    if alert_id and alert_id not in existing_ids:
        predictions_state["active_alerts"].append(alert_data)
    # Notificar inmediatamente a clientes WebSocket
    broadcast_to_websockets({"type": "alert", "data": alert_data})

def broadcast_to_websockets(message):
    for connection in active_connections[:]:
        try:
            connection.send_text(json.dumps(message))
        except:
            active_connections.remove(connection)

@app.on_event("startup")
async def startup_event():
    mqtt_sub.connect()
    print("✓ Backend API iniciado")

@app.on_event("shutdown")
async def shutdown_event():
    mqtt_sub.disconnect()

@app.get("/")
def root():
    return {"message": "BoomApp Backend API", "version": "1.0.0"}

@app.get("/api/debug/mqtt")
def debug_mqtt():
    return {
        "broker": mqtt_sub.broker,
        "port": mqtt_sub.port,
        "connected": mqtt_sub.connected,
        "vehicle_state": vehicle_state
    }

@app.get("/api/vehicle/status")
def get_vehicle_status():
    return {
        "obd": vehicle_state.get("obd", {}),
        "sensors": vehicle_state.get("sensors", {}),
        "last_update": vehicle_state.get("last_update"),
        "status": "online" if vehicle_state.get("last_update") else "offline"
    }

@app.get("/api/vehicle/obd")
def get_obd_data():
    return vehicle_state.get("obd", {})

@app.get("/api/vehicle/sensors")
def get_sensor_data():
    return vehicle_state.get("sensors", {})

# ============== ENDPOINTS DE PREDICCIONES ==============

@app.get("/api/predictions/status")
def get_predictions_status():
    """Estado completo de predicciones y desgaste"""
    return {
        "wear_state": predictions_state.get("wear_state", {}),
        "alert_summary": predictions_state.get("alert_summary", {}),
        "last_update": predictions_state.get("last_update"),
        "status": "online" if predictions_state.get("last_update") else "offline"
    }

@app.get("/api/predictions/wear")
def get_wear_state():
    """Estado de desgaste de componentes"""
    return predictions_state.get("wear_state", {})

@app.get("/api/predictions/alerts")
def get_active_alerts():
    """Alertas activas del sistema"""
    return {
        "alerts": predictions_state.get("active_alerts", []),
        "summary": predictions_state.get("alert_summary", {})
    }

@app.get("/api/predictions/component/{component_name}")
def get_component_wear(component_name: str):
    """Estado de desgaste de un componente específico"""
    wear_state = predictions_state.get("wear_state", {})
    components = wear_state.get("components", {})
    
    if component_name in components:
        return {
            "component": component_name,
            "data": components[component_name],
            "overall_health": wear_state.get("overall_health", 100)
        }
    return {"error": f"Componente '{component_name}' no encontrado"}

# ============== ENDPOINTS DE PRONÓSTICOS FUTUROS ==============

@app.get("/api/forecasts/status")
def get_forecasts_status():
    """Estado completo de pronósticos futuros"""
    return {
        "component_forecasts": forecasts_state.get("component_forecasts", {}),
        "summary": forecasts_state.get("summary", {}),
        "overall_health": forecasts_state.get("overall_health", 100),
        "last_update": forecasts_state.get("last_update"),
        "status": "online" if forecasts_state.get("last_update") else "offline"
    }

@app.get("/api/forecasts/predictions")
def get_future_predictions():
    """Todas las predicciones de problemas futuros"""
    predictions = forecasts_state.get("all_predictions", [])
    
    # Separar por nivel de riesgo
    by_risk = {"critical": [], "high": [], "moderate": [], "low": []}
    for pred in predictions:
        risk = pred.get("risk_level", "low")
        if risk in by_risk:
            by_risk[risk].append(pred)
    
    return {
        "total": len(predictions),
        "by_risk_level": by_risk,
        "all_predictions": predictions,
        "last_update": forecasts_state.get("last_update")
    }

@app.get("/api/forecasts/component/{component_name}")
def get_component_forecast(component_name: str):
    """Pronóstico futuro de un componente específico"""
    forecasts = forecasts_state.get("component_forecasts", {})
    
    if component_name in forecasts:
        forecast = forecasts[component_name]
        return {
            "component": component_name,
            "current_health": forecast.get("current_health", 100),
            "forecast": forecast.get("forecast", {}),
            "estimated_remaining_life_hours": forecast.get("estimated_remaining_life_hours", 0),
            "trend": forecast.get("trend", "stable"),
            "risk_factors": forecast.get("risk_factors", []),
            "predictions": forecast.get("predictions", [])
        }
    
    valid_components = list(forecasts.keys())
    return {
        "error": f"Componente '{component_name}' no encontrado",
        "valid_components": valid_components
    }

@app.get("/api/forecasts/high-risk")
def get_high_risk_predictions():
    """Predicciones de alto riesgo que requieren atención"""
    predictions = forecasts_state.get("all_predictions", [])
    
    high_risk = [
        p for p in predictions 
        if p.get("risk_level") in ["critical", "high"]
    ]
    
    # Ordenar por tiempo estimado hasta fallo
    high_risk.sort(
        key=lambda x: x.get("estimated_time_to_failure_hours") or float('inf')
    )
    
    return {
        "count": len(high_risk),
        "predictions": high_risk,
        "requires_immediate_attention": len([p for p in high_risk if p.get("risk_level") == "critical"]) > 0
    }

@app.get("/api/forecasts/recommendations")
def get_maintenance_recommendations():
    """Recomendaciones de mantenimiento basadas en pronósticos"""
    forecasts = forecasts_state.get("component_forecasts", {})
    predictions = forecasts_state.get("all_predictions", [])
    
    recommendations = []
    
    for comp_name, forecast in forecasts.items():
        remaining_life = forecast.get("estimated_remaining_life_hours", 999)
        health = forecast.get("current_health", 100)
        trend = forecast.get("trend", "stable")
        risk_factors = forecast.get("risk_factors", [])
        
        # Generar recomendación basada en estado
        urgency = "low"
        if remaining_life < 10 or health < 30:
            urgency = "critical"
        elif remaining_life < 50 or health < 50:
            urgency = "high"
        elif remaining_life < 100 or health < 70:
            urgency = "moderate"
        
        if urgency != "low" or risk_factors:
            recommendations.append({
                "component": comp_name,
                "urgency": urgency,
                "current_health": health,
                "estimated_remaining_life_hours": remaining_life,
                "trend": trend,
                "risk_factors": risk_factors,
                "action": _get_recommended_action(comp_name, urgency, trend)
            })
    
    # Añadir recomendaciones de predicciones específicas
    for pred in predictions:
        if pred.get("recommendation"):
            recommendations.append({
                "component": pred.get("component"),
                "urgency": pred.get("risk_level"),
                "problem_type": pred.get("problem_type"),
                "description": pred.get("description"),
                "action": pred.get("recommendation"),
                "estimated_time_hours": pred.get("estimated_time_to_failure_hours")
            })
    
    # Ordenar por urgencia
    urgency_order = {"critical": 0, "high": 1, "moderate": 2, "low": 3}
    recommendations.sort(key=lambda x: urgency_order.get(x.get("urgency", "low"), 4))
    
    return {
        "total_recommendations": len(recommendations),
        "recommendations": recommendations,
        "last_update": forecasts_state.get("last_update")
    }

def _get_recommended_action(component: str, urgency: str, trend: str) -> str:
    """Genera acción recomendada basada en componente y urgencia"""
    actions = {
        "engine": {
            "critical": "Detener vehículo y solicitar asistencia. No continuar conduciendo.",
            "high": "Programar revisión urgente del motor en las próximas 24-48 horas.",
            "moderate": "Agendar cita de servicio para revisión del motor esta semana."
        },
        "brakes": {
            "critical": "¡PELIGRO! No conducir. Revisar frenos inmediatamente.",
            "high": "Revisar sistema de frenos urgentemente. Evitar conducción prolongada.",
            "moderate": "Inspeccionar pastillas y discos de freno pronto."
        },
        "transmission": {
            "critical": "Evitar conducir. Posible fallo de transmisión inminente.",
            "high": "Revisar transmisión. Evitar aceleraciones bruscas.",
            "moderate": "Programar revisión de transmisión y cambio de aceite."
        },
        "tires": {
            "critical": "Revisar neumáticos inmediatamente. Posible riesgo de reventón.",
            "high": "Verificar presión y estado de neumáticos urgentemente.",
            "moderate": "Rotar neumáticos y verificar alineación."
        },
        "battery": {
            "critical": "Batería en estado crítico. Reemplazar antes de próximo uso.",
            "high": "Verificar carga y estado de batería. Considerar reemplazo.",
            "moderate": "Revisar conexiones de batería y nivel de carga."
        }
    }
    
    component_actions = actions.get(component, {})
    return component_actions.get(urgency, f"Revisar {component} según urgencia: {urgency}")

# ============== ENDPOINTS DE COSTES ==============

@app.get("/api/costs/estimate")
def get_cost_estimate():
    """Estimación de costes de reparación basada en predicciones"""
    cost_estimate = forecasts_state.get("cost_estimate", {})
    
    return {
        "total_estimated": cost_estimate.get("total_estimated", {"min": 0, "max": 0, "average": 0}),
        "potential_savings": cost_estimate.get("potential_savings_if_preventive", 0),
        "repair_count": cost_estimate.get("repair_count", 0),
        "repairs": cost_estimate.get("repairs", []),
        "currency": "EUR",
        "last_update": forecasts_state.get("last_update")
    }

@app.get("/api/costs/by-component/{component_name}")
def get_component_cost(component_name: str):
    """Coste estimado de reparación para un componente específico"""
    cost_estimate = forecasts_state.get("cost_estimate", {})
    repairs = cost_estimate.get("repairs", [])
    
    component_repairs = [r for r in repairs if r.get("component") == component_name]
    
    if component_repairs:
        total_min = sum(r.get("cost_range", {}).get("min", 0) for r in component_repairs)
        total_max = sum(r.get("cost_range", {}).get("max", 0) for r in component_repairs)
        total_avg = sum(r.get("cost_range", {}).get("average", 0) for r in component_repairs)
        
        return {
            "component": component_name,
            "total_estimated": {
                "min": round(total_min, 2),
                "max": round(total_max, 2),
                "average": round(total_avg, 2)
            },
            "repairs": component_repairs,
            "currency": "EUR"
        }
    
    return {
        "component": component_name,
        "total_estimated": {"min": 0, "max": 0, "average": 0},
        "repairs": [],
        "message": "Sin reparaciones estimadas para este componente",
        "currency": "EUR"
    }

@app.get("/api/costs/by-urgency")
def get_costs_by_urgency():
    """Costes agrupados por nivel de urgencia"""
    cost_estimate = forecasts_state.get("cost_estimate", {})
    repairs = cost_estimate.get("repairs", [])
    
    by_urgency = {
        "critical": {"repairs": [], "total": 0},
        "urgent": {"repairs": [], "total": 0},
        "recommended": {"repairs": [], "total": 0},
        "preventive": {"repairs": [], "total": 0}
    }
    
    for repair in repairs:
        urgency = repair.get("urgency", "recommended")
        if urgency in by_urgency:
            by_urgency[urgency]["repairs"].append(repair)
            by_urgency[urgency]["total"] += repair.get("cost_range", {}).get("average", 0)
    
    # Redondear totales
    for urgency in by_urgency:
        by_urgency[urgency]["total"] = round(by_urgency[urgency]["total"], 2)
        by_urgency[urgency]["count"] = len(by_urgency[urgency]["repairs"])
    
    return {
        "by_urgency": by_urgency,
        "currency": "EUR",
        "last_update": forecasts_state.get("last_update")
    }

@app.get("/api/costs/savings")
def get_potential_savings():
    """Ahorro potencial si se realiza mantenimiento preventivo"""
    cost_estimate = forecasts_state.get("cost_estimate", {})
    repairs = cost_estimate.get("repairs", [])
    
    savings_details = []
    total_savings = 0
    
    for repair in repairs:
        savings = repair.get("savings_if_preventive", 0)
        if savings > 0:
            savings_details.append({
                "component": repair.get("component"),
                "repair_type": repair.get("repair_type"),
                "current_cost": repair.get("cost_range", {}).get("average", 0),
                "potential_savings": savings,
                "description": repair.get("description")
            })
            total_savings += savings
    
    return {
        "total_potential_savings": round(total_savings, 2),
        "savings_details": savings_details,
        "recommendation": "Realizar mantenimiento preventivo puede ahorrar significativamente en reparaciones mayores",
        "currency": "EUR"
    }

@app.get("/api/costs/summary")
def get_cost_summary():
    """Resumen completo de costes con predicciones y recomendaciones"""
    cost_estimate = forecasts_state.get("cost_estimate", {})
    forecasts = forecasts_state.get("component_forecasts", {})
    
    summary = {
        "total_estimated": cost_estimate.get("total_estimated", {"min": 0, "max": 0, "average": 0}),
        "potential_savings": cost_estimate.get("potential_savings_if_preventive", 0),
        "repair_count": cost_estimate.get("repair_count", 0),
        "overall_health": forecasts_state.get("overall_health", 100),
        "components_at_risk": [],
        "immediate_action_required": False,
        "currency": "EUR",
        "last_update": forecasts_state.get("last_update")
    }
    
    # Identificar componentes en riesgo
    for comp_name, forecast in forecasts.items():
        health = forecast.get("current_health", 100)
        if health < 70:
            summary["components_at_risk"].append({
                "component": comp_name,
                "health": health,
                "trend": forecast.get("trend", "stable")
            })
            if health < 30:
                summary["immediate_action_required"] = True
    
    return summary

@app.websocket("/ws/vehicle")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    print(f"✓ Cliente WebSocket conectado. Total: {len(active_connections)}")
    
    try:
        # Enviar estado actual al conectar (vehículo + predicciones + pronósticos)
        await websocket.send_json({
            "type": "initial",
            "data": {
                "vehicle": vehicle_state,
                "predictions": predictions_state,
                "forecasts": forecasts_state
            }
        })
        
        # Mantener conexión abierta
        while True:
            data = await websocket.receive_text()
            # Procesar comandos del cliente si es necesario
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        print(f"✗ Cliente WebSocket desconectado. Total: {len(active_connections)}")
