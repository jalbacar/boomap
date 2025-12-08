"""
Script rápido para verificar publicación MQTT
Ejecutar MIENTRAS el simulador está corriendo
"""
import paho.mqtt.client as mqtt
import time

messages_received = []

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✓ Conectado a test.mosquitto.org")
        client.subscribe("boomapp/vehicle/#")
        print("✓ Esperando mensajes en boomapp/vehicle/#...\n")
    else:
        print(f"✗ Error conexión: {rc}")

def on_message(client, userdata, msg):
    messages_received.append(msg.topic)
    print(f"✓ Mensaje recibido: {msg.topic}")
    print(f"  Datos: {msg.payload.decode()[:100]}...\n")

client = mqtt.Client(client_id="quick_test")
client.on_connect = on_connect
client.on_message = on_message

try:
    print("Conectando a test.mosquitto.org...")
    client.connect("test.mosquitto.org", 1883, 60)
    client.loop_start()
    
    print("Escuchando por 15 segundos...\n")
    time.sleep(15)
    
    client.loop_stop()
    client.disconnect()
    
    print("\n" + "="*50)
    if messages_received:
        print(f"✓ ÉXITO: Recibidos {len(messages_received)} mensajes")
        print(f"Topics: {set(messages_received)}")
    else:
        print("✗ PROBLEMA: No se recibieron mensajes")
        print("\nPosibles causas:")
        print("1. El simulador no está corriendo")
        print("2. El simulador no tiene MQTT activado")
        print("3. El simulador usa otro broker")
        print("4. Firewall bloqueando puerto 1883")
    print("="*50)
    
except Exception as e:
    print(f"✗ Error: {e}")
