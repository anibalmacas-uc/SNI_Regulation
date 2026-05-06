"""
SIMULADOR DEL SISTEMA NACIONAL INTERCONECTADO (SNI) - ECUADOR
Aplicación Streamlit interactiva para simular el funcionamiento de la red eléctrica

Autor: Sistema de Potencia
Fecha: 2026
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Agregar rutas
sys.path.insert(0, os.path.dirname(__file__))

# Importar módulos
from config import (
    FREQUENCY_NOMINAL, FREQUENCY_UFLS_TRIGGER, GENERATION_MIX,
    SNI_CENTER_LAT, SNI_CENTER_LON, SNI_ZONES, SIMULATION_HOURS
)
from src.data.power_plants import PowerPlantDatabase, DynamicPlantSimulator
from src.data.demand_curves import DemandCurveGenerator, DemandAdjuster
from src.utils import FrequencyCalculator, EconomicImpactCalculator, GridStabilityMonitor
from src.simulators import UnderFrequencyLoadShedding, BlackoutRiskAssessment
from src.components import DashboardComponents
from src.components.map_component import InteractiveMapComponent
from streamlit_folium import st_folium


# ============ CONFIGURACIÓN DE PÁGINA ============
st.set_page_config(
    page_title="SNI Ecuador - Simulador",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ ESTILOS CSS ============
st.markdown("""
<style>
    .title-main {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1e40af;
        margin-bottom: 10px;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #64748b;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #f8fafc;
        border-left: 4px solid #3b82f6;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .alert-critical {
        background-color: #fee2e2;
        border-left: 4px solid #dc2626;
        padding: 15px;
        border-radius: 5px;
    }
    .alert-warning {
        background-color: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 15px;
        border-radius: 5px;
    }
    .alert-success {
        background-color: #dcfce7;
        border-left: 4px solid #16a34a;
        padding: 15px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ============ INICIALIZACIÓN DE ESTADO ============
def initialize_session_state():
    """Inicializa variables de sesión"""
    
    if 'plants_data' not in st.session_state:
        st.session_state.plants_data = PowerPlantDatabase.export_as_dataframe()
    
    if 'custom_plants' not in st.session_state:
        st.session_state.custom_plants = []
    
    if 'simulation_hour' not in st.session_state:
        st.session_state.simulation_hour = 14  # 14:00 (pico)
    
    if 'frequency_history' not in st.session_state:
        st.session_state.frequency_history = []
    
    if 'ufls_simulator' not in st.session_state:
        st.session_state.ufls_simulator = UnderFrequencyLoadShedding()
    
    if 'generation_by_type' not in st.session_state:
        st.session_state.generation_by_type = {}
    
    if 'demand_curve_24h' not in st.session_state:
        curve_data = DemandCurveGenerator.generate_smooth_24h_curve()
        st.session_state.demand_curve_24h = curve_data['demand']
        st.session_state.demand_hours_24h = curve_data['hours']

initialize_session_state()


# ============ FUNCIONES PRINCIPALES ============
def calculate_current_generation(plants_df, adjustment_factors):
    """Calcula generación total actual por tipo"""
    
    generation = {
        'Hidroeléctrica': 0,
        'Térmica': 0,
        'Solar': 0,
        'Eólica': 0,
        'Biomasa': 0,
    }
    
    for _, plant in plants_df.iterrows():
        plant_type = plant['type']
        capacity = plant['capacity_mw']
        
        # Obtener factor de ajuste
        factor = adjustment_factors.get(plant['name'], 0.85)
        
        generation[plant_type] += capacity * factor
    
    return generation


def simulate_system_state(hour, demand_adjustment_percent=0, demand_adjustment_mw=0,
                         generation_factors=None, affected_zones_list=None):
    """
    Simula el estado del sistema en una hora específica
    
    Returns:
        dict: Estado del sistema
    """
    
    if generation_factors is None:
        generation_factors = {}
    
    # Demanda
    demand_base = st.session_state.demand_curve_24h[int(hour * 4)]  # Cada 0.25h
    demand_adjusted = demand_base * (1 + demand_adjustment_percent/100) + demand_adjustment_mw
    demand_adjusted = max(0, demand_adjusted)
    
    # Generación
    generation_by_type = calculate_current_generation(
        st.session_state.plants_data, 
        generation_factors
    )
    
    total_generation = sum(generation_by_type.values())
    
    # Frecuencia
    current_frequency = FrequencyCalculator.calculate_frequency_deviation(
        total_generation, demand_adjusted, FREQUENCY_NOMINAL
    )
    
    # Voltaje (simplificado)
    voltage_pu = 1.0 - abs(total_generation - demand_adjusted) / 10000
    voltage_pu = max(0.85, min(1.15, voltage_pu))
    
    # Déficit
    deficit_mw = max(0, demand_adjusted - total_generation)
    
    # UFLS
    ufls_status = st.session_state.ufls_simulator.evaluate_ufls(
        current_frequency, 
        demand_adjusted
    )
    
    # Riesgo de blackout
    risk_assessment = BlackoutRiskAssessment.assess_risk(
        current_frequency,
        voltage_pu,
        deficit_mw,
        demand_adjusted
    )
    
    # Margen operativo
    reserve_margin = ((total_generation - demand_adjusted) / total_generation * 100) if total_generation > 0 else 0
    
    return {
        'hour': hour,
        'demand': demand_adjusted,
        'generation_total': total_generation,
        'generation_by_type': generation_by_type,
        'frequency': current_frequency,
        'voltage': voltage_pu,
        'deficit': deficit_mw,
        'reserve_margin': reserve_margin,
        'ufls_status': ufls_status,
        'risk_assessment': risk_assessment,
    }


# ============ HEADER ============
col_title1, col_title2 = st.columns([3, 1])

with col_title1:
    st.markdown('<div class="title-main">SNI Ecuador - Simulador de Sistema de Potencia</div>', 
                unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Demanda máxima histórica: Martes, 14 de abril de 2026 (~5000 MW)</div>', 
                unsafe_allow_html=True)

with col_title2:
    st.metric("Fecha de Simulación", "14 Abril 2026", "Martes")

st.divider()


# ============ PANEL DE CONTROL ============
controls = DashboardComponents.render_control_panel()

# Procesar inputs del usuario
generation_factors = {}
plants_active = []

# Aplicar estado de centrales
for _, plant in st.session_state.plants_data.iterrows():
    plant_type = plant['type']
    capacity = plant['capacity_mw']
    
    # Determinar si está habilitada
    is_enabled = True
    if plant_type == 'Hidroeléctrica' and not controls['hydroelectric_enabled']:
        is_enabled = False
    elif plant_type == 'Térmica' and not controls['thermal_enabled']:
        is_enabled = False
    elif plant_type in ['Solar', 'Eólica', 'Biomasa'] and not controls['renewable_enabled']:
        is_enabled = False
    
    factor = 0.85 if is_enabled else 0  # 85% de capacidad si está habilitada
    generation_factors[plant['name']] = factor
    
    if is_enabled:
        plants_active.append(plant['name'])

# ============ SECCIONES PRINCIPALES ============
tab1, tab2, tab3, tab4 = st.tabs([
    "Dashboard Principal", 
    "Mapa Interactivo", 
    "Análisis Detallado",
    "Seguridad & UFLS"
])

# ============ TAB 1: DASHBOARD PRINCIPAL ============
with tab1:
    
    # Controles de hora
    col_time1, col_time2 = st.columns([3, 1])
    
    with col_time1:
        simulation_hour = st.slider(
            "Selecciona la hora de simulación (24h)",
            min_value=0.0,
            max_value=23.75,
            value=float(st.session_state.simulation_hour),
            step=0.25,
            format="%.2f",
            key="hour_slider"
        )
        st.session_state.simulation_hour = simulation_hour
    
    with col_time2:
        hour_int = int(simulation_hour)
        hour_min = int((simulation_hour - hour_int) * 60)
        st.info(f"{hour_int:02d}:{hour_min:02d}")
    
    st.divider()
    
    # Simular estado del sistema
    system_state = simulate_system_state(
        simulation_hour,
        demand_adjustment_percent=controls['demand_adjustment_percent'],
        demand_adjustment_mw=controls['demand_adjustment_mw'],
        generation_factors=generation_factors
    )
    
    # KPIs
    DashboardComponents.render_kpi_cards(
        system_state['generation_total'],
        system_state['demand'],
        system_state['frequency'],
        system_state['voltage'],
        system_state['deficit'],
        system_state['reserve_margin']
    )
    
    st.divider()
    
    # Gráficos principales
    col_pie, col_gen_demand = st.columns(2)
    
    with col_pie:
        fig_mix = DashboardComponents.render_generation_mix_chart(
            system_state['generation_by_type']
        )
        st.plotly_chart(fig_mix, use_container_width=True, key='chart_generation_mix')
    
    with col_gen_demand:
        fig_gen_dem = DashboardComponents.render_generation_vs_demand(
            st.session_state.demand_hours_24h,
            np.ones(len(st.session_state.demand_hours_24h)) * system_state['generation_total'],
            st.session_state.demand_curve_24h * (
                1 + controls['demand_adjustment_percent']/100
            ) + controls['demand_adjustment_mw'],
            current_hour=simulation_hour
        )
        st.plotly_chart(fig_gen_dem, use_container_width=True, key='chart_generation_vs_demand')
    
    st.divider()
    
    # Información de generación
    col_info1, col_info2, col_info3 = st.columns(3)
    
    with col_info1:
        st.markdown("### Generación por Tipo")
        for gen_type, value in system_state['generation_by_type'].items():
            if value > 0:
                pct = (value / system_state['generation_total'] * 100) if system_state['generation_total'] > 0 else 0
                st.write(f"**{gen_type}**: {value:.0f} MW ({pct:.1f}%)")
    
    with col_info2:
        st.markdown("### Balance del Sistema")
        st.write(f"**Generación**: {system_state['generation_total']:.0f} MW")
        st.write(f"**Demanda**: {system_state['demand']:.0f} MW")
        st.write(f"**Balance**: {(system_state['generation_total'] - system_state['demand']):+.0f} MW")
        st.write(f"**Margen**: {system_state['reserve_margin']:.1f}%")
    
    with col_info3:
        st.markdown("### Parámetros de Red")
        st.write(f"**Frecuencia**: {system_state['frequency']:.3f} Hz")
        st.write(f"**Desv. Frecuencia**: {(system_state['frequency'] - 60.0):+.3f} Hz")
        st.write(f"**Voltaje**: {system_state['voltage']:.3f} pu")
        st.write(f"**Déficit**: {system_state['deficit']:.0f} MW")


# ============ TAB 2: MAPA INTERACTIVO ============
with tab2:
    
    st.markdown("### Ubicación de Centrales del SNI")
    st.info("""
    - **Azul**: Hidroeléctrica
    - **Naranja**: Térmica  
    - **Amarillo**: Solar
    - **Verde**: Eólica
    - **Gris**: Desconectada
    """)
    
    # Preparar datos para mapa
    df_plants_display = st.session_state.plants_data.copy()
    
    # Estado de plantas
    status_map = {}
    for _, plant in df_plants_display.iterrows():
        plant_name = plant['name']
        plant_type = plant['type']
        
        is_enabled = generation_factors.get(plant_name, 0) > 0
        status_map[plant_name] = is_enabled
    
    # Renderizar mapa
    map_obj = InteractiveMapComponent.render_map(
        df_plants_display,
        status_map=status_map,
        affected_zones=system_state['ufls_status'].get('affected_zones', []),
        show_zones=True
    )
    
    map_data = st_folium(map_obj, width=1400, height=600)
    
    st.markdown("---")
    
    # Tabla de plantas
    st.markdown("### Detalle de Centrales")
    
    df_display = df_plants_display[[
        'name', 'type', 'capacity_mw', 'latitude', 'longitude', 'status'
    ]].copy()
    
    df_display['estado_simulación'] = df_display['name'].apply(
        lambda x: '🟢 ON' if status_map.get(x, False) else '🔴 OFF'
    )
    
    df_display['factor_generación'] = df_display['name'].apply(
        lambda x: f"{generation_factors.get(x, 0)*100:.0f}%"
    )
    
    st.dataframe(
        df_display[[
            'name', 'type', 'capacity_mw', 'estado_simulación', 'factor_generación'
        ]].rename(columns={
            'name': 'Central',
            'type': 'Tipo',
            'capacity_mw': 'Capacidad (MW)',
            'estado_simulación': 'Estado',
            'factor_generación': 'Factor Gen'
        }),
        use_container_width=True,
        hide_index=True
    )


# ============ TAB 3: ANÁLISIS DETALLADO ============
with tab3:
    
    st.markdown("###Análisis Temporal (24 horas)")
    
    # Generar curva 24h con condiciones actuales
    hours = st.session_state.demand_hours_24h
    demand_24h = st.session_state.demand_curve_24h * (
        1 + controls['demand_adjustment_percent']/100
    ) + controls['demand_adjustment_mw']
    
    # Generación aproximada 24h
    generation_24h = np.ones_like(hours) * system_state['generation_total']
    
    # Gráfico
    fig_24h = DashboardComponents.render_generation_vs_demand(
        hours, generation_24h, demand_24h, current_hour=simulation_hour
    )
    st.plotly_chart(fig_24h, use_container_width=True, key='chart_24h_analysis')
    
    st.divider()
    
    # Estadísticas
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    
    with col_stat1:
        st.markdown("#### Demanda")
        st.metric("Mínima", f"{demand_24h.min():.0f} MW")
        st.metric("Máxima", f"{demand_24h.max():.0f} MW")
        st.metric("Promedio", f"{demand_24h.mean():.0f} MW")
    
    with col_stat2:
        st.markdown("#### Generación (Actual)")
        st.metric("Capacidad Instalada", f"{system_state['generation_total']:.0f} MW")
        st.metric("Factor de Carga", f"{(system_state['generation_total']/df_plants_display['capacity_mw'].sum()*100):.1f}%")
    
    with col_stat3:
        st.markdown("#### Brechas")
        max_gap = (demand_24h.max() - system_state['generation_total'])
        st.metric("Máx. Déficit Potencial", f"{max(0, max_gap):.0f} MW")
        st.metric("Horas Críticas", f"{np.sum(demand_24h > system_state['generation_total'])}")
    
    st.divider()
    
    # Tabla de costos económicos
    st.markdown("####Impacto Económico")
    
    if system_state['deficit'] > 0:
        hourly_loss = EconomicImpactCalculator.calculate_deficit_loss(
            system_state['deficit'],
            duration_hours=1.0
        )
        
        st.warning(f"""
        **Déficit Actual**: {system_state['deficit']:.0f} MW
        
        **Pérdidas Económicas por hora**: ${hourly_loss:,.0f} USD
        
        **Pérdidas económicas 24h**: ${hourly_loss * 24:,.0f} USD
        """)
    else:
        st.success("No hay déficit de generación - Sistema en balance")


# ============ TAB 4: SEGURIDAD & UFLS ============
with tab4:
    
    st.markdown("### Estabilidad del Sistema y Esquema UFLS")
    
    # Mostrar estado de riesgo
    risk_level = system_state['risk_assessment']['risk_level']
    risk_score = system_state['risk_assessment']['risk_score']
    risk_factors = system_state['risk_assessment']['risk_factors']
    
    if risk_level == 'CRITICAL':
        st.error(f"🔴 **ESTADO CRÍTICO** - Riesgo: {risk_score:.0f}%")
    elif risk_level == 'RED':
        st.warning(f"🟠 **ESTADO ROJO** - Riesgo: {risk_score:.0f}%")
    elif risk_level == 'YELLOW':
        st.warning(f"🟡 **ESTADO AMARILLO** - Riesgo: {risk_score:.0f}%")
    else:
        st.success(f"✅ **ESTADO VERDE** - Riesgo: {risk_score:.0f}%")
    
    st.divider()
    
    # Detalles del riesgo
    col_risk1, col_risk2 = st.columns(2)
    
    with col_risk1:
        st.markdown("#### Factores de Riesgo")
        for factor in risk_factors:
            st.write(f"• {factor}")
    
    with col_risk2:
        st.markdown("#### Acciones Recomendadas")
        for action in system_state['risk_assessment']['recovery_actions']:
            st.write(action)
    
    st.divider()
    
    # Estado UFLS
    st.markdown("#### Esquema UFLS (Under Frequency Load Shedding)")
    
    ufls_status = system_state['ufls_status']
    ufls_status_str = st.session_state.ufls_simulator.get_ufls_status_string()
    
    st.info(ufls_status_str)
    
    if ufls_status['active_stages']:
        st.markdown(f"**Etapas Activas**: {sorted(ufls_status['active_stages'])}")
        st.markdown(f"**MW Desconectados**: {ufls_status['total_load_shed_mw']:.0f}")
        st.markdown(f"**% de Carga Desconectada**: {ufls_status['load_shed_percent']:.1f}%")
        
        # Zonas afectadas
        if ufls_status['affected_zones']:
            st.markdown("**Zonas Afectadas**:")
            
            # Calcular impacto por zona
            zone_impact = EconomicImpactCalculator.calculate_zone_impact(
                ufls_status['total_load_shed_mw'],
                ufls_status['affected_zones'],
                {zone: SNI_ZONES[zone]['population_millions'] for zone in ufls_status['affected_zones']}
            )
            
            st.dataframe(
                zone_impact[[
                    'zone', 'people_affected', 'estimated_economic_loss_usd'
                ]].rename(columns={
                    'zone': 'Zona',
                    'people_affected': 'Personas Afectadas',
                    'estimated_economic_loss_usd': 'Pérdida Económica (USD)'
                }),
                use_container_width=True,
                hide_index=True
            )
            
            # Resumen
            total_people = zone_impact['people_affected'].sum()
            total_loss = zone_impact['estimated_economic_loss_usd'].sum()
            
            st.error(f"""
            **IMPACTO TOTAL**:
            - Personas afectadas: {total_people:,}
            - Pérdida económica por hora: ${total_loss:,.0f}
            """)
    
    else:
        st.success("UFLS inactivo - Sistema en operación normal")
    
    st.divider()
    
    # Parámetros críticos
    st.markdown("#### Parámetros Críticos del Sistema")
    
    col_param1, col_param2, col_param3 = st.columns(3)
    
    with col_param1:
        st.metric(
            "Frecuencia",
            f"{system_state['frequency']:.3f} Hz",
            f"{(system_state['frequency'] - 60.0):+.3f}",
            delta_color="inverse"
        )
    
    with col_param2:
        st.metric(
            "Voltaje",
            f"{system_state['voltage']:.3f} pu",
            f"{(system_state['voltage'] - 1.0)*100:+.1f}%",
            delta_color="inverse"
        )
    
    with col_param3:
        time_to_blackout = system_state['risk_assessment']['time_to_blackout_seconds']
        if time_to_blackout == float('inf'):
            st.metric("Tiempo a Blackout", "∞ (Seguro)")
        else:
            st.metric("Tiempo a Blackout", f"{time_to_blackout:.0f}s" if time_to_blackout > 0 else "EN CRISIS")


# ============ FOOTER ============
st.divider()

col_footer1, col_footer2, col_footer3 = st.columns(3)

with col_footer1:
    st.caption("**Simulador SNI Ecuador**")

with col_footer2:
    st.caption(f"Simulación: {int(simulation_hour):02d}:{int((simulation_hour % 1) * 60):02d}")
    st.caption(f"Última actualización: {datetime.now().strftime('%H:%M:%S')}")

with col_footer3:
    st.caption("Sistema Nacional Interconectado (SNI)")
    st.caption("República del Ecuador")
