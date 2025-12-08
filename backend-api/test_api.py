import requests
import json

BASE_URL = "http://localhost:8000"

def test_root():
    response = requests.get(f"{BASE_URL}/")
    print("GET /")
    print(json.dumps(response.json(), indent=2))
    print()

def test_vehicle_status():
    response = requests.get(f"{BASE_URL}/api/vehicle/status")
    print("GET /api/vehicle/status")
    print(json.dumps(response.json(), indent=2))
    print()

def test_obd():
    response = requests.get(f"{BASE_URL}/api/vehicle/obd")
    print("GET /api/vehicle/obd")
    print(json.dumps(response.json(), indent=2))
    print()

def test_sensors():
    response = requests.get(f"{BASE_URL}/api/vehicle/sensors")
    print("GET /api/vehicle/sensors")
    print(json.dumps(response.json(), indent=2))
    print()

if __name__ == "__main__":
    print("=== TEST BACKEND API ===\n")
    try:
        test_root()
        test_vehicle_status()
        test_obd()
        test_sensors()
        print("✓ Todos los tests completados")
    except Exception as e:
        print(f"✗ Error: {e}")
