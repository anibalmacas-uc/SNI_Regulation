"""
Datos de centrales hidroeléctricas y térmicas de Ecuador
Basado en datos históricos y públicamente disponibles
"""

import pandas as pd
import numpy as np
from datetime import datetime


class PowerPlantDatabase:
    """Base de datos de centrales de generación del SNI Ecuador"""
    
    # Principales centrales hidroeléctricas de Ecuador
    HYDROELECTRIC_PLANTS = [
        {
            "name": "Coca Codo Sinclair",
            "type": "Hidroeléctrica",
            "capacity_mw": 1500,
            "latitude": -0.6533,
            "longitude": -77.9733,
            "status": True,
            "reservoir": "Río Coca-Codo",
            "commission_year": 2016
        },
        {
            "name": "Paute",
            "type": "Hidroeléctrica",
            "capacity_mw": 1100,
            "latitude": -2.7667,
            "longitude": -78.6167,
            "status": True,
            "reservoir": "Embalse Paute",
            "commission_year": 1983
        },
        {
            "name": "Sopladora",
            "type": "Hidroeléctrica",
            "capacity_mw": 487,
            "latitude": -2.8333,
            "longitude": -78.9333,
            "status": True,
            "reservoir": "Río Paute",
            "commission_year": 2016
        },
        {
            "name": "Mazar",
            "type": "Hidroeléctrica",
            "capacity_mw": 160,
            "latitude": -2.6333,
            "longitude": -78.4333,
            "status": True,
            "reservoir": "Río Paute",
            "commission_year": 2011
        },
        {
            "name": "Minas San Francisco",
            "type": "Hidroeléctrica",
            "capacity_mw": 30,
            "latitude": -2.6167,
            "longitude": -78.5,
            "status": True,
            "reservoir": "Río Paute",
            "commission_year": 2012
        },
        {
            "name": "Agoyán",
            "type": "Hidroeléctrica",
            "capacity_mw": 156,
            "latitude": -1.2,
            "longitude": -78.6167,
            "status": True,
            "reservoir": "Río Pastaza",
            "commission_year": 2003
        },
        {
            "name": "Delsitanisagua",
            "type": "Hidroeléctrica",
            "capacity_mw": 113,
            "latitude": -1.1,
            "longitude": -78.5667,
            "status": True,
            "reservoir": "Río Pastaza",
            "commission_year": 2003
        },
        {
            "name": "San Francisco",
            "type": "Hidroeléctrica",
            "capacity_mw": 75,
            "latitude": -0.8,
            "longitude": -78.3,
            "status": True,
            "reservoir": "Río San Francisco",
            "commission_year": 2011
        },
    ]
    
    # Principales centrales térmicas de Ecuador
    THERMAL_PLANTS = [
        {
            "name": "Térmica Guayaquil",
            "type": "Térmica",
            "capacity_mw": 700,
            "latitude": -2.2,
            "longitude": -79.8833,
            "status": True,
            "fuel_type": "Gas Natural",
            "commission_year": 2007
        },
        {
            "name": "Térmica Esmeraldas",
            "type": "Térmica",
            "capacity_mw": 290,
            "latitude": 0.9667,
            "longitude": -79.65,
            "status": True,
            "fuel_type": "Petróleo",
            "commission_year": 1980
        },
        {
            "name": "Térmica Quito",
            "type": "Térmica",
            "capacity_mw": 345,
            "latitude": -0.35,
            "longitude": -78.5,
            "status": True,
            "fuel_type": "Gas Natural",
            "commission_year": 2010
        },
        {
            "name": "Térmica Machala",
            "type": "Térmica",
            "capacity_mw": 270,
            "latitude": -3.2667,
            "longitude": -79.9,
            "status": True,
            "fuel_type": "Gas Natural",
            "commission_year": 2005
        },
        {
            "name": "Térmica Salinas",
            "type": "Térmica",
            "capacity_mw": 240,
            "latitude": -2.2167,
            "longitude": -80.95,
            "status": True,
            "fuel_type": "Petróleo",
            "commission_year": 1982
        },
        {
            "name": "Térmica Milagro",
            "type": "Térmica",
            "capacity_mw": 165,
            "latitude": -2.6333,
            "longitude": -79.6,
            "status": True,
            "fuel_type": "Gas Natural",
            "commission_year": 2003
        },
        {
            "name": "Térmica Santa Elena",
            "type": "Térmica",
            "capacity_mw": 160,
            "latitude": -2.2333,
            "longitude": -80.3667,
            "status": True,
            "fuel_type": "Gas Natural",
            "commission_year": 2015
        },
    ]
    
    # Plantas renovables
    RENEWABLE_PLANTS = [
        {
            "name": "Parque Solar Quisapincha",
            "type": "Solar",
            "capacity_mw": 31,
            "latitude": -1.2,
            "longitude": -78.65,
            "status": True,
            "commission_year": 2020
        },
        {
            "name": "Parque Eólico Balzar",
            "type": "Eólica",
            "capacity_mw": 20,
            "latitude": -2.5,
            "longitude": -79.2,
            "status": True,
            "commission_year": 2018
        },
        {
            "name": "Biomasa Sucumbíos",
            "type": "Biomasa",
            "capacity_mw": 9,
            "latitude": 0.0,
            "longitude": -76.0,
            "status": True,
            "commission_year": 2019
        },
    ]
    
    @classmethod
    def get_all_plants(cls):
        """Retorna todas las plantas en un DataFrame"""
        all_plants = cls.HYDROELECTRIC_PLANTS + cls.THERMAL_PLANTS + cls.RENEWABLE_PLANTS
        return pd.DataFrame(all_plants)
    
    @classmethod
    def get_plants_by_type(cls, plant_type):
        """Retorna plantas filtradas por tipo"""
        df = cls.get_all_plants()
        return df[df['type'] == plant_type].to_dict('records')
    
    @classmethod
    def get_active_capacity(cls, include_type=None):
        """Calcula capacidad total instalada activa"""
        df = cls.get_all_plants()
        active = df[df['status'] == True]
        
        if include_type:
            active = active[active['type'] == include_type]
        
        return active['capacity_mw'].sum()
    
    @classmethod
    def export_as_dataframe(cls, include_status=True):
        """Exporta como DataFrame con información adicional"""
        df = cls.get_all_plants()
        df['installed_date'] = pd.to_datetime(df['commission_year'], format='%Y')
        
        # Categoría
        def categorize(plant_type):
            if plant_type == "Hidroeléctrica":
                return "Hidroeléctrica"
            elif plant_type == "Térmica":
                return "Térmica"
            else:
                return "Renovable"
        
        df['category'] = df['type'].apply(categorize)
        return df


class DynamicPlantSimulator:
    """Simula la generación variable de plantas a lo largo del día"""
    
    @staticmethod
    def simulate_hourly_output(hour, capacity_mw, plant_type, variability=0.1):
        """
        Simula la salida de una planta en una hora específica
        
        Args:
            hour: Hora del día (0-23)
            capacity_mw: Capacidad instalada
            plant_type: Tipo de planta
            variability: Factor de variabilidad (0-1)
        
        Returns:
            MW generados
        """
        
        if plant_type == "Hidroeléctrica":
            # Las hidroeléctricas son más estables, ~85-95% de capacidad
            base_factor = 0.90
            noise = np.random.normal(0, variability * 0.05)
            return capacity_mw * (base_factor + noise)
        
        elif plant_type == "Térmica":
            # Las térmicas siguen la demanda, más variables
            # Peak en horas de máxima demanda (19:00 = hora 19)
            peak_factor = 1 - np.cos(2 * np.pi * (hour - 6) / 24)
            peak_factor = 0.4 + peak_factor * 0.5
            noise = np.random.normal(0, variability * 0.08)
            return capacity_mw * (peak_factor + noise)
        
        else:  # Solar, Eólica, Biomasa
            if plant_type == "Solar":
                # Solar sigue el ciclo del sol (6:00 a 18:00)
                if 6 <= hour <= 18:
                    solar_factor = np.sin(np.pi * (hour - 6) / 12)
                else:
                    solar_factor = 0
                return capacity_mw * solar_factor
            
            elif plant_type == "Eólica":
                # Eólica tiene mayor variabilidad
                wind_factor = 0.3 + 0.4 * np.sin(2 * np.pi * hour / 24)
                noise = np.random.normal(0, variability * 0.15)
                return capacity_mw * (wind_factor + noise)
            
            else:  # Biomasa
                return capacity_mw * 0.8  # Más constante
    
    @staticmethod
    def generate_24h_curve(df_plants, base_demand_curve, seed=42):
        """
        Genera una curva de 24 horas de generación
        
        Args:
            df_plants: DataFrame de plantas
            base_demand_curve: Array con demanda por hora
            seed: Para reproducibilidad
        
        Returns:
            dict con curvas de generación por tipo
        """
        np.random.seed(seed)
        hours = np.arange(24)
        
        generation_by_type = {
            "Hidroeléctrica": np.zeros(24),
            "Térmica": np.zeros(24),
            "Solar": np.zeros(24),
            "Eólica": np.zeros(24),
            "Biomasa": np.zeros(24),
        }
        
        # Simular cada planta
        for _, plant in df_plants.iterrows():
            plant_type = plant['type']
            capacity = plant['capacity_mw']
            
            for hour in hours:
                output = DynamicPlantSimulator.simulate_hourly_output(
                    hour, capacity, plant_type
                )
                generation_by_type[plant_type][hour] += output
        
        # Ajustar para que coincida aproximadamente con demanda
        total_gen = sum(generation_by_type.values())
        total_demand = base_demand_curve.sum()
        
        scaling_factor = total_demand / (total_gen + 1e-6)
        for key in generation_by_type:
            generation_by_type[key] *= scaling_factor * 0.95  # 95% para margen
        
        return generation_by_type
