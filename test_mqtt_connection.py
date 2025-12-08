import paho.mqtt.client as mqtt
import time

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✓ Conectado al broker (rc: {rc})")
        client.subscribe("boomapp/vehicle/#")
        print("✓ Suscrito a: boomapp/vehicle/#")
    else:
        print(f"✗ Error de conexión (rc: {rc})")

def on_message(client, userdata, msg):
    print(f"\n[{msg.topic}]")
    print(f"Payload: {msg.payload.decode()}")

def on_disconnect(client, userdata, rc):
    print(f"✗ Desconectado (rc: {rc})")

if __name__ == "__main__":
    broker = input("Broker MQTT (test.mosquitto.org): ").strip() or "test.mosquitto.org"
    
    print(f"\n=== TEST CONEXIÓN MQTT ===")
    print(f"Broker: {broker}")
    print(f"Topics: boomapp/vehicle/#\n")
    
    client = mqtt.Client(client_id="boomapp_test")
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    try:
        print("Conectando...")
        client.connect(broker, 1883, 60)
        print("Esperando mensajes... (Ctrl+C para salir)\n")
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n\nDesconectando...")
        client.disconnect()
    except Exception as e:
        print(f"✗ Error: {e}")
