from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json
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

# Clientes WebSocket activos
active_connections = []

# Inicializar suscriptor MQTT
mqtt_sub = MQTTSubscriber(
    broker="localhost",
    on_obd_data=lambda data: update_vehicle_state("obd", data),
    on_sensor_data=lambda data: update_vehicle_state("sensors", data)
)

def update_vehicle_state(data_type, data):
    vehicle_state[data_type] = data
    vehicle_state["last_update"] = datetime.now().isoformat()
    # Notificar a todos los clientes WebSocket
    broadcast_to_websockets({"type": data_type, "data": data})

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

@app.websocket("/ws/vehicle")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    print(f"✓ Cliente WebSocket conectado. Total: {len(active_connections)}")
    
    try:
        # Enviar estado actual al conectar
        await websocket.send_json({
            "type": "initial",
            "data": vehicle_state
        })
        
        # Mantener conexión abierta
        while True:
            data = await websocket.receive_text()
            # Procesar comandos del cliente si es necesario
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        print(f"✗ Cliente WebSocket desconectado. Total: {len(active_connections)}")
