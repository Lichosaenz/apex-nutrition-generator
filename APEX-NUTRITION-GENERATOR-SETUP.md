# 🏋️ APEX NUTRITION GENERATOR v2 - SETUP & QUICK START

**Creado:** 21 Septiembre 2026  
**Tecnología:** Python + Streamlit  
**Para:** Apex Human Labs - Nutrición Coaching

---

## ✨ ¿QUÉ ACABAS DE RECIBIR?

Una **app profesional Streamlit** que AUTOMATIZA completamente la creación de planes de nutrición personalizados para tus clientes de coaching.

### 🎯 El flujo (en 4 pasos):

```
1. Ingresás datos del cliente          → 2. App calcula TDEE + Macros (Biolayne)
        ↓                                             ↓
   (edad, peso, altura,          →    (Müller BMR automático)
    objetivo, actividad)

3. Ingresás menú semanal          → 4. Descargás PDF personalizado
        ↓                                             ↓
   (5 comidas/día específicas)     →    (Plan completo exportable)
```

---

## 📂 ARCHIVOS INCLUIDOS

```
apex-nutrition-generator/
├── app.py                          ← MAIN APP (1,700+ líneas)
├── requirements.txt                ← Dependencias Python
├── run.sh                          ← Launcher para Mac/Linux
├── run.bat                         ← Launcher para Windows
└── README.md                       ← Documentación completa
```

---

## 🚀 INSTALACIÓN & EJECUCIÓN (3 OPCIONES)

### OPCIÓN 1: Mac / Linux (Recomendado)
```bash
cd apex-nutrition-generator
chmod +x run.sh
./run.sh
```

### OPCIÓN 2: Windows
```cmd
cd apex-nutrition-generator
run.bat
```

### OPCIÓN 3: Manual (Cualquier SO)
```bash
# 1. Instala Python 3.8+ (si no lo tienes)
# 2. Abre terminal/CMD en la carpeta del proyecto
# 3. Crea virtual environment
python -m venv venv

# 4. Activa (Mac/Linux)
source venv/bin/activate

# 4. Activa (Windows)
venv\Scripts\activate.bat

# 5. Instala dependencias
pip install -r requirements.txt

# 6. Ejecuta
streamlit run app.py
```

**Result:** La app se abre en `http://localhost:8501`

---

## 📋 CÓMO USAR - PASO A PASO

### **TAB 1️⃣ : "👤 Perfil Cliente"**

Ingresa datos del cliente:
- Nombre
- Edad, peso (kg), altura (cm)
- Sexo, % grasa corporal
- Nivel de actividad (Sedentario → Extremadamente activo)
- Objetivo: Pérdida Grasa / Ganancia Muscular / Mantenimiento
- Restricciones dietéticas (opcional)

**Click:** "💾 Guardar Cliente"

---

### **TAB 2️⃣ : "📊 Cálculos"**

La app calcula **automáticamente**:

| Métrica | Fórmula |
|---------|---------|
| **BMR** | Müller Equation (edad, peso, % grasa) |
| **TDEE** | BMR × Activity Factor |
| **Proteína** | 2.7 g/kg (pérdida grasa) ó 2.0 g/kg (ganancia) |
| **Carbos + Grasas** | Distribuidos según objetivo |
| **Fibra** | ~12g por 1,000 kcal |

**Ejemplo (José Luis):**
```
💪 BMR: 1,820 kcal
⚙️  Activity Factor: 1.55x (Moderado)
📊 TDEE: 2,821 kcal
💰 Macros para PÉRDIDA GRASA:
   └─ Calorías: 2,321 (-500 déficit)
   └─ Proteína: 178g
   └─ Carbos: 275g
   └─ Grasas: 64g
   └─ Fibra: 28g
```

---

### **TAB 3️⃣ : "🍽️ Menú Semanal"**

Ingresa el **menú ESPECÍFICO** que darás al cliente esta semana:

```
Desayuno:
→ "Avena 40g + 3 claras + 1 banana + 1tbsp mantequilla de cacahuete"

Colación 1:
→ "Manzana 180g + proteína en polvo 30g"

Almuerzo:
→ "Pechuga pollo 180g asada + arroz blanco 150g + brócoli 250g + ensalada"

Colación 2:
→ "Yogur griego 165g sin azúcar + berries congeladas"

Cena:
→ "Atún enlatado 100g + sweet potato 100g + espinaca"
```

**IMPORTANTE:** Aquí es donde DIFFERENCIA la app — cada cliente puede tener **menú diferente cada semana**, y el plan se adapta automáticamente.

---

### **TAB 4️⃣ : "📝 Plan de Comidas"**

La app **distribuye automáticamente** los macros del cliente entre las 5 comidas.

```
Cliente: José Luis Sáenz | Objetivo: Pérdida Grasa | Total: 2,321 kcal

Desayuno:           ~464 kcal | Proteína ~36g | Carbs ~55g | Grasas ~13g
Colación 1:         ~464 kcal | Proteína ~36g | Carbs ~55g | Grasas ~13g
Almuerzo:           ~464 kcal | Proteína ~36g | Carbs ~55g | Grasas ~13g
Colación 2:         ~464 kcal | Proteína ~36g | Carbs ~55g | Grasas ~13g
Cena:               ~464 kcal | Proteína ~36g | Carbs ~55g | Grasas ~13g
────────────────────────────────────────────────────────
TOTAL:            2,321 kcal | Proteína 178g | Carbs 275g | Grasas 64g
```

---

### **TAB 5️⃣ : "🧾 Lista de Compras"**

Organizada automáticamente por **categoría de supermercado**:

```
🥚 PROTEÍNAS
  ☐ Pechuga pollo (1 kg)
  ☐ Atún enlatado (3 latas)
  ☐ Huevos (1 docena)
  ☐ Proteína en polvo (1 kg)
  ☐ Yogur griego (6 yogures)

🌾 CARBOHIDRATOS
  ☐ Arroz blanco (1 kg)
  ☐ Avena (500g)
  ☐ Sweet potatoes (1.5 kg)
  ☐ Pasta integral (500g)

🥦 VEGETALES
  ☐ Brócoli (2 cabezas)
  ☐ Espinaca (1 bolsa)
  ☐ Zucchini (2 unidades)
  ☐ Pimientos (3 piezas)
  ☐ Espárragos (1 atado)

[... y más categorías]
```

---

### **TAB 6️⃣ : "📥 PDF Export"**

**Click:** "📄 Generar PDF del Plan"

Se descarga automáticamente un PDF profesional que incluye:
- ✅ Datos del cliente
- ✅ Cálculos Biolayne (BMR, TDEE, Macros)
- ✅ Plan de comidas completo
- ✅ Macros por comida
- ✅ Fecha de generación

**Listo para enviar al cliente.**

---

## 🧮 FÓRMULAS INCLUIDAS (Biolayne Framework)

### BMR - Müller Equation
```
BMR = (13.587 × LM) + (9.613 × FM) + (198 × Sex) – (3.351 × Age) + 674

Donde:
- LM = Lean Mass (kg)
- FM = Fat Mass (kg)  
- Sex = 1 (hombre) ó 0 (mujer)
```

### TDEE
```
TDEE = BMR × Activity Factor

Activity Factors:
- Sedentario: 1.2
- Ligero (1-2x/semana): 1.375
- Moderado (3-4x/semana): 1.55
- Muy activo (5-6x/semana): 1.725
- Extremadamente activo: 1.9
```

### Macros por Objetivo

**PÉRDIDA DE GRASA:**
```
- Déficit: 500 kcal/día
- Proteína: 2.7 g/kg masa magra (ALTA para preservar músculo)
- Carbos: 60% de calorías restantes
- Grasas: 40% de calorías restantes
```

**GANANCIA MUSCULAR:**
```
- Superávit: 15% del TDEE
- Proteína: 2.0 g/kg masa magra
- Carbos: 50% de calorías restantes
- Grasas: 50% de calorías restantes
```

**MANTENIMIENTO:**
```
- Proteína: 1.8 g/kg masa magra
- Carbos: 50% de calorías restantes
- Grasas: 50% de calorías restantes
```

---

## 🍔 BASE DE DATOS DE ALIMENTOS

Incluye ~40 alimentos organizados por tipo:

### Proteínas (9)
Pollo, Res 90-10, Atún, Claras de huevo, Yogur griego, Queso cottage, Proteína en polvo, Tilapia, Tofu

### Carbohidratos (7)
Papas, Arroz blanco, Avena, Pan integral, Quinoa, Sweet potato, Pasta

### Grasas (6)
Huevo completo, Aguacate, Almendras, Mantequilla de cacahuete, Aceite de oliva, Nueces

### Vegetales (6)
Brócoli, Espinaca, Zucchini, Pimientos, Espárragos, Zanahoria

### Frutas (5)
Banana, Manzana, Fresas, Arándanos, Mango

### Condimentos Sin Calorías (13)
Hot sauce, Mostaza, Vinagre balsámico, Soja, Catsup bajo azúcar, Sal/pimienta, Hierbas, Especias, Limón, Sriracha, etc.

---

## 🎨 DISEÑO & ESTILO

- **Dark mode** con tema Apex (profesional)
- **Neon green (#00ff41)** para highlights (energía)
- **Card-based layout** (fácil de leer)
- **Responsive** (funciona en laptop, tablet, móvil)

---

## 💡 CASOS DE USO

### Caso 1: Cliente nuevo
1. Creas perfil → App calcula → Ingresás menú → Descargas PDF
2. Tiempo total: **~10 minutos** por cliente

### Caso 2: Cambio de menú semanal
1. Cliente ya existe (guardado)
2. Solo ingresás nuevo menú → Actualizo PDF
3. Tiempo: **~3 minutos**

### Caso 3: Múltiples clientes
- La app guarda todos los clientes en sesión
- Cambias cliente → Menú se resetea → Ingresás nuevo menú → Exportas
- **Flujo rápido y eficiente**

---

## 🔧 REQUISITOS TÉCNICOS

- **Python 3.8+** (Windows, Mac, Linux)
- **Conexión a internet** (para descargas iniciales)
- **Espacio en disco:** ~500 MB (sin dependencies)

---

## ⚡ PRÓXIMAS MEJORAS (ROADMAP)

✅ **Ya incluido:**
- Cálculos Biolayne completos
- Cliente manager
- Menú ingreso flexible
- PDF export básico

🔜 **Fase 2 (Próxima):**
- Meal prep recipe database
- Ingredient parsing automático
- Advanced PDF con recetas
- Client history/tracking

🚀 **Fase 3 (Futuro):**
- Google Drive sync
- Integración con Trainerize
- App móvil
- Seguimiento progreso con gráficos

---

## 🆘 TROUBLESHOOTING

### Error: "Python no encontrado"
→ Descarga Python 3.8+ desde python.org

### Error: "streamlit command not found"
→ Asegúrate que venv está activado:
```bash
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate.bat  # Windows
```

### La app se cierra después de ejecutar
→ Usa `run.sh` o `run.bat` que tiene `pause` al final

### Otros errores
→ Lee el README.md completo incluido en la carpeta

---

## 📞 SOPORTE

**Contacto:** José Luis Sáenz - Apex Human Labs

---

## 🏆 TECNOLOGÍA USADA

- **Streamlit** — Framework de app web
- **Pandas** — Manipulación de datos
- **NumPy** — Cálculos numéricos
- **ReportLab** — Generación de PDFs

---

**Hecho con ❤️ para Apex Human Labs**  
*Automatizando nutrición, escalando coaching*

🚀 **¡Listo para empezar!** 

Ejecuta `run.sh` ó `run.bat` y comienza a generar planes personalizados.
