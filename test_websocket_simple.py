import websocket
import json
import time

def on_message(ws, message):
    data = json.loads(message)
    msg_type = data.get('type', 'unknown')
    
    print(f"\n[{msg_type.upper()}]")
    
    if msg_type == 'initial':
        print("Estado inicial:")
        print(json.dumps(data['data'], indent=2))
    elif msg_type == 'obd':
        obd = data['data']
        print(f"RPM: {obd.get('rpm')} | Velocidad: {obd.get('speed')} km/h | Temp: {obd.get('coolant_temp')}°C")
    elif msg_type == 'sensors':
        sensors = data['data']
        print(f"Temp: {sensors.get('temperature')}°C | Presión: {sensors.get('pressure')} | Vibración: {sensors.get('vibration')}")

def on_error(ws, error):
    print(f"✗ Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("\n✗ Conexión cerrada")

def on_open(ws):
    print("✓ Conectado al WebSocket\n")

if __name__ == "__main__":
    print("=== TEST WEBSOCKET CLIENT (Simple) ===\n")
    
    url = "wss://boomap-production.up.railway.app/ws/vehicle"
    
    ws = websocket.WebSocketApp(
        url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    try:
        ws.run_forever()
    except KeyboardInterrupt:
        print("\n\n✓ Desconectado por el usuario")
        ws.close()
