"""Componente de mapa interactivo con Folium"""

import folium
from folium.plugins import MarkerCluster
import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
from config import SNI_CENTER_LAT, SNI_CENTER_LON, SNI_ZOOM_LEVEL


class InteractiveMapComponent:
    """Mapa interactivo de Ecuador con centrales de generación"""
    
    # Colores por tipo de central
    PLANT_COLORS = {
        'Hidroeléctrica': '#3b82f6',      # Azul
        'Térmica': '#f59e0b',             # Naranja
        'Solar': '#fbbf24',               # Amarillo
        'Eólica': '#10b981',              # Verde
        'Biomasa': '#14b8a6',             # Turquesa
    }
    
    @staticmethod
    def create_base_map():
        """Crea mapa base de Ecuador"""
        
        m = folium.Map(
            location=[SNI_CENTER_LAT, SNI_CENTER_LON],
            zoom_start=SNI_ZOOM_LEVEL,
            tiles='OpenStreetMap'
        )
        
        # Agregar título
        title_html = '''
        <div style="position: fixed; 
                    top: 10px; left: 50px; width: 300px; height: 60px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:16px; font-weight: bold; padding: 10px">
            🗺️ Sistema Nacional Interconectado (SNI) - Ecuador
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        return m
    
    @staticmethod
    def add_plants_to_map(m, df_plants, status_map=None, highlight_plant=None):
        """
        Agrega marcadores de plantas al mapa
        
        Args:
            m: Objeto folium.Map
            df_plants: DataFrame con plantas
            status_map: dict {nombre_planta: bool} para estado on/off
            highlight_plant: nombre de planta a destacar
        """
        
        for idx, row in df_plants.iterrows():
            plant_name = row['name']
            plant_type = row['type']
            capacity = row['capacity_mw']
            latitude = row['latitude']
            longitude = row['longitude']
            
            # Determinar estado (on/off)
            is_active = True
            if status_map:
                is_active = status_map.get(plant_name, True)
            
            # Determinar color
            if highlight_plant == plant_name:
                color = '#ff0000'  # Rojo para destacado
            elif not is_active:
                color = '#808080'  # Gris si está apagado
            else:
                color = InteractiveMapComponent.PLANT_COLORS.get(plant_type, '#999999')
            
            # Icon status
            icon_color = 'red' if not is_active else (
                'red' if highlight_plant == plant_name else 'blue'
            )
            
            # Popup con información
            popup_html = f"""
            <b>{plant_name}</b><br>
            Tipo: {plant_type}<br>
            Capacidad: {capacity} MW<br>
            Estado: {'🟢 ON' if is_active else '🔴 OFF'}<br>
            Lat: {latitude:.4f}<br>
            Lon: {longitude:.4f}
            """
            
            folium.CircleMarker(
                location=[latitude, longitude],
                radius=max(5, min(15, np.log10(capacity) * 3)),
                popup=folium.Popup(popup_html, max_width=250),
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.7 if is_active else 0.3,
                weight=3 if highlight_plant == plant_name else 1,
                tooltip=f"{plant_name}<br>{capacity} MW",
            ).add_to(m)
        
        return m
    
    @staticmethod
    def add_zones_to_map(m, zones_data):
        """
        Agrega zonas del SNI al mapa
        
        Args:
            m: Objeto folium.Map
            zones_data: dict con información de zonas
        """
        
        for zone_name, zone_info in zones_data.items():
            lat = zone_info['lat']
            lon = zone_info['lon']
            
            folium.CircleMarker(
                location=[lat, lon],
                radius=20,
                popup=f"<b>{zone_name}</b><br>Pop: {zone_info['population_millions']}M",
                color='#purple',
                fill=False,
                weight=2,
                opacity=0.5,
                tooltip=zone_name,
            ).add_to(m)
        
        return m
    
    @staticmethod
    def render_map(df_plants, status_map=None, highlight_plant=None, 
                   affected_zones=None, show_zones=False):
        """
        Renderiza mapa interactivo completo
        
        Args:
            df_plants: DataFrame con plantas
            status_map: dict de estado de plantas
            highlight_plant: planta a destacar
            affected_zones: zonas afectadas por UFLS
            show_zones: mostrar zonas del SNI
        
        Returns:
            Objeto folium.Map
        """
        
        m = InteractiveMapComponent.create_base_map()
        
        # Agregar plantas
        m = InteractiveMapComponent.add_plants_to_map(
            m, df_plants, status_map, highlight_plant
        )
        
        # Agregar zonas si es necesario
        if show_zones:
            from config import SNI_ZONES
            m = InteractiveMapComponent.add_zones_to_map(m, SNI_ZONES)
            
            # Resaltar zonas afectadas
            if affected_zones:
                for zone_name in affected_zones:
                    if zone_name in SNI_ZONES:
                        zone_info = SNI_ZONES[zone_name]
                        folium.CircleMarker(
                            location=[zone_info['lat'], zone_info['lon']],
                            radius=25,
                            popup=f"<b>ZONA AFECTADA: {zone_name}</b>",
                            color='#ff0000',
                            fill=True,
                            fillColor='#ff0000',
                            fillOpacity=0.4,
                            weight=3,
                        ).add_to(m)
        
        # Agregar leyenda
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; right: 10px; width: 200px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:12px; padding: 10px">
            <p style="margin:0"><b>Leyenda</b></p>
            <p style="margin:5px 0"><span style="color:#3b82f6">●</span> Hidroeléctrica</p>
            <p style="margin:5px 0"><span style="color:#f59e0b">●</span> Térmica</p>
            <p style="margin:5px 0"><span style="color:#fbbf24">●</span> Solar</p>
            <p style="margin:5px 0"><span style="color:#10b981">●</span> Eólica</p>
            <p style="margin:5px 0"><span style="color:#808080">●</span> Desconectada</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        return m
