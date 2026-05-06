# Simulador del Sistema Nacional Interconectado (SNI) - Ecuador

## 📋 Descripción General

Aplicación GUI interactiva que simula el funcionamiento del Sistema Nacional Interconectado (SNI) de Ecuador. Diseñada para ingenieros de sistemas de potencia, permite analizar balances de generación-demanda, monitorear parámetros críticos de red, y simular esquemas de alivio de carga por baja frecuencia (UFLS).

**Basada en datos históricos reales**:
- Demanda máxima histórica: ~5000 MW (Martes, 14 de abril de 2026)
- Generación: Hidroeléctrica 74.3%, Térmica 23.9%, Renovable 1.8%
- 8 principales centrales hidroeléctricas
- 7 centrales térmicas distribuidas geográficamente

---

## 🏗️ Estructura del Proyecto

```
Matriz_Ener_08_05_2026/
├── app.py                          # Aplicación principal Streamlit
├── config.py                       # Configuración global y constantes
├── requirements.txt                # Dependencias Python
├── README.md                       # Este archivo
│
└── src/
    ├── __init__.py
    ├── data/
    │   ├── __init__.py
    │   ├── power_plants.py        # Base de datos de centrales (MÓDULO 1 & 2)
    │   └── demand_curves.py        # Generación de curvas de demanda
    │
    ├── utils/
    │   ├── __init__.py            # Funciones de cálculo (MÓDULO 3)
    │   ├── calculations.py
    │   └── [FrequencyCalculator, EconomicImpactCalculator, GridStabilityMonitor]
    │
    ├── components/
    │   ├── __init__.py            # Componentes de UI (MÓDULO 1)
    │   └── map_component.py       # Mapa interactivo (MÓDULO 2)
    │
    └── simulators/
        ├── __init__.py            # Motor UFLS y Load Shedding (MÓDULO 4)
        └── [UnderFrequencyLoadShedding, BlackoutRiskAssessment]
```

---

## 🎯 Módulos Implementados

### **MÓDULO 1: Interfaz de Usuario (Dashboard)**
**Archivo**: `src/components/__init__.py` y `app.py`

✅ **Características**:
- Sliders para control de demanda (±30%, ±500 MW)
- Toggles para encender/apagar categorías de generación:
  - Hidroeléctrica
  - Térmica
  - Renovable
- Formulario para añadir nuevas centrales con:
  - Nombre, Tipo de Energía, Capacidad (MW)
  - Latitud/Longitud WGS84
- Panel de métricas KPI en tiempo real

**Clases Principales**:
- `DashboardComponents`: Renderiza gráficos y controles

---

### **MÓDULO 2: Mapa Interactivo y Marcadores**
**Archivo**: `src/components/map_component.py`

✅ **Características**:
- Mapa base de Ecuador centrado en SNI (lat -1.8312, lon -78.1834)
- Marcadores de todas las 15 centrales principales:
  - **Hidroeléctricas**: Coca Codo Sinclair (1500 MW), Paute (1100 MW), Sopladora (487 MW), etc.
  - **Térmicas**: Guayaquil (700 MW), Quito (345 MW), Esmeraldas (290 MW), etc.
  - **Renovables**: Parque Solar Quisapincha, Parque Eólico Balzar, Biomasa Sucumbíos
- Actualización dinámica:
  - Verde (on) → Rojo (off) cuando se desactivan en UI
  - Tamaño del marcador proporcional a capacidad (MW)
  - Zoom automático a centrales personalizadas

**Colores**:
- 🔵 Azul: Hidroeléctrica
- 🟠 Naranja: Térmica
- 🟡 Amarillo: Solar
- 🟢 Verde: Eólica
- ⚫ Gris: Desconectada

**Clases Principales**:
- `InteractiveMapComponent`: Gestiona mapa, marcadores y capas

---

### **MÓDULO 3: Motor de Gráficos e Interpolación**
**Archivo**: `src/data/demand_curves.py` y `src/utils/__init__.py`

✅ **Características**:
- Curva de generación vs demanda en tiempo real (24h)
- Interpolación cúbica suave (CubicSpline de SciPy)
  - Basada en puntos históricos (cada hora)
  - Resolución: 15 minutos (0.25h)
- Generación simulada por tipo:
  - Hidroeléctrica: 90% ± ruido (estable)
  - Térmica: Variable con demanda, pico a las 19:00
  - Solar: Ciclo diurno (6:00-18:00)
  - Eólica: Alta variabilidad
  - Biomasa: Constante ~80%
- Visualización de déficit (relleno rojo cuando Demanda > Generación)

**Clases Principales**:
- `DemandCurveGenerator`: Genera curvas suaves
- `DynamicPlantSimulator`: Simula salida variable de plantas

---

### **MÓDULO 4: Simulador de Impacto y Seguridad (Load Shedding)**
**Archivo**: `src/simulators/__init__.py`

✅ **Características**:

#### **A. Física del Sistema (UFLS)**
- Lógica de alivio de carga por baja frecuencia:
  - **Etapa 1** (59.5 Hz): Desconectar 5% (Zona Norte, Oriente)
  - **Etapa 2** (59.3 Hz): Desconectar 10% adicional (Zona Central, Litoral)
  - **Etapa 3** (59.0 Hz): Desconectar 15% adicional (Zona Sur)
- Cálculo de frecuencia basado en desbalance P = G - D
- Modelo de inercia del sistema: df/dt = K × (Pg - Pd) / Prated

#### **B. Impacto Socioeconómico**
- **Métricas de déficit**:
  - Zonas afectadas (dinámica)
  - Personas afectadas por zona (basado en población)
  - Pérdidas económicas estimadas:
    - Industrial: $5,000/MWh
    - Comercial: $3,000/MWh
    - Residencial: $1,000/MWh
    - Público: $2,000/MWh
- **Evaluación de riesgo**:
  - Score 0-100
  - Niveles: GREEN, YELLOW, RED, CRITICAL
  - Tiempo estimado a blackout
  - Acciones de recuperación recomendadas

**Clases Principales**:
- `UnderFrequencyLoadShedding`: Gestiona UFLS por etapas
- `BlackoutRiskAssessment`: Evalúa riesgo de apagón total
- `EconomicImpactCalculator`: Calcula pérdidas económicas

---

## 🚀 Instalación y Uso

### **Paso 1: Clonar/Navegar al proyecto**
```bash
cd /your_home/SNI_Regulation
```

### **Paso 2: Crear entorno virtual**
```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### **Paso 3: Instalar dependencias**
```bash
pip install -r requirements.txt
```

### **Paso 4: Ejecutar la aplicación**
```bash
streamlit run app.py
```

La aplicación se abrirá en **`http://localhost:8501`**

---

## 📊 Uso de la Aplicación

### **Tab 1: Dashboard Principal**
1. **Slider de Hora**: Selecciona hora del día (0-24)
2. **KPIs**: Visualiza generación, demanda, frecuencia, voltaje
3. **Gráficos**:
   - Composición de generación (pie chart)
   - Generación vs Demanda (area chart)
4. **Información detallada**: Balance de sistema, parámetros de red

### **Tab 2: Mapa Interactivo**
1. **Ubicación de centrales**: Haz click en marcadores para ver info
2. **Estado dinámico**: Verde (on) / Gris (off)
3. **Zonas afectadas**: Resaltadas en rojo si hay UFLS activo
4. **Tabla de detalles**: Descarga de datos de plantas

### **Tab 3: Análisis Detallado**
1. **Curva 24h**: Demanda esperada vs generación disponible
2. **Estadísticas**: Mín, Máx, Promedio
3. **Impacto económico**: Pérdidas por déficit

### **Tab 4: Seguridad & UFLS**
1. **Indicador de riesgo**: Semáforo visual
2. **Factores de riesgo**: Desviaciones de frecuencia, voltaje, etc.
3. **Acciones recomendadas**: Automáticas según riesgo
4. **Estado UFLS**: Etapas activas, MW desconectados
5. **Impacto por zona**: Tabla con personas/pérdidas

---

## 🔧 Parámetros Configurables

Editar en `config.py`:

```python
# Parámetros de frecuencia
FREQUENCY_NOMINAL = 60.0  # Hz
FREQUENCY_MIN_SAFE = 59.5  # Hz
FREQUENCY_UFLS_TRIGGER = 59.2  # Hz

# Demanda
DEMAND_PEAK_MW = 5000  # MW
DEMAND_MIN_MW = 2500   # MW

# Composición de generación
GENERATION_MIX = {
    "HIDROELÉCTRICA": 0.743,  # 74.3%
    "TÉRMICA": 0.239,         # 23.9%
    "RENOVABLE": 0.012,       # 1.8%
}

# Tasas económicas
ECONOMIC_LOSS_USD_PER_MWH = 150

# Esquema UFLS
UFLS_STAGES = {
    1: {"frequency": 59.5, "load_shed_percent": 5, ...},
    2: {"frequency": 59.3, "load_shed_percent": 10, ...},
    3: {"frequency": 59.0, "load_shed_percent": 15, ...},
}
```

---

## 📈 Datos Base Utilizados

### **Demanda (Curva Diaria)**
Basada en el gráfico adjunto "Demanda máxima histórica: Martes, 14 de abril de 2026":
- **Mínima**: ~2600 MW (02:00-04:00)
- **Máxima**: ~5000 MW (17:00-20:00)
- **Promedio**: ~3800 MW

### **Centrales Instaladas (15 plantas)**

#### Hidroeléctricas (8):
1. Coca Codo Sinclair - 1500 MW
2. Paute - 1100 MW
3. Sopladora - 487 MW
4. Agoyán - 156 MW
5. Delsitanisagua - 113 MW
6. Mazar - 160 MW
7. San Francisco - 75 MW
8. Minas San Francisco - 30 MW

#### Térmicas (7):
1. Guayaquil - 700 MW
2. Quito - 345 MW
3. Esmeraldas - 290 MW
4. Machala - 270 MW
5. Salinas - 240 MW
6. Santa Elena - 160 MW
7. Milagro - 165 MW

#### Renovables (3):
1. Parque Solar Quisapincha - 31 MW
2. Parque Eólico Balzar - 20 MW
3. Biomasa Sucumbíos - 9 MW

**Total Instalado**: 10,955 MW

---

## 🔬 Física y Modelos Implementados

### **Cálculo de Frecuencia**
```
df/dt = K × (Pg - Pd) / Prated

Donde:
- Pg: Potencia generada (MW)
- Pd: Potencia demandada (MW)
- K: Constante de inercia (~0.015 Hz/MW)
- Prated: Potencia nominal del sistema
```

### **Criterios de UFLS**
Se activan en cascada cuando la frecuencia cae:
- Etapa 1: f < 59.5 Hz → Desconectar 5%
- Etapa 2: f < 59.3 Hz → Desconectar 10%
- Etapa 3: f < 59.0 Hz → Desconectar 15%

### **Evaluación de Riesgo (0-100)**
- Desviación de frecuencia: 30 pts
- Voltaje crítico: 35 pts
- Déficit de potencia: 25 pts
- Tiempo de recuperación: 15 pts

**Niveles**:
- **GREEN** (0-25): Sistema seguro
- **YELLOW** (25-50): Monitoreo activo
- **RED** (50-75): Acciones recomendadas
- **CRITICAL** (75-100): Riesgo inmediato de blackout

---

## 📝 Notas Técnicas

### **Librerías Principales**
- **Streamlit**: Framework para UI
- **Plotly**: Gráficos interactivos
- **Folium**: Mapas geográficos
- **Pandas/NumPy**: Análisis de datos
- **SciPy**: Interpolación y cálculos científicos

### **Reproducivilidad**
- Todos los gráficos usan semillas aleatorias para variabilidad controlada
- Histórico de simulación disponible en sesión
- Exportación de datos posible (CSV)

### **Escalabilidad Futura**
- Agregar más centrales
- Importar datos en tiempo real de CENACE
- Modelo de flujo de potencia óptimo (OPF)
- Predicción de demanda con ML
- Análisis de contingencias (N-1)

---

## 🤝 Contribuciones

Para reportar bugs o sugerir mejoras, contactar al equipo de ingeniería de sistemas de potencia.

---

## 📄 Licencia

Sistema desarrollado para fines educativos y de investigación.
Información basada en datos públicos del SNI Ecuador.

---

## ✨ Autores

**Grupo 5 - Pablo Cárdenas, Joseph Jaramillo, Anibal Macas & Anthony Pallchisaca**
**Ingenieria en Telecomunicaciones**
**Universidad de Cuenca**
Desarrolladores Senior Python  
Sistema Nacional Interconectado (SNI) - Ecuador  

**Fecha**: Abril 2026  
**Versión**: 1.0.0
