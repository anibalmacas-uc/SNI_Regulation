# 🗂️ ÍNDICE DE PROYECTO - SNI Ecuador Simulator

## 📍 Ubicación del Proyecto
```
/home/josssseph/Documents/Tenth_Semester/Regulation/Matriz_Ener_08_05_2026/
```

---

## 📚 Documentación (Lee Primero)

### **Para Empezar Rápido** (5 minutos)
1. 📄 [QUICKSTART.md](QUICKSTART.md) - Guía de inicio rápido
   - Cómo ejecutar la app
   - Cómo usar los controles
   - Escenarios interesantes

### **Documentación Técnica** (30 minutos)
1. 📄 [README.md](README.md) - Documentación completa
   - Estructura del proyecto
   - Explicación de 4 módulos
   - Parámetros configurables
   - Datos base utilizados

2. 📄 [TECHNICAL_SUMMARY.md](TECHNICAL_SUMMARY.md) - Resumen técnico detallado
   - Arquitectura del sistema
   - Modelos implementados
   - Validaciones
   - Mejoras futuras

### **Resumen Ejecutivo** (10 minutos)
1. 📄 [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md) - Resumen ejecutivo
   - Entregables
   - Características implementadas
   - Resultados técnicos
   - Métricas del proyecto

---

## 📁 Estructura de Carpetas

```
.
├── 📄 app.py                          ← INICIA AQUÍ (ejecutar con streamlit)
├── 📄 config.py                       ← Configuración global
├── 📄 requirements.txt                ← Dependencias (pip install)
│
├── 🚀 quickstart.sh                   ← Script Linux/macOS
├── 🚀 quickstart.bat                  ← Script Windows
│
├── 📊 README.md                       ← Documentación principal
├── 📊 QUICKSTART.md                   ← Guía rápida
├── 📊 TECHNICAL_SUMMARY.md            ← Resumen técnico
├── 📊 EXECUTIVE_SUMMARY.md            ← Resumen ejecutivo
├── 📊 INDEX.md                        ← Este archivo
│
└── src/                               ← CÓDIGO MODULAR
    │
    ├── data/                          (Módulo 1 & 2: Datos)
    │   ├── __init__.py
    │   ├── power_plants.py            (15 centrales)
    │   └── demand_curves.py           (Interpolación 24h)
    │
    ├── utils/                         (Módulo 3: Cálculos)
    │   ├── __init__.py                (Física del sistema)
    │   └── calculations.py
    │
    ├── components/                    (Módulo 1 & 2: UI)
    │   ├── __init__.py                (Dashboard components)
    │   └── map_component.py           (Mapa Folium)
    │
    └── simulators/                    (Módulo 4: UFLS)
        └── __init__.py                (UFLS, Riesgo, Load Shedding)
```

---

## ⚡ Inicio Rápido

### Opción 1: Script Automático
```bash
bash quickstart.sh              # Linux/macOS
# o
quickstart.bat                 # Windows
```

### Opción 2: Manual
```bash
python3 -m venv venv
source venv/bin/activate       # (o venv\Scripts\activate en Windows)
pip install -r requirements.txt
streamlit run app.py
```

**URL**: http://localhost:8501

---

## 📊 Módulos Principales

### **MÓDULO 1: Interfaz de Usuario (Dashboard)**
**Ubicación**: `src/components/__init__.py`, `app.py`

✅ Sliders de control  
✅ Toggles on/off  
✅ Formulario de nueva central  
✅ 6 tarjetas KPI  

**Usa en**: `app.py` línea 200+

---

### **MÓDULO 2: Mapa Interactivo**
**Ubicación**: `src/components/map_component.py`

✅ 15 marcadores dinámicos  
✅ Colores por tipo  
✅ Actualización en tiempo real  
✅ Zonas afectadas  

**Usa en**: `app.py` Tab 2 línea 350+

---

### **MÓDULO 3: Gráficos e Interpolación**
**Ubicación**: `src/data/demand_curves.py`, `src/utils/__init__.py`

✅ Interpolación CubicSpline  
✅ Curva 24h suave  
✅ Resolución 15 minutos  
✅ Gráfico de déficit  

**Usa en**: `app.py` Tab 1 y 3

---

### **MÓDULO 4: UFLS y Seguridad**
**Ubicación**: `src/simulators/__init__.py`

✅ Esquema UFLS en cascada  
✅ Cálculo de frecuencia  
✅ Evaluación de riesgo  
✅ Impacto económico  

**Usa en**: `app.py` Tab 4 línea 500+

---

## 🔧 Clases Principales

### Datos
- `PowerPlantDatabase` - Base de datos de 15 centrales
- `DynamicPlantSimulator` - Generación simulada por hora
- `DemandCurveGenerator` - Interpolación suave de demanda
- `DemandAdjuster` - Ajustes de demanda por usuario

### Utilidades
- `FrequencyCalculator` - Cálculo de desviación de frecuencia
- `EconomicImpactCalculator` - Pérdidas económicas en USD
- `PowerFlowAnalyzer` - Análisis de flujos de potencia
- `GridStabilityMonitor` - Monitoreo de estabilidad

### UI
- `DashboardComponents` - Componentes del dashboard (KPIs, gráficos)
- `InteractiveMapComponent` - Mapa Folium con marcadores

### Simuladores
- `UnderFrequencyLoadShedding` - Lógica UFLS (3 etapas)
- `BlackoutRiskAssessment` - Evaluación de riesgo de blackout

---

## 📈 Datos Base

### Centrales Instaladas (10,955 MW)
**Archivo**: `src/data/power_plants.py`

- 8 Hidroeléctricas (8,621 MW | 74.3%)
- 7 Térmicas (2,620 MW | 23.9%)
- 3 Renovables (60 MW | 1.8%)

### Demanda 24h
**Archivo**: `src/data/demand_curves.py`

- Mínima: 2,600 MW (madrugada)
- Máxima: 5,000 MW (atardecer) ← Dato histórico real
- Promedio: 3,800 MW

### Zonas SNI
**Archivo**: `config.py`

- Zona Norte: 2.5M habitantes
- Zona Central: 3.2M habitantes
- Zona Sur: 2.0M habitantes
- Zona Litoral: 3.5M habitantes
- Zona Oriente: 0.8M habitantes

---

## 🔑 Configuración

**Archivo**: `config.py`

### Parámetros Ajustables
```python
FREQUENCY_NOMINAL = 60.0              # Hz
FREQUENCY_UFLS_TRIGGER = 59.2         # Hz
DEMAND_PEAK_MW = 5000                 # MW
ECONOMIC_LOSS_USD_PER_MWH = 150       # USD

# Ver UFLS_STAGES, SNI_ZONES, GENERATION_MIX
```

---

## 🎯 Casos de Uso

### Escenario 1: Normal
- Hora: 12:00
- Estado: ✅ GREEN
- Déficit: 0 MW
- [Ver QUICKSTART.md → Escenario 1]

### Escenario 2: Pico
- Hora: 19:00
- Estado: ✅ GREEN
- Déficit: 0 MW
- [Ver QUICKSTART.md → Escenario 2]

### Escenario 3: Déficit Moderado
- Desactiva: Térmica
- Estado: 🟡 YELLOW → UFLS Etapa 1
- [Ver QUICKSTART.md → Escenario 3]

### Escenario 4: Crisis
- Desactiva: Hidroeléctrica + Térmica
- Estado: 🔴 CRITICAL
- [Ver QUICKSTART.md → Escenario 4]

---

## 📝 Archivos Importantes

### Para Ejecutar
| Archivo | Propósito | Acción |
|---------|----------|--------|
| `app.py` | Aplicación Streamlit | `streamlit run app.py` |
| `quickstart.sh` | Inicio automático | `bash quickstart.sh` |
| `requirements.txt` | Dependencias | `pip install -r requirements.txt` |

### Para Entender
| Archivo | Tema |
|---------|------|
| `README.md` | Documentación completa |
| `QUICKSTART.md` | Guía de inicio |
| `TECHNICAL_SUMMARY.md` | Detalles técnicos |
| `EXECUTIVE_SUMMARY.md` | Resumen ejecutivo |
| `config.py` | Parámetros globales |

### Para Modificar
| Archivo | Qué cambiar |
|---------|-----------|
| `config.py` | Constantes del sistema |
| `src/data/power_plants.py` | Agregar/cambiar centrales |
| `src/components/__init__.py` | Modificar dashboard |
| `app.py` | Lógica principal |

---

## 🐛 Troubleshooting

### "ModuleNotFoundError"
→ Ejecuta: `pip install -r requirements.txt`

### "Port 8501 already in use"
→ Ejecuta: `streamlit run app.py --server.port 8502`

### "Mapa no se carga"
→ Verifica conexión a internet (usa OpenStreetMap)

### "App va lenta"
→ Reduce plantas o data historics en config.py

---

## 📊 Estadísticas

**Código**:
- Archivos Python: 8
- Líneas de código: ~2,274
- Funciones: 50+
- Clases: 12+

**Documentación**:
- Archivos Markdown: 4
- Líneas de documentación: ~1,504
- Diagramas: 5+

**Datos**:
- Centrales: 15
- Datos 24h: 96 puntos
- Zonas: 5
- Parámetros configurables: 20+

---

## ✨ Stack Tecnológico

- **Frontend**: Streamlit (Python UI framework)
- **Gráficos**: Plotly (interactivos), Folium (mapas)
- **Datos**: Pandas (tablas), NumPy (arrays)
- **Matemática**: SciPy (interpolación), NumPy (cálculos)
- **Backend**: Python 3.8+

---

## 🚀 Próximos Pasos

1. Lee: **QUICKSTART.md** (5 minutos)
2. Ejecuta: **quickstart.sh** o **quickstart.bat**
3. Explora: **4 tabs de la aplicación**
4. Personaliza: **config.py** según necesidades
5. Desarrolla: **Agrega nuevas centrales o funcionalidades**

---

## 📞 Soporte

Para preguntas técnicas, consulta:

1. **Documentación**: README.md
2. **Código fuente**: Comentarios en cada función
3. **Configuración**: config.py
4. **Ejemplos**: QUICKSTART.md → Escenarios

---

**Versión**: 1.0.0  
**Última actualización**: Abril 2026  
**Estado**: ✅ Producción  

🎉 **¡Bienvenido al Simulador SNI Ecuador!** 🎉
