"""
Configuración global para la aplicación SNI Ecuador
"""

# ============ CONSTANTES DEL SISTEMA ============
FREQUENCY_NOMINAL = 60.0  # Hz
FREQUENCY_MIN_SAFE = 59.5  # Hz
FREQUENCY_UFLS_TRIGGER = 59.2  # Hz - Activation point

# Demanda
DEMAND_PEAK_MW = 5000  # MW - Pico histórico
DEMAND_MIN_MW = 2500   # MW - Mínimo estimado

# Generación total disponible
GENERATION_TOTAL_MW = 10955  # GWh

# Composición de generación (%)
GENERATION_MIX = {
    "HIDROELÉCTRICA": 0.743,
    "TÉRMICA": 0.239,
    "RENOVABLE": 0.012,
}

# Tasas de pérdidas económicas
ECONOMIC_LOSS_USD_PER_MWH = 150  # USD por MWh no suministrado

# Zona de cobertura del SNI
SNI_CENTER_LAT = -1.8312
SNI_CENTER_LON = -78.1834
SNI_ZOOM_LEVEL = 6

# ============ PARÁMETROS DE SIMULACIÓN ============
SIMULATION_HOURS = 24
SIMULATION_TIMESTEP = 0.25  # Horas (15 min)
TIME_RESOLUTION = int(SIMULATION_HOURS / SIMULATION_TIMESTEP)

# Frecuencia de actualización de cálculos
FREQUENCY_DECAY_RATE = 0.01  # Hz/s cuando hay déficit
# ============ ESQUEMA UFLS (Under Frequency Load Shedding) ============
UFLS_STAGES = {
    1: {"frequency": 59.5, "load_shed_percent": 5, "zones": ["Zona Norte", "Zona Oriente"]},
    2: {"frequency": 59.3, "load_shed_percent": 10, "zones": ["Zona Central", "Zona Litoral"]},
    3: {"frequency": 59.0, "load_shed_percent": 15, "zones": ["Zona Sur"]},
}

# ============ ZONAS DEL SNI ============
SNI_ZONES = {
    "Zona Norte": {"lat": -0.3, "lon": -78.5, "population_millions": 2.5},
    "Zona Central": {"lat": -1.2, "lon": -78.5, "population_millions": 3.2},
    "Zona Sur": {"lat": -2.9, "lon": -79.0, "population_millions": 2.0},
    "Zona Litoral": {"lat": -2.2, "lon": -80.5, "population_millions": 3.5},
    "Zona Oriente": {"lat": -1.0, "lon": -76.0, "population_millions": 0.8},
}
