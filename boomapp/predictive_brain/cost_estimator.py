"""
Estimador de costes de reparación vehicular.
Calcula el coste estimado de reparaciones basado en alertas y predicciones.
Precios basados en talleres de precio medio en España.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
import time


class RepairUrgency(Enum):
    """Urgencia de la reparación"""
    PREVENTIVE = "preventive"      # Mantenimiento preventivo
    RECOMMENDED = "recommended"    # Recomendado pronto
    URGENT = "urgent"              # Urgente
    CRITICAL = "critical"          # Crítico/Inmediato


@dataclass
class RepairCost:
    """Coste estimado de una reparación"""
    component: str
    repair_type: str
    description: str
    min_cost: float
    max_cost: float
    avg_cost: float
    labor_hours: float
    parts_cost: float
    labor_cost: float
    urgency: RepairUrgency
    savings_if_preventive: float = 0.0  # Ahorro si se actúa preventivamente
    
    def to_dict(self) -> dict:
        return {
            "component": self.component,
            "repair_type": self.repair_type,
            "description": self.description,
            "cost_range": {
                "min": self.min_cost,
                "max": self.max_cost,
                "average": self.avg_cost
            },
            "breakdown": {
                "parts": self.parts_cost,
                "labor": self.labor_cost,
                "labor_hours": self.labor_hours
            },
            "urgency": self.urgency.value,
            "savings_if_preventive": self.savings_if_preventive,
            "currency": "EUR"
        }


@dataclass
class CostSummary:
    """Resumen de costes totales"""
    total_min: float = 0.0
    total_max: float = 0.0
    total_avg: float = 0.0
    repairs: List[RepairCost] = field(default_factory=list)
    potential_savings: float = 0.0
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> dict:
        return {
            "total_estimated": {
                "min": round(self.total_min, 2),
                "max": round(self.total_max, 2),
                "average": round(self.total_avg, 2)
            },
            "potential_savings_if_preventive": round(self.potential_savings, 2),
            "repair_count": len(self.repairs),
            "repairs": [r.to_dict() for r in self.repairs],
            "timestamp": self.timestamp,
            "currency": "EUR"
        }


class CostEstimator:
    """
    Estimador de costes de reparación.
    Precios basados en talleres de precio medio en España (2024).
    """
    
    # Tarifa media de mano de obra por hora (€/hora)
    LABOR_RATE = 45.0  # Precio medio en España
    
    # Catálogo de reparaciones por componente y tipo de problema
    REPAIR_CATALOG = {
        "engine": {
            "overheating": {
                "preventive": {
                    "description": "Revisión sistema refrigeración + cambio líquido",
                    "parts": 35,
                    "hours": 1.0,
                },
                "minor": {
                    "description": "Cambio termostato + manguitos",
                    "parts": 80,
                    "hours": 2.0,
                },
                "major": {
                    "description": "Reparación/cambio radiador + bomba agua",
                    "parts": 350,
                    "hours": 4.0,
                },
                "critical": {
                    "description": "Reparación junta culata por sobrecalentamiento",
                    "parts": 450,
                    "hours": 12.0,
                }
            },
            "excessive_wear": {
                "preventive": {
                    "description": "Cambio aceite + filtros anticipado",
                    "parts": 60,
                    "hours": 0.5,
                },
                "minor": {
                    "description": "Ajuste motor + cambio bujías/bobinas",
                    "parts": 150,
                    "hours": 2.5,
                },
                "major": {
                    "description": "Reparación segmentos/válvulas",
                    "parts": 600,
                    "hours": 10.0,
                },
                "critical": {
                    "description": "Reconstrucción motor / motor de intercambio",
                    "parts": 2500,
                    "hours": 20.0,
                }
            },
            "oil_change": {
                "preventive": {
                    "description": "Cambio aceite y filtro",
                    "parts": 45,
                    "hours": 0.5,
                }
            }
        },
        "brakes": {
            "wear_degradation": {
                "preventive": {
                    "description": "Revisión sistema de frenos",
                    "parts": 0,
                    "hours": 0.5,
                },
                "minor": {
                    "description": "Cambio pastillas de freno (eje)",
                    "parts": 60,
                    "hours": 1.0,
                },
                "major": {
                    "description": "Cambio pastillas + discos (eje)",
                    "parts": 180,
                    "hours": 2.0,
                },
                "critical": {
                    "description": "Cambio completo sistema frenos (4 ruedas)",
                    "parts": 450,
                    "hours": 4.0,
                }
            },
            "accelerated_wear": {
                "preventive": {
                    "description": "Revisión y ajuste frenos",
                    "parts": 15,
                    "hours": 1.0,
                },
                "minor": {
                    "description": "Cambio pastillas + rectificado discos",
                    "parts": 90,
                    "hours": 2.5,
                },
                "major": {
                    "description": "Cambio pastillas + discos + pinzas",
                    "parts": 380,
                    "hours": 4.0,
                }
            }
        },
        "transmission": {
            "gear_stress": {
                "preventive": {
                    "description": "Cambio aceite transmisión",
                    "parts": 80,
                    "hours": 1.0,
                },
                "minor": {
                    "description": "Ajuste/reparación embrague",
                    "parts": 200,
                    "hours": 4.0,
                },
                "major": {
                    "description": "Cambio kit embrague completo",
                    "parts": 450,
                    "hours": 6.0,
                },
                "critical": {
                    "description": "Reparación/reconstrucción caja de cambios",
                    "parts": 1200,
                    "hours": 15.0,
                }
            },
            "aggressive_driving_wear": {
                "preventive": {
                    "description": "Revisión transmisión + cambio aceite",
                    "parts": 90,
                    "hours": 1.5,
                },
                "minor": {
                    "description": "Cambio sincronizadores",
                    "parts": 350,
                    "hours": 8.0,
                },
                "major": {
                    "description": "Reconstrucción parcial caja cambios",
                    "parts": 800,
                    "hours": 12.0,
                }
            }
        },
        "tires": {
            "pressure_loss": {
                "preventive": {
                    "description": "Revisión + inflado + válvulas",
                    "parts": 20,
                    "hours": 0.3,
                },
                "minor": {
                    "description": "Reparación pinchazo",
                    "parts": 15,
                    "hours": 0.5,
                },
                "major": {
                    "description": "Cambio neumático (1 unidad)",
                    "parts": 90,
                    "hours": 0.5,
                },
                "critical": {
                    "description": "Cambio juego neumáticos (4 unidades)",
                    "parts": 360,
                    "hours": 1.5,
                }
            },
            "high_speed_wear": {
                "preventive": {
                    "description": "Rotación + equilibrado neumáticos",
                    "parts": 0,
                    "hours": 1.0,
                },
                "minor": {
                    "description": "Alineación + equilibrado",
                    "parts": 0,
                    "hours": 1.5,
                },
                "major": {
                    "description": "Cambio 2 neumáticos + alineación",
                    "parts": 180,
                    "hours": 1.5,
                }
            }
        },
        "battery": {
            "heat_degradation": {
                "preventive": {
                    "description": "Revisión + limpieza bornes batería",
                    "parts": 5,
                    "hours": 0.3,
                },
                "minor": {
                    "description": "Carga + test batería",
                    "parts": 0,
                    "hours": 0.5,
                },
                "major": {
                    "description": "Cambio batería",
                    "parts": 120,
                    "hours": 0.5,
                },
                "critical": {
                    "description": "Cambio batería + revisión alternador",
                    "parts": 180,
                    "hours": 1.5,
                }
            },
            "cold_performance": {
                "preventive": {
                    "description": "Test y carga batería",
                    "parts": 0,
                    "hours": 0.5,
                },
                "minor": {
                    "description": "Cambio batería estándar",
                    "parts": 100,
                    "hours": 0.5,
                }
            }
        }
    }
    
    def __init__(self, labor_rate: float = None):
        self.labor_rate = labor_rate or self.LABOR_RATE
    
    def _get_repair_level(self, risk_level: str, health_score: float) -> str:
        """Determina el nivel de reparación basado en riesgo y salud"""
        if risk_level == "critical" or health_score < 20:
            return "critical"
        elif risk_level == "high" or health_score < 40:
            return "major"
        elif risk_level == "moderate" or health_score < 70:
            return "minor"
        return "preventive"
    
    def _calculate_repair_cost(self, component: str, problem_type: str, 
                                repair_level: str) -> Optional[RepairCost]:
        """Calcula el coste de una reparación específica"""
        
        component_repairs = self.REPAIR_CATALOG.get(component, {})
        problem_repairs = component_repairs.get(problem_type, {})
        repair_data = problem_repairs.get(repair_level)
        
        if not repair_data:
            # Buscar nivel más cercano disponible
            levels = ["preventive", "minor", "major", "critical"]
            current_idx = levels.index(repair_level) if repair_level in levels else 0
            
            for i in range(current_idx, -1, -1):
                repair_data = problem_repairs.get(levels[i])
                if repair_data:
                    break
            
            if not repair_data:
                return None
        
        parts_cost = repair_data["parts"]
        labor_hours = repair_data["hours"]
        labor_cost = labor_hours * self.labor_rate
        avg_cost = parts_cost + labor_cost
        
        # Rango de precios (±20%)
        min_cost = avg_cost * 0.8
        max_cost = avg_cost * 1.2
        
        # Calcular ahorro potencial si se actúa preventivamente
        preventive_data = problem_repairs.get("preventive", {})
        if preventive_data and repair_level != "preventive":
            preventive_cost = preventive_data["parts"] + (preventive_data["hours"] * self.labor_rate)
            savings = avg_cost - preventive_cost
        else:
            savings = 0
        
        # Determinar urgencia
        urgency_map = {
            "preventive": RepairUrgency.PREVENTIVE,
            "minor": RepairUrgency.RECOMMENDED,
            "major": RepairUrgency.URGENT,
            "critical": RepairUrgency.CRITICAL
        }
        
        return RepairCost(
            component=component,
            repair_type=problem_type,
            description=repair_data["description"],
            min_cost=round(min_cost, 2),
            max_cost=round(max_cost, 2),
            avg_cost=round(avg_cost, 2),
            labor_hours=labor_hours,
            parts_cost=parts_cost,
            labor_cost=round(labor_cost, 2),
            urgency=urgency_map.get(repair_level, RepairUrgency.RECOMMENDED),
            savings_if_preventive=round(savings, 2)
        )
    
    def estimate_from_predictions(self, predictions: List[Dict]) -> CostSummary:
        """Estima costes basándose en predicciones del FuturePredictor"""
        summary = CostSummary()
        processed = set()  # Evitar duplicados
        
        for pred in predictions:
            component = pred.get("component", "")
            problem_type = pred.get("problem_type", "")
            risk_level = pred.get("risk_level", "low")
            
            # Evitar duplicados del mismo componente/problema
            key = f"{component}:{problem_type}"
            if key in processed:
                continue
            processed.add(key)
            
            # Obtener salud del componente si está disponible
            health = pred.get("data_points", {}).get("health_score", 70)
            
            repair_level = self._get_repair_level(risk_level, health)
            repair_cost = self._calculate_repair_cost(component, problem_type, repair_level)
            
            if repair_cost:
                summary.repairs.append(repair_cost)
                summary.total_min += repair_cost.min_cost
                summary.total_max += repair_cost.max_cost
                summary.total_avg += repair_cost.avg_cost
                summary.potential_savings += repair_cost.savings_if_preventive
        
        return summary
    
    def estimate_from_alerts(self, alerts: List[Dict]) -> CostSummary:
        """Estima costes basándose en alertas activas"""
        summary = CostSummary()
        processed = set()
        
        # Mapeo de tipos de alerta a tipos de problema
        alert_to_problem = {
            "overheating": "overheating",
            "high_rpm": "excessive_wear",
            "vibration": "wear_degradation",
            "pressure": "pressure_loss",
            "temperature": "heat_degradation",
        }
        
        for alert in alerts:
            component = alert.get("component", "")
            alert_level = alert.get("level", "info")
            message = alert.get("message", "").lower()
            
            # Determinar tipo de problema desde el mensaje
            problem_type = None
            for keyword, ptype in alert_to_problem.items():
                if keyword in message:
                    problem_type = ptype
                    break
            
            if not problem_type:
                # Usar problema genérico basado en componente
                default_problems = {
                    "engine": "excessive_wear",
                    "brakes": "wear_degradation",
                    "transmission": "gear_stress",
                    "tires": "pressure_loss",
                    "battery": "heat_degradation"
                }
                problem_type = default_problems.get(component, "")
            
            if not problem_type:
                continue
            
            key = f"{component}:{problem_type}"
            if key in processed:
                continue
            processed.add(key)
            
            # Mapear nivel de alerta a nivel de reparación
            level_map = {
                "info": "preventive",
                "warning": "minor",
                "critical": "major",
                "emergency": "critical"
            }
            repair_level = level_map.get(alert_level, "minor")
            
            repair_cost = self._calculate_repair_cost(component, problem_type, repair_level)
            
            if repair_cost:
                summary.repairs.append(repair_cost)
                summary.total_min += repair_cost.min_cost
                summary.total_max += repair_cost.max_cost
                summary.total_avg += repair_cost.avg_cost
                summary.potential_savings += repair_cost.savings_if_preventive
        
        return summary
    
    def estimate_from_wear_state(self, wear_state: Dict) -> CostSummary:
        """Estima costes basándose en estado de desgaste de componentes"""
        summary = CostSummary()
        components = wear_state.get("components", {})
        
        for comp_name, comp_data in components.items():
            health = comp_data.get("health_score", 100)
            status = comp_data.get("status", "good")
            hours_until = comp_data.get("hours_until_maintenance", 999)
            
            # Solo estimar si hay problemas
            if status == "good" and hours_until > 50:
                continue
            
            # Determinar tipo de problema genérico
            default_problems = {
                "engine": "excessive_wear",
                "brakes": "wear_degradation",
                "transmission": "gear_stress",
                "tires": "high_speed_wear",
                "battery": "heat_degradation"
            }
            problem_type = default_problems.get(comp_name, "")
            
            if not problem_type:
                continue
            
            # Determinar nivel de reparación
            if status == "failure" or health < 20:
                repair_level = "critical"
            elif status == "critical" or health < 40:
                repair_level = "major"
            elif status == "warning" or health < 70:
                repair_level = "minor"
            else:
                repair_level = "preventive"
            
            repair_cost = self._calculate_repair_cost(comp_name, problem_type, repair_level)
            
            if repair_cost:
                summary.repairs.append(repair_cost)
                summary.total_min += repair_cost.min_cost
                summary.total_max += repair_cost.max_cost
                summary.total_avg += repair_cost.avg_cost
                summary.potential_savings += repair_cost.savings_if_preventive
        
        return summary
    
    def get_maintenance_schedule_cost(self) -> Dict:
        """Retorna costes de mantenimiento preventivo programado"""
        preventive_costs = []
        
        maintenance_items = [
            ("engine", "oil_change", "Cambio aceite y filtros"),
            ("brakes", "wear_degradation", "Revisión frenos"),
            ("transmission", "gear_stress", "Cambio aceite transmisión"),
            ("tires", "high_speed_wear", "Rotación y equilibrado"),
            ("battery", "heat_degradation", "Revisión batería"),
        ]
        
        total = 0
        for component, problem, desc in maintenance_items:
            cost = self._calculate_repair_cost(component, problem, "preventive")
            if cost:
                preventive_costs.append({
                    "item": desc,
                    "component": component,
                    "cost": cost.avg_cost
                })
                total += cost.avg_cost
        
        return {
            "maintenance_items": preventive_costs,
            "total_preventive_cost": round(total, 2),
            "recommendation": "Realizar mantenimiento preventivo cada 10,000-15,000 km o anualmente",
            "currency": "EUR"
        }
