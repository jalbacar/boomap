import paho.mqtt.client as mqtt
import json

def on_connect(client, userdata, flags, rc):
    print(f"✓ Conectado al broker MQTT (rc: {rc})")
    client.subscribe("boomapp/vehicle/#")
    print("✓ Suscrito a: boomapp/vehicle/#")

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        print(f"\n[{msg.topic}]")
        for key, value in data.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.2f}")
            else:
                print(f"  {key}: {value}")
    except:
        print(f"[{msg.topic}] {msg.payload.decode()}")

if __name__ == "__main__":
    print("=== CLIENTE MQTT DE PRUEBA ===\n")
    broker = input("Broker (localhost): ").strip() or "localhost"
    
    client = mqtt.Client(client_id="boomapp_test_client")
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect(broker, 1883, 60)
        print(f"\nEscuchando mensajes de BoomApp...\n")
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n\nDesconectando...")
        client.disconnect()
    except Exception as e:
        print(f"Error: {e}")
