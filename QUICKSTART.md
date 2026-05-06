# 🎯 Guía Rápida - SNI Ecuador Simulator

## Inicio Rápido (2 minutos)

### Linux/macOS
```bash
# 1. Navegar al directorio
cd /home/josssseph/Documents/Tenth_Semester/Regulation/Matriz_Ener_08_05_2026

# 2. Ejecutar script de inicio
bash quickstart.sh
```

### Windows
```bash
# 1. Navegar al directorio
cd path\to\Matriz_Ener_08_05_2026

# 2. Ejecutar script
quickstart.bat
```

### Manual (todos los sistemas)
```bash
# 1. Crear entorno virtual
python3 -m venv venv

# 2. Activar
source venv/bin/activate  # Linux/macOS
# o
venv\Scripts\activate  # Windows

# 3. Instalar paquetes
pip install -r requirements.txt

# 4. Ejecutar
streamlit run app.py
```

---

## 🎮 Cómo Usar

### **Paso 1: Dashboard Principal**
1. Abre la app en `http://localhost:8501`
2. Usa el **slider lateral** para cambiar la hora del día
3. Observa cómo cambian los KPIs en tiempo real

### **Paso 2: Controlar Generación**
En el panel lateral ("⚙️ Controles del Sistema"):
- ✅ **Hidroeléctrica**: Toggle on/off (74% de la generación)
- ✅ **Térmica**: Toggle on/off (24% de la generación)
- ✅ **Renovable**: Toggle on/off (2% de la generación)

**Efecto**: Cuando apagas una categoría, disminuye la generación total

### **Paso 3: Ajustar Demanda**
- Usa el slider **"Cambio de Demanda (%)"** para simular ±30%
- O usa el campo **"Cambio de Demanda (MW)"** para ±500 MW

**Efecto**: Afecta directamente el déficit y el riesgo de UFLS

### **Paso 4: Añadir Nueva Central**
1. Expande **"➕ Añadir Nueva Central"**
2. Completa los campos:
   - Nombre: p.ej., "Hidroeléctrica Nueva"
   - Tipo: Hidroeléctrica, Térmica, Solar, Eólica, Biomasa
   - Capacidad: 10-2000 MW
   - Latitud: -6.0 a 2.0 (WGS84)
   - Longitud: -82.0 a -75.0 (WGS84)
3. Click en "✨ Agregar Central"
4. **Verás** la nueva central aparecer en:
   - El mapa (Tab 2)
   - La tabla de detalle
   - La generación total aumenta

---

## 📊 Tabs Explicados

### **Tab 1: 📊 Dashboard Principal**
- **Arriba**: Slider para seleccionar hora (0-23:45)
- **Tarjetas KPI**: Generación, Demanda, Frecuencia, Voltaje, Déficit, Margen
- **Gráfico circular**: Composición de generación actual
- **Gráfico de área**: Generación vs Demanda 24h (línea roja=demanda, relleno verde=generación)
- **Panel de información**: Detalles del balance y parámetros

**🔴 Indicador Crítico**: Si la área roja (déficit) aparece, el sistema tiene falta de generación

### **Tab 2: 🗺️ Mapa Interactivo**
- **Mapa de Ecuador**: Centrado en SNI
- **Marcadores de plantas**:
  - 🔵 Azul = Hidroeléctrica
  - 🟠 Naranja = Térmica
  - 🟡 Amarillo = Solar
  - 🟢 Verde = Eólica
  - ⚫ Gris = Desconectada
- **Tamaño del marcador**: Proporcional a capacidad
- **Click en marcador**: Muestra info (nombre, tipo, MW)
- **Zonas resaltadas en rojo**: Áreas afectadas por UFLS

**💡 Tip**: Si desactivas "Térmica", verás los marcadores naranjas ponerse grises

### **Tab 3: 📈 Análisis Detallado**
- **Gráfico 24h**: Curva de demanda vs generación para todo el día
- **Hora actual**: Marcada con línea vertical azul
- **Estadísticas**:
  - Demanda: Mín, Máx, Promedio
  - Generación: Capacidad actual, Factor de carga
  - Brechas: Máximo déficit potencial
- **Impacto económico**: Pérdidas en USD por falta de generación

### **Tab 4: 🆘 Seguridad & UFLS**
- **Indicador de riesgo**: Semáforo con color y score (0-100)
- **Factores de riesgo**: Lista de problemas detectados
- **Acciones recomendadas**: Qué hacer según el riesgo
- **Estado UFLS**: 
  - ✅ Verde si está inactivo
  - 🔴 Rojo si está activo
  - Muestra etapas activas, MW desconectados, % de carga
- **Impacto por zona**: Tabla con personas afectadas y pérdidas económicas
- **Parámetros críticos**: Frecuencia, Voltaje, Tiempo a Blackout

---

## 🚨 Escenarios Interesantes

### **Escenario 1: Déficit Leve**
1. Abre la app
2. Mueve el slider a **17:00** (demanda pico)
3. Desactiva **Renovables**
4. Aumenta demanda en **+10%**

**Resultado**: Pequeño déficit (~100 MW), frecuencia < 59.8 Hz, estado AMARILLO

### **Escenario 2: Activación de UFLS**
1. Mueve a **18:00** (máxima demanda)
2. Desactiva **Térmica** (apagón de todas las centrales térmicas)
3. Aumenta demanda en **+20%**

**Resultado**: 
- Déficit ~1000 MW
- Frecuencia cae a 59.2 Hz
- ⚠️ **UFLS ACTIVADO**: Etapa 1 y 2 se activan
- Zones afectadas: Zona Norte, Oriente, Central, Litoral
- Pérdidas económicas: Millones de USD por hora

### **Escenario 3: Riesgo Crítico de Blackout**
1. Mueve a **19:00** (peak absoluto)
2. Desactiva **Hidroeléctrica** Y **Térmica**
3. Aumenta demanda en **+25%**

**Resultado**:
- 🔴 **ESTADO CRÍTICO**
- Déficit enorme (~3500 MW)
- Frecuencia < 58.5 Hz (punto sin retorno)
- UFLS Etapa 3 activada
- 5+ zonas sin electricidad
- Blackout total en ~30-60 segundos

---

## 📈 Interpretación de Gráficos

### **Gráfico Generación vs Demanda**
```
5000 MW ┬─────────────────────────────────────────────
        │  ╱╲                  ╱╲
        │ ╱  ╲ DEMANDA        ╱  ╲
4000 MW ├╱────╲───────────────╱────╲──────────────
        │      ╲             ╱      ╲
        │       ╲───────────╱        ╲
3000 MW ├                                            ← GENERACIÓN (constante)
        │
2000 MW └─────────────────────────────────────────────
        00  06  12  18  24 (Horas)
        
RED = DÉFICIT (cuando Demanda > Generación)
```

### **Semáforo de Riesgo**
- 🟢 **GREEN** (0-25): Sistema seguro - operación normal
- 🟡 **YELLOW** (25-50): Monitorear - preparar acciones
- 🟠 **RED** (50-75): Acciones recomendadas - activar reservas
- 🔴 **CRITICAL** (75-100): Riesgo inmediato - activar UFLS

---

## 💡 Preguntas Comunes

**Q: ¿Por qué cambia la frecuencia si no cambio nada?**  
A: Hay ruido aleatorio en la generación de plantas renovables y térmicas para simular realismo.

**Q: ¿Qué significa "Factor de Carga" 0.65?**  
A: Generación real / Capacidad instalada = 65%

**Q: ¿Por qué no aparece mi nueva central en el mapa?**  
A: Actualiza la página (F5) o cambia de Tab y vuelve.

**Q: ¿Cómo obtengo datos de la simulación?**  
A: Los datos están en `st.session_state`. Se puede exportar a CSV (agregar en Tab 3).

**Q: ¿Se puede cambiar la hora automáticamente?**  
A: Sí, modifica `SIMULATION_TIMESTEP` en `config.py` para simulación automática.

---

## 🔧 Modificaciones Comunes

### **Cambiar constantes del sistema**
Edita `config.py`:
```python
DEMAND_PEAK_MW = 5000      # Cambiar pico de demanda
FREQUENCY_UFLS_TRIGGER = 59.2  # Cambiar punto trigger de UFLS
ECONOMIC_LOSS_USD_PER_MWH = 150  # Pérdidas económicas
```

### **Agregar nueva central permanentemente**
Edita `src/data/power_plants.py`:
```python
HYDROELECTRIC_PLANTS.append({
    "name": "Mi Central",
    "type": "Hidroeléctrica",
    "capacity_mw": 250,
    "latitude": -1.5,
    "longitude": -78.2,
    ...
})
```

### **Cambiar colores del mapa**
Edita `src/components/map_component.py`:
```python
PLANT_COLORS = {
    'Hidroeléctrica': '#3b82f6',  # Cambia este hex
    ...
}
```

---

## 🐛 Resolución de Problemas

| Problema | Solución |
|----------|----------|
| `ModuleNotFoundError: No module named 'streamlit'` | Ejecuta `pip install -r requirements.txt` |
| `Port 8501 already in use` | `streamlit run app.py --server.port 8502` |
| Mapa no se carga | Verifica conexión a internet (usa OpenStreetMap) |
| Gráficos lentos | Reduce resolución: `#st.set_page_config(wide_mode=False)` |
| App congela al agregar central | Recarga la página (F5) |

---

## ✨ Tips Avanzados

1. **Modo de depuración**: Abre las DevTools del navegador (F12) para ver logs
2. **Caché**: Streamlit cachea funciones. Usa `@st.cache_data` para funciones lentas
3. **Performance**: Para muchas plantas, usa `@st.cache_resource` en `PowerPlantDatabase`
4. **Historial**: Todos los cálculos quedan en `st.session_state` para reproducibilidad

---

**¡Listo para simular! 🚀**

Cualquier pregunta, revisa el `README.md` o el código comentado en cada módulo.
