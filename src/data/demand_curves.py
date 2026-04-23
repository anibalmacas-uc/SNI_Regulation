"""
Generación de curvas de demanda del SNI basadas en datos históricos
"""

import numpy as np
from scipy.interpolate import CubicSpline, interp1d
import pandas as pd
from datetime import datetime, timedelta


class DemandCurveGenerator:
    """Genera curvas de demanda realistas para Ecuador"""
    
    # Puntos de demanda histórica (basados en el gráfico adjunto)
    # Demanda máxima histórica: Martes, 14 de abril de 2026 ~ 5000 MW
    HISTORICAL_DEMAND_POINTS = {
        0: 2800,   # 00:00
        1: 2700,   # 01:00
        2: 2600,   # 02:00
        3: 2650,   # 03:00
        4: 2700,   # 04:00
        5: 2900,   # 05:00
        6: 3200,   # 06:00
        7: 3800,   # 07:00
        8: 4200,   # 08:00
        9: 4400,   # 09:00
        10: 4500,  # 10:00
        11: 4600,  # 11:00
        12: 4650,  # 12:00
        13: 4700,  # 13:00
        14: 4750,  # 14:00
        15: 4800,  # 15:00
        16: 4900,  # 16:00
        17: 5000,  # 17:00
        18: 4950,  # 18:00
        19: 4900,  # 19:00 - Pico ~5000 MW
        20: 4600,  # 20:00
        21: 4200,  # 21:00
        22: 3800,  # 22:00
        23: 3200,  # 23:00
    }
    
    @classmethod
    def generate_smooth_24h_curve(cls, peak_factor=1.0, noise_level=0.02):
        """
        Genera una curva suave de demanda 24h usando interpolación cúbica
        
        Args:
            peak_factor: Factor multiplicativo para amplificar/reducir demanda
            noise_level: Nivel de ruido aleatorio (0-1)
        
        Returns:
            dict: {'hours': array, 'demand': array}
        """
        
        hours_base = np.array(list(cls.HISTORICAL_DEMAND_POINTS.keys()), dtype=float)
        demand_base = np.array(list(cls.HISTORICAL_DEMAND_POINTS.values()), dtype=float)
        
        # Aplicar factor de pico
        demand_base = demand_base * peak_factor
        
        # Crear spline cúbica para interpolación suave
        # Usar bc_type='natural' en lugar de 'periodic' para evitar restricciones de igualdad
        cs = CubicSpline(hours_base, demand_base, bc_type='natural')
        
        # Generar puntos cada 15 minutos (0.25 horas)
        hours_fine = np.arange(0, 24, 0.25)
        demand_smooth = cs(hours_fine)
        
        # Agregar ruido realista
        if noise_level > 0:
            noise = np.random.normal(0, noise_level * demand_smooth.mean(), len(demand_smooth))
            demand_smooth = demand_smooth + noise
            demand_smooth = np.maximum(demand_smooth, demand_smooth.min())  # Sin negativos
        
        return {
            'hours': hours_fine,
            'demand': demand_smooth,
            'demand_hourly': demand_base,
        }
    
    @classmethod
    def generate_weekly_pattern(cls, base_curve_config=None):
        """
        Genera patrones de demanda para una semana completa
        
        Returns:
            DataFrame con demanda por hora, día
        """
        
        # Factores por día de la semana (Lunes-Domingo)
        # Sabado y domingo tienen menor demanda
        day_factors = {
            'Lunes': 1.0,
            'Martes': 1.02,
            'Miércoles': 1.01,
            'Jueves': 0.99,
            'Viernes': 1.03,
            'Sábado': 0.92,
            'Domingo': 0.88,
        }
        
        base_curve = cls.generate_smooth_24h_curve(peak_factor=1.0, noise_level=0.01)
        
        data = []
        start_date = datetime(2026, 4, 14)  # Martes, 14 de abril
        
        for day_offset in range(7):
            current_date = start_date + timedelta(days=day_offset)
            day_name = current_date.strftime('%A')
            
            # Mapeo a español
            day_name_es = {
                'Monday': 'Lunes',
                'Tuesday': 'Martes',
                'Wednesday': 'Miércoles',
                'Thursday': 'Jueves',
                'Friday': 'Viernes',
                'Saturday': 'Sábado',
                'Sunday': 'Domingo',
            }.get(day_name, 'Desconocido')
            
            factor = day_factors.get(day_name_es, 1.0)
            
            for hour, demand in zip(base_curve['hours'], base_curve['demand']):
                data.append({
                    'datetime': current_date + timedelta(hours=hour),
                    'date': current_date.date(),
                    'day': day_name_es,
                    'hour': int(hour),
                    'demand_mw': demand * factor,
                })
        
        return pd.DataFrame(data)
    
    @classmethod
    def get_peak_hours(cls, demand_array, num_peaks=5):
        """
        Identifica las horas de máxima demanda
        
        Args:
            demand_array: Array de demanda
            num_peaks: Número de picos a retornar
        
        Returns:
            list: Índices de horas pico
        """
        
        indices = np.argsort(demand_array)[-num_peaks:]
        return sorted(indices)
    
    @classmethod
    def get_valley_hours(cls, demand_array, num_valleys=3):
        """
        Identifica las horas de mínima demanda
        
        Args:
            demand_array: Array de demanda
            num_valleys: Número de valles a retornar
        
        Returns:
            list: Índices de horas valle
        """
        
        indices = np.argsort(demand_array)[:num_valleys]
        return sorted(indices)


class DemandAdjuster:
    """Ajusta la demanda según input del usuario"""
    
    @staticmethod
    def apply_percentage_change(demand_curve, percentage_change):
        """
        Aplica cambio porcentual a la demanda
        
        Args:
            demand_curve: Array de demanda
            percentage_change: Cambio en % (ej: +10 o -5)
        
        Returns:
            Array ajustado
        """
        
        factor = 1 + (percentage_change / 100)
        return demand_curve * factor
    
    @staticmethod
    def apply_absolute_change(demand_curve, mw_change):
        """
        Aplica cambio absoluto en MW
        
        Args:
            demand_curve: Array de demanda
            mw_change: Cambio en MW (ej: +500 o -200)
        
        Returns:
            Array ajustado
        """
        
        return demand_curve + mw_change
    
    @staticmethod
    def create_scenario(base_demand, changes_by_hour):
        """
        Crea escenario personalizado de demanda
        
        Args:
            base_demand: Demanda base
            changes_by_hour: dict {hora: cambio_mw}
        
        Returns:
            Array de demanda modificado
        """
        
        adjusted = base_demand.copy()
        for hour, change in changes_by_hour.items():
            if 0 <= hour < len(adjusted):
                adjusted[hour] += change
        
        return adjusted


class LoadForecastingModel:
    """Modelo simple de predicción de carga"""
    
    @staticmethod
    def forecast_next_day(historical_week_df):
        """
        Predice la demanda del día siguiente basada en histórico
        
        Args:
            historical_week_df: DataFrame con datos semanales
        
        Returns:
            Array con pronóstico 24h
        """
        
        # Agrupar por hora y calcular promedio
        hourly_avg = historical_week_df.groupby('hour')['demand_mw'].mean()
        
        return hourly_avg.values
    
    @staticmethod
    def calculate_confidence_interval(historical_week_df, confidence=0.95):
        """
        Calcula intervalos de confianza para el pronóstico
        
        Args:
            historical_week_df: DataFrame con datos semanales
            confidence: Nivel de confianza (0-1)
        
        Returns:
            dict con bounds
        """
        
        hourly_std = historical_week_df.groupby('hour')['demand_mw'].std()
        hourly_mean = historical_week_df.groupby('hour')['demand_mw'].mean()
        
        z_score = 1.96 if confidence == 0.95 else 2.576  # Para 99%
        
        return {
            'mean': hourly_mean.values,
            'upper': (hourly_mean + z_score * hourly_std).values,
            'lower': (hourly_mean - z_score * hourly_std).values,
        }
