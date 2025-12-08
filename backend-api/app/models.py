from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class OBDData(BaseModel):
    rpm: float
    speed: float
    coolant_temp: float
    throttle: float
    fuel_level: float

class SensorData(BaseModel):
    temperature: float
    pressure: float
    humidity: float
    vibration: float

class VehicleStatus(BaseModel):
    obd: Optional[OBDData] = None
    sensors: Optional[SensorData] = None
    last_update: Optional[str] = None
    status: str
