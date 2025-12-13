#!/usr/bin/env python3
"""
Script para ejecutar el Cerebro Predictivo de BoomApp.
Se suscribe a MQTT, analiza datos de sensores y publica predicciones/alertas.
"""

import os
import sys
from dotenv import load_dotenv
from boomapp.predictive_brain import PredictiveEngine

def main():
    # Cargar variables de entorno desde .env
    load_dotenv()
    
    print("="*60)
    print("🧠 BOOMAPP - CEREBRO DE MANTENIMIENTO PREDICTIVO")
    print("="*60)
    
    # Leer configuración desde variables de entorno
    broker = os.getenv("MQTT_BROKER", "localhost")
    port = int(os.getenv("MQTT_PORT", "1883"))
    username = os.getenv("MQTT_USERNAME")
    password = os.getenv("MQTT_PASSWORD")
    use_tls = os.getenv("MQTT_USE_TLS", "false").lower() == "true"
    
    # Crear e iniciar motor predictivo
    engine = PredictiveEngine(
        broker=broker,
        port=port,
        username=username,
        password=password,
        use_tls=use_tls
    )
    
    if engine.connect():
        print("\n" + "="*60)
        print("🧠 CEREBRO PREDICTIVO ACTIVO")
        print("="*60)
        print(f"Broker: {broker}:{port}")
        print(f"TLS: {'Sí' if use_tls else 'No'}")
        print("-"*60)
        print("Topics de entrada:")
        print("  - boomapp/vehicle/obd")
        print("  - boomapp/vehicle/sensors")
        print("Topics de salida:")
        print("  - boomapp/predictions/wear")
        print("  - boomapp/predictions/alerts")
        print("="*60)
        print("\nEsperando datos de sensores...")
        print("(Presiona Ctrl+C para detener)\n")
        
        try:
            while engine.running:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n[PredictiveBrain] Deteniendo...")
            
            # Mostrar estadísticas finales
            stats = engine.get_stats()
            print("\n" + "="*40)
            print("📊 ESTADÍSTICAS DE SESIÓN")
            print("="*40)
            print(f"Mensajes OBD procesados: {stats['obd_messages_processed']}")
            print(f"Mensajes sensores procesados: {stats['sensor_messages_processed']}")
            print(f"Predicciones publicadas: {stats['predictions_published']}")
            print(f"Alertas publicadas: {stats['alerts_published']}")
            print(f"Tiempo activo: {stats['uptime_seconds']:.1f} segundos")
            print("="*40)
            
            engine.disconnect()
    else:
        print("\n✗ No se pudo conectar al broker MQTT")
        print("Verifica que el broker esté corriendo y las credenciales sean correctas.")
        sys.exit(1)

if __name__ == "__main__":
    main()
