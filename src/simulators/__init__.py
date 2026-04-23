"""Simulador de alivio de carga por baja frecuencia (UFLS)"""

import numpy as np
import pandas as pd
from datetime import datetime
from config import UFLS_STAGES, SNI_ZONES, FREQUENCY_UFLS_TRIGGER


class UnderFrequencyLoadShedding:
    """Implementa esquema UFLS del SNI"""
    
    def __init__(self):
        self.active_stages = set()
        self.total_load_shed_mw = 0
        self.affected_zones = []
        self.shedding_history = []
        self.frequency_history = []
    
    def evaluate_ufls(self, current_frequency, system_load_mw):
        """
        Evalúa si se debe activar UFLS basado en frecuencia
        
        Args:
            current_frequency: Frecuencia actual (Hz)
            system_load_mw: Carga del sistema (MW)
        
        Returns:
            dict: {
                'active_stages': set de etapas activas,
                'total_load_shed_mw': MW a desconectar,
                'affected_zones': zonas afectadas,
                'action_required': bool
            }
        """
        
        self.frequency_history.append(current_frequency)
        
        # Detectar qué etapas se deben activar
        new_active_stages = set()
        total_shed = 0
        affected_zones = []
        
        for stage_num, stage_config in sorted(UFLS_STAGES.items()):
            if current_frequency <= stage_config['frequency']:
                new_active_stages.add(stage_num)
                load_shed_percent = stage_config['load_shed_percent']
                total_shed = (system_load_mw * load_shed_percent) / 100
                affected_zones.extend(stage_config['zones'])
        
        # Comparar con estado anterior
        action_required = new_active_stages != self.active_stages
        
        self.active_stages = new_active_stages
        self.total_load_shed_mw = total_shed
        self.affected_zones = list(set(affected_zones))  # Remover duplicados
        
        return {
            'active_stages': self.active_stages,
            'total_load_shed_mw': total_shed,
            'affected_zones': self.affected_zones,
            'action_required': action_required,
            'load_shed_percent': (total_shed / system_load_mw * 100) if system_load_mw > 0 else 0,
        }
    
    def calculate_zone_disconnections(self, total_load_mw):
        """
        Calcula desconexiones por zona
        
        Args:
            total_load_mw: Carga total del sistema (MW)
        
        Returns:
            DataFrame con desconexiones por zona
        """
        
        data = []
        
        for zone in self.affected_zones:
            # Estimar carga de la zona
            zone_data = SNI_ZONES.get(zone, {})
            population_share = zone_data.get('population_millions', 1.0) / 12.0  # Total ~12M
            zone_load = total_load_mw * population_share
            
            # Desconexión por zona (puede ser parcial si es última etapa)
            load_to_shed = (total_load_mw * 0.15) / len(self.affected_zones)  # 15% distribuido
            
            data.append({
                'zone': zone,
                'population_millions': zone_data.get('population_millions', 1.0),
                'estimated_zone_load_mw': zone_load,
                'load_to_disconnect_mw': load_to_shed,
                'estimated_people_affected': int(zone_data.get('population_millions', 1.0) * 1_000_000),
            })
        
        return pd.DataFrame(data)
    
    def get_ufls_status_string(self):
        """Retorna descripción textual del estado UFLS"""
        
        if not self.active_stages:
            return "✅ SISTEMA ESTABLE - Sin alivio de carga activo"
        
        stages_list = sorted(self.active_stages)
        return f"⚠️  UFLS ACTIVADO - Etapas: {stages_list} | MW desconectados: {self.total_load_shed_mw:.0f}"
    
    def record_shedding_event(self, timestamp, frequency, deficit_mw, zones_affected):
        """Registra evento de UFLS para auditoría"""
        
        self.shedding_history.append({
            'timestamp': timestamp,
            'frequency': frequency,
            'deficit_mw': deficit_mw,
            'zones_affected': zones_affected,
            'active_stages': list(self.active_stages),
            'load_shed_mw': self.total_load_shed_mw,
        })
    
    def get_shedding_history_df(self):
        """Retorna historial de eventos como DataFrame"""
        return pd.DataFrame(self.shedding_history)
    
    def reset(self):
        """Resetea el estado del UFLS"""
        self.active_stages = set()
        self.total_load_shed_mw = 0
        self.affected_zones = []


class BlackoutRiskAssessment:
    """Evalúa riesgo de apagón total del sistema"""
    
    # Criterios de riesgo (variables de decisión)
    CRITICAL_THRESHOLDS = {
        'frequency_critical': 58.5,      # Hz - punto sin retorno
        'voltage_critical': 0.85,         # pu
        'deficit_critical_percent': 20,   # % de la demanda
        'time_to_blackout_seconds': 30,   # Tiempo para estabilizar
    }
    
    @staticmethod
    def assess_risk(current_frequency, voltage_pu, deficit_mw, total_load_mw, 
                    generation_ramping_capability_mw_per_min=100):
        """
        Evalúa riesgo de apagón a partir de múltiples parámetros
        
        Args:
            current_frequency: Frecuencia actual (Hz)
            voltage_pu: Voltaje en por unidad
            deficit_mw: Déficit de potencia (MW)
            total_load_mw: Carga total (MW)
            generation_ramping_capability_mw_per_min: Velocidad de ramping de generación
        
        Returns:
            dict: {
                'risk_level': 'GREEN'|'YELLOW'|'RED'|'CRITICAL',
                'risk_score': float (0-100),
                'time_to_blackout_seconds': float,
                'recovery_actions': list
            }
        """
        
        risk_factors = []
        risk_score = 0
        
        # Factor 1: Desviación de frecuencia
        freq_deviation = abs(60.0 - current_frequency)
        if freq_deviation > 1.0:
            risk_factors.append('Desviación de frecuencia > 1.0 Hz')
            risk_score += 30
        elif freq_deviation > 0.5:
            risk_score += 15
        
        # Factor 2: Voltaje
        if voltage_pu < BlackoutRiskAssessment.CRITICAL_THRESHOLDS['voltage_critical']:
            risk_factors.append('Voltaje crítico')
            risk_score += 35
        elif voltage_pu < 0.90:
            risk_score += 20
        
        # Factor 3: Déficit de potencia
        deficit_percent = (deficit_mw / total_load_mw * 100) if total_load_mw > 0 else 0
        if deficit_percent > 15:
            risk_factors.append(f'Déficit alto: {deficit_percent:.1f}%')
            risk_score += 25
        elif deficit_percent > 5:
            risk_score += 10
        
        # Factor 4: Capacidad de ramping
        recovery_time_minutes = deficit_mw / max(generation_ramping_capability_mw_per_min, 1)
        if recovery_time_minutes > 5:
            risk_factors.append(f'Lenta recuperación: {recovery_time_minutes:.1f} min')
            risk_score += 15
        
        # Cálculo de tiempo a apagón
        FREQUENCY_DECAY = 0.1  # Hz/s bajo déficit severo
        time_to_blackout = (current_frequency - 58.5) / FREQUENCY_DECAY
        
        # Determinar nivel de riesgo
        if risk_score >= 75 or current_frequency < 59.0:
            risk_level = 'CRITICAL'
        elif risk_score >= 50 or current_frequency < 59.3:
            risk_level = 'RED'
        elif risk_score >= 25 or deficit_percent > 10:
            risk_level = 'YELLOW'
        else:
            risk_level = 'GREEN'
        
        return {
            'risk_level': risk_level,
            'risk_score': min(100, risk_score),
            'risk_factors': risk_factors,
            'time_to_blackout_seconds': max(0, time_to_blackout),
            'deficit_percent': deficit_percent,
            'recovery_actions': BlackoutRiskAssessment._get_recovery_actions(
                deficit_percent, current_frequency, risk_level
            ),
        }
    
    @staticmethod
    def _get_recovery_actions(deficit_percent, frequency, risk_level):
        """Retorna acciones de recuperación recomendadas"""
        
        actions = []
        
        if risk_level == 'CRITICAL':
            actions.extend([
                '🔴 ALERTA MÁXIMA: Activar UFLS etapa 3',
                '🔴 Desconectar carga no esencial inmediatamente',
                '🔴 Contactar sistema de transmisión regional',
                '🔴 Preparar protocolos de blackout controlado',
            ])
        elif risk_level == 'RED':
            actions.extend([
                '🟠 Activar UFLS etapa 2',
                '🟠 Incrementar generación térmica al máximo',
                '🟠 Monitoreo intensivo de frecuencia',
            ])
        elif risk_level == 'YELLOW':
            actions.extend([
                '🟡 Activar UFLS etapa 1 si es necesario',
                '🟡 Preparar aumento de generación',
                '🟡 Monitoreo normal',
            ])
        else:
            actions.append('✅ Sistema operando en rangos normales')
        
        return actions
