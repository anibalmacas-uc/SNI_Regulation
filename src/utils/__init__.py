"""Funciones de utilidad para cálculos del sistema"""

import numpy as np
import pandas as pd
from datetime import datetime


class FrequencyCalculator:
    """Calcula cambios de frecuencia basados en desbalance generación-demanda"""
    
    @staticmethod
    def calculate_frequency_deviation(generation_mw, demand_mw, current_frequency=60.0):
        """
        Calcula desviación de frecuencia según desbalance de potencia
        
        Modelo simplificado: df/dt = k * (Pg - Pd) / Prated
        
        Args:
            generation_mw: Potencia generada (MW)
            demand_mw: Potencia demandada (MW)
            current_frequency: Frecuencia actual (Hz)
        
        Returns:
            Desviación de frecuencia (Hz)
        """
        
        # Constante de inercia del sistema (aproximada para Ecuador)
        # Sistemas más grandes tienen mayor inercia
        K_INERTIA = 0.015  # Hz/MW de desbalance
        
        power_imbalance = generation_mw - demand_mw
        frequency_change = K_INERTIA * power_imbalance
        
        new_frequency = current_frequency + frequency_change
        
        return new_frequency
    
    @staticmethod
    def time_to_blackout(generation_mw, demand_mw, current_frequency=60.0):
        """
        Estima tiempo hasta que la frecuencia alcance punto crítico (58.5 Hz)
        si no se toman acciones
        
        Args:
            generation_mw: Potencia generada (MW)
            demand_mw: Potencia demandada (MW)
            current_frequency: Frecuencia actual (Hz)
        
        Returns:
            Tiempo en segundos
        """
        
        CRITICAL_FREQUENCY = 58.5
        FREQUENCY_DECAY_RATE = 0.05  # Hz/segundo cuando hay déficit
        
        if generation_mw >= demand_mw:
            return float('inf')  # No hay riesgo
        
        frequency_gap = current_frequency - CRITICAL_FREQUENCY
        
        if frequency_gap <= 0:
            return 0  # Ya en crisis
        
        time_seconds = frequency_gap / FREQUENCY_DECAY_RATE
        return max(0, time_seconds)


class EconomicImpactCalculator:
    """Calcula impacto económico de déficits de generación"""
    
    # Pérdidas económicas por MWh no suministrado (USD)
    LOSS_RATES = {
        "industrial": 5000,      # Sector industrial
        "comercial": 3000,       # Sector comercial
        "residencial": 1000,     # Sector residencial
        "público": 2000,         # Servicios públicos
    }
    
    @staticmethod
    def calculate_deficit_loss(deficit_mw, duration_hours=1.0, sector_mix=None):
        """
        Calcula pérdidas económicas por déficit de energía
        
        Args:
            deficit_mw: Déficit de potencia (MW)
            duration_hours: Duración del déficit (horas)
            sector_mix: dict con distribución de sectores
        
        Returns:
            float: Pérdidas en USD
        """
        
        if sector_mix is None:
            sector_mix = {
                "industrial": 0.30,
                "comercial": 0.25,
                "residencial": 0.35,
                "público": 0.10,
            }
        
        energy_not_supplied_mwh = deficit_mw * duration_hours
        
        total_loss = 0
        for sector, fraction in sector_mix.items():
            sector_energy = energy_not_supplied_mwh * fraction
            sector_loss = sector_energy * EconomicImpactCalculator.LOSS_RATES[sector]
            total_loss += sector_loss
        
        return total_loss
    
    @staticmethod
    def calculate_zone_impact(deficit_mw, affected_zones, population_data):
        """
        Calcula impacto por zona afectada
        
        Args:
            deficit_mw: Déficit total (MW)
            affected_zones: list de zonas afectadas
            population_data: dict con población por zona (millones)
        
        Returns:
            DataFrame con impacto por zona
        """
        
        mw_per_zone = deficit_mw / len(affected_zones) if affected_zones else 0
        
        data = []
        for zone in affected_zones:
            pop_millions = population_data.get(zone, 1.0)
            people_affected = int(pop_millions * 1_000_000)
            mwh_not_supplied = mw_per_zone  # Aproximado
            
            data.append({
                'zone': zone,
                'deficit_mw': mw_per_zone,
                'people_affected': people_affected,
                'estimated_economic_loss_usd': mwh_not_supplied * 3500,  # Promedio
            })
        
        return pd.DataFrame(data)


class PowerFlowAnalyzer:
    """Análisis de flujo de potencia en zonas del SNI"""
    
    @staticmethod
    def calculate_zone_generation(plants_df, zone_name, generation_factors):
        """
        Calcula generación de una zona específica
        
        Args:
            plants_df: DataFrame de plantas
            zone_name: Nombre de zona
            generation_factors: dict {planta: factor_0_a_1}
        
        Returns:
            float: MW generados
        """
        
        # Agrupar plantas por zona (simplificado)
        zone_plants = plants_df[plants_df['zone'] == zone_name] if 'zone' in plants_df else plants_df
        
        total_generation = 0
        for _, plant in zone_plants.iterrows():
            factor = generation_factors.get(plant['name'], 0.85)
            total_generation += plant['capacity_mw'] * factor
        
        return total_generation
    
    @staticmethod
    def analyze_transmission_congestion(generation_by_zone, demand_by_zone):
        """
        Analiza congestión de transmisión entre zonas
        
        Args:
            generation_by_zone: dict {zona: MW}
            demand_by_zone: dict {zona: MW}
        
        Returns:
            dict con análisis de flujos
        """
        
        analysis = {}
        
        for zone in generation_by_zone.keys():
            gen = generation_by_zone[zone]
            dem = demand_by_zone.get(zone, 0)
            balance = gen - dem
            
            analysis[zone] = {
                'generation': gen,
                'demand': dem,
                'balance': balance,
                'export': max(0, balance),
                'import': abs(min(0, balance)),
                'utilization_percent': (dem / gen * 100) if gen > 0 else 0,
            }
        
        return analysis


class GridStabilityMonitor:
    """Monitorea estabilidad de la red en tiempo real"""
    
    def __init__(self):
        self.frequency_history = []
        self.voltage_history = []
        self.power_imbalance_history = []
    
    def check_stability(self, frequency, voltage, power_imbalance):
        """
        Verifica estabilidad del sistema
        
        Returns:
            dict con estado de salud del sistema
        """
        
        # Umbrales
        FREQUENCY_MIN = 59.5
        FREQUENCY_MAX = 60.5
        VOLTAGE_MIN = 0.90  # En pu (por unidad)
        VOLTAGE_MAX = 1.10
        MAX_IMBALANCE_PERCENT = 10
        
        status = {
            'frequency_ok': FREQUENCY_MIN <= frequency <= FREQUENCY_MAX,
            'voltage_ok': VOLTAGE_MIN <= voltage <= VOLTAGE_MAX,
            'imbalance_ok': abs(power_imbalance) <= MAX_IMBALANCE_PERCENT,
            'overall_status': 'NORMAL',
        }
        
        # Determinar estado general
        if not status['frequency_ok'] or not status['voltage_ok'] or not status['imbalance_ok']:
            if frequency < 59.0 or not status['voltage_ok']:
                status['overall_status'] = 'CRÍTICO'
            elif frequency < 59.5 or abs(power_imbalance) > 15:
                status['overall_status'] = 'ALERTA'
            else:
                status['overall_status'] = 'ADVERTENCIA'
        
        return status
