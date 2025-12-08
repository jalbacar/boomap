#!/bin/bash
BASE_URL="https://boomap-production.up.railway.app"

echo "1. Info API:"
curl $BASE_URL/
echo -e "\n"

echo "2. Debug MQTT:"
curl $BASE_URL/api/debug/mqtt
echo -e "\n"

echo "3. Vehicle Status:"
curl $BASE_URL/api/vehicle/status
echo -e "\n"

echo "4. OBD Data:"
curl $BASE_URL/api/vehicle/obd
echo -e "\n"

echo "5. Sensor Data:"
curl $BASE_URL/api/vehicle/sensors
echo -e "\n"
