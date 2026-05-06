"""Componentes de la interfaz Streamlit"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta


class DashboardComponents:
    """Componentes reutilizables del dashboard"""
    
    @staticmethod
    def render_kpi_cards(generation_total_mw, demand_mw, frequency, voltage_pu, 
                        deficit_mw, reserve_margin_percent):
        """Renderiza tarjetas KPI principales"""
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.metric(
                "Generación Total",
                f"{generation_total_mw:.0f} MW",
                delta=f"{(generation_total_mw - demand_mw):+.0f} MW"
            )
        
        with col2:
            st.metric(
                "Demanda",
                f"{demand_mw:.0f} MW",
                delta=None
            )
        
        with col3:
            color = "🔴" if frequency < 59.5 else "🟢"
            st.metric(
                "Frecuencia",
                f"{frequency:.2f} Hz",
                delta=f"{(frequency - 60.0):+.2f}",
            )
        
        with col4:
            voltage_delta = (voltage_pu - 1.0) * 100
            st.metric(
                "Voltaje",
                f"{voltage_pu:.3f} pu",
                delta=f"{voltage_delta:+.1f}%"
            )
        
        with col5:
            st.metric(
                "Déficit",
                f"{max(0, deficit_mw):.0f} MW",
                delta=f"{max(0, deficit_mw):.0f}"
            )
        
        with col6:
            st.metric(
                "Margen Operativo",
                f"{reserve_margin_percent:.1f}%",
                delta=None
            )
    
    @staticmethod
    def render_generation_mix_chart(generation_by_type):
        """Gráfico de composición de generación"""
        
        # Preparar datos
        types = list(generation_by_type.keys())
        values = list(generation_by_type.values())
        
        # Colores por tipo
        colors = {
            'Hidroeléctrica': '#3b82f6',
            'Térmica': '#f59e0b',
            'Solar': '#fbbf24',
            'Eólica': '#10b981',
            'Biomasa': '#14b8a6',
        }
        
        fig = go.Figure(data=[
            go.Pie(
                labels=types,
                values=values,
                marker=dict(colors=[colors.get(t, '#808080') for t in types]),
                textposition='inside',
                textinfo='label+percent',
                hovertemplate='<b>%{label}</b><br>%{value:.0f} MW<br>%{percent}<extra></extra>',
            )
        ])
        
        fig.update_layout(
            title="Composición de Generación Actual",
            height=400,
            showlegend=True,
            font=dict(size=11),
        )
        
        return fig
    
    @staticmethod
    def render_generation_vs_demand(hours, generation_curve, demand_curve, 
                                    current_hour=None):
        """Gráfico de generación vs demanda 24h"""
        
        fig = go.Figure()
        
        # Demanda
        fig.add_trace(go.Scatter(
            x=hours,
            y=demand_curve,
            name='Demanda',
            line=dict(color='#ef4444', width=2),
            fill=None,
        ))
        
        # Generación
        fig.add_trace(go.Scatter(
            x=hours,
            y=generation_curve,
            name='Generación',
            line=dict(color='#10b981', width=2),
            fill='tonexty',
            fillcolor='rgba(16, 185, 129, 0.2)',
        ))
        
        # Marcar déficit (si aplica)
        deficit = demand_curve - generation_curve
        deficit_hours = hours[deficit > 0] if np.any(deficit > 0) else []
        if len(deficit_hours) > 0:
            deficit_values = deficit[deficit > 0]
            fig.add_trace(go.Scatter(
                x=deficit_hours,
                y=demand_curve[deficit > 0],
                name='Déficit',
                line=dict(color='#ef4444', width=0),
                fill='tonexty',
                fillcolor='rgba(239, 68, 68, 0.3)',
            ))
        
        # Línea de hora actual
        if current_hour is not None:
            fig.add_vline(
                x=current_hour,
                line_dash='dash',
                line_color='#6366f1',
                annotation_text='Hora Actual',
                annotation_position='top left',
            )
        
        fig.update_layout(
            title='Curva de Generación vs Demanda (24h)',
            xaxis_title='Hora del Día',
            yaxis_title='Potencia (MW)',
            height=400,
            hovermode='x unified',
            legend=dict(yanchor='top', y=0.99, xanchor='right', x=0.99),
            xaxis=dict(tickformat='.0f', ticksuffix='h'),
        )
        
        return fig
    
    @staticmethod
    def render_frequency_timeline(frequency_history, time_points):
        """Gráfico de evolución de frecuencia"""
        
        fig = go.Figure()
        
        # Frecuencia
        fig.add_trace(go.Scatter(
            x=time_points,
            y=frequency_history,
            name='Frecuencia',
            line=dict(color='#3b82f6', width=2),
            mode='lines',
        ))
        
        # Líneas de referencia
        fig.add_hline(
            y=60.0,
            line_dash='dash',
            line_color='#10b981',
            annotation_text='Nominal (60 Hz)',
            annotation_position='right',
        )
        
        fig.add_hline(
            y=59.5,
            line_dash='dash',
            line_color='#f59e0b',
            annotation_text='Alerta (59.5 Hz)',
            annotation_position='right',
        )
        
        fig.add_hline(
            y=59.2,
            line_dash='dash',
            line_color='#ef4444',
            annotation_text='UFLS Trigger (59.2 Hz)',
            annotation_position='right',
        )
        
        fig.update_layout(
            title='Evolución de Frecuencia del Sistema',
            xaxis_title='Tiempo',
            yaxis_title='Frecuencia (Hz)',
            height=350,
            hovermode='x unified',
            yaxis=dict(range=[58.0, 61.0]),
        )
        
        return fig
    
    @staticmethod
    def render_zone_impact_table(zone_data):
        """Tabla de impacto por zona"""
        
        df_display = zone_data.copy()
        df_display['load_to_disconnect_mw'] = df_display['load_to_disconnect_mw'].round(0).astype(int)
        df_display['estimated_zone_load_mw'] = df_display['estimated_zone_load_mw'].round(0).astype(int)
        
        return df_display[['zone', 'population_millions', 'estimated_zone_load_mw', 
                          'load_to_disconnect_mw', 'estimated_people_affected']]
    
    @staticmethod
    def render_control_panel():
        """Panel de controles de simulación"""
        
        st.sidebar.markdown("## Controles del Sistema")
        
        # Controles de generación
        st.sidebar.markdown("### Estado de Centrales")
        
        hydroelectric_enabled = st.sidebar.toggle(
            "Hidroeléctrica",
            value=True,
            key="hydro_enabled"
        )
        
        thermal_enabled = st.sidebar.toggle(
            "Térmica",
            value=True,
            key="thermal_enabled"
        )
        
        renewable_enabled = st.sidebar.toggle(
            "Renovable",
            value=True,
            key="renewable_enabled"
        )
        
        # Ajuste de demanda
        st.sidebar.markdown("### Ajuste de Demanda")
        
        demand_adjustment = st.sidebar.slider(
            "Cambio de Demanda (%)",
            min_value=-30,
            max_value=+30,
            value=0,
            step=1,
            key="demand_adjustment"
        )
        
        demand_mw_adjustment = st.sidebar.number_input(
            "Cambio de Demanda (MW)",
            min_value=-500,
            max_value=+500,
            value=0,
            step=50,
            key="demand_mw_adjustment"
        )
        
        # Añadir nueva central
        st.sidebar.markdown("### ➕ Añadir Nueva Central")
        
        with st.sidebar.expander("Formulario"):
            plant_name = st.text_input("Nombre de la Central", key="new_plant_name")
            plant_type = st.selectbox(
                "Tipo de Energía",
                ["Hidroeléctrica", "Térmica", "Solar", "Eólica", "Biomasa"],
                key="new_plant_type"
            )
            capacity_mw = st.number_input(
                "Capacidad (MW)",
                min_value=1,
                max_value=2000,
                value=100,
                step=10,
                key="new_plant_capacity"
            )
            latitude = st.number_input(
                "Latitud (WGS84)",
                min_value=-6.0,
                max_value=2.0,
                value=-1.8,
                step=0.1,
                key="new_plant_lat"
            )
            longitude = st.number_input(
                "Longitud (WGS84)",
                min_value=-82.0,
                max_value=-75.0,
                value=-78.0,
                step=0.1,
                key="new_plant_lon"
            )
            
            add_plant_btn = st.button("Agregar Central", key="add_plant")
        
        return {
            'hydroelectric_enabled': hydroelectric_enabled,
            'thermal_enabled': thermal_enabled,
            'renewable_enabled': renewable_enabled,
            'demand_adjustment_percent': demand_adjustment,
            'demand_adjustment_mw': demand_mw_adjustment,
            'new_plant': {
                'name': plant_name,
                'type': plant_type,
                'capacity_mw': capacity_mw,
                'latitude': latitude,
                'longitude': longitude,
                'add': add_plant_btn,
            }
        }
