import asyncio
import websockets
import json

async def test_websocket():
    uri = "wss://boomap-production.up.railway.app/ws/vehicle"
    
    print(f"Conectando a {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✓ Conectado al WebSocket\n")
            
            # Recibir mensajes
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                
                print(f"[{data.get('type', 'unknown')}]")
                
                if data['type'] == 'initial':
                    print("Estado inicial recibido:")
                    print(json.dumps(data['data'], indent=2))
                elif data['type'] == 'obd':
                    obd = data['data']
                    print(f"  RPM: {obd.get('rpm', 'N/A')}")
                    print(f"  Velocidad: {obd.get('speed', 'N/A')} km/h")
                    print(f"  Temp Motor: {obd.get('coolant_temp', 'N/A')}°C")
                    print(f"  Acelerador: {obd.get('throttle', 'N/A')}%")
                    print(f"  Combustible: {obd.get('fuel_level', 'N/A')}%")
                elif data['type'] == 'sensors':
                    sensors = data['data']
                    print(f"  Temperatura: {sensors.get('temperature', 'N/A')}°C")
                    print(f"  Presión: {sensors.get('pressure', 'N/A')} kPa")
                    print(f"  Humedad: {sensors.get('humidity', 'N/A')}%")
                    print(f"  Vibración: {sensors.get('vibration', 'N/A')}")
                
                print()
                
    except websockets.exceptions.ConnectionClosed:
        print("✗ Conexión cerrada")
    except KeyboardInterrupt:
        print("\n\n✓ Desconectado por el usuario")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    print("=== TEST WEBSOCKET CLIENT ===\n")
    print("Presiona Ctrl+C para salir\n")
    asyncio.run(test_websocket())
