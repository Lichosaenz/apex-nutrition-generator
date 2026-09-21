import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import json
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import locale

# Set page config
st.set_page_config(page_title="Apex Nutrition Generator", layout="wide", initial_sidebar_state="expanded")

# Custom CSS
st.markdown("""
<style>
    .main { background-color: #0a0e27; color: #ffffff; }
    .sidebar .sidebar-content { background-color: #1a1f3a; }
    h1, h2, h3 { color: #00ff41; font-weight: bold; }
    .stTabs [role="tablist"] button { color: #ffffff; }
    .stTabs [role="tablist"] button[aria-selected="true"] { color: #00ff41; border-color: #00ff41; }
    .metric-card { background-color: #1a1f3a; padding: 20px; border-radius: 10px; border-left: 4px solid #00ff41; }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# BIOLAYNE FRAMEWORK - FORMULAS
# ============================================================================

class BiolayneCalculator:
    @staticmethod
    def calculate_bmr_muller(age, weight, height, sex, body_fat_percent):
        """
        Müller Equation:
        BMR = (13.587 × LM) + (9.613 × FM) + (198 × Sex) – (3.351 × Age) + 674
        Sex: 1 = male, 0 = female
        """
        # Convert to metric if needed
        weight_kg = weight
        height_cm = height
        
        # Calculate lean mass and fat mass
        fat_mass_kg = (weight_kg * body_fat_percent) / 100
        lean_mass_kg = weight_kg - fat_mass_kg
        
        sex_value = 1 if sex == "Hombre" else 0
        
        bmr = (13.587 * lean_mass_kg) + (9.613 * fat_mass_kg) + (198 * sex_value) - (3.351 * age) + 674
        return bmr
    
    @staticmethod
    def calculate_tdee(bmr, activity_factor):
        """TDEE = BMR × Activity Factor"""
        return bmr * activity_factor
    
    @staticmethod
    def get_activity_factor(activity_level):
        """Activity factor lookup"""
        factors = {
            "Sedentario": 1.2,
            "Ligero (1-2x/semana)": 1.375,
            "Moderado (3-4x/semana)": 1.55,
            "Muy activo (5-6x/semana)": 1.725,
            "Extremadamente activo": 1.9
        }
        return factors.get(activity_level, 1.55)
    
    @staticmethod
    def calculate_macros(tdee, goal, weight_kg, lean_mass_kg, experience_level=None):
        """Calculate personalized macros based on goal"""
        macros = {}
        
        if goal == "Pérdida de Grasa":
            deficit = 500  # kcal
            target_calories = tdee - deficit
            # Protein: 2.7 g/kg lean mass
            protein = lean_mass_kg * 2.7
            protein_cals = protein * 4
            
            # 60/40 carbs/fats for remaining
            remaining_cals = target_calories - protein_cals
            carb_cals = remaining_cals * 0.60
            fat_cals = remaining_cals * 0.40
            
            carbs = carb_cals / 4
            fats = fat_cals / 9
            
            macros = {
                "calories": round(target_calories),
                "protein_g": round(protein),
                "carbs_g": round(carbs),
                "fats_g": round(fats),
                "deficit": deficit
            }
        
        elif goal == "Ganancia Muscular":
            # Surplus based on experience
            surplus_pct = 0.15  # Default 15%
            target_calories = tdee * (1 + surplus_pct/100)
            
            # Protein: 2.0 g/kg lean mass for muscle gain
            protein = lean_mass_kg * 2.0
            protein_cals = protein * 4
            
            # 50/50 carbs/fats for remaining
            remaining_cals = target_calories - protein_cals
            carb_cals = remaining_cals * 0.50
            fat_cals = remaining_cals * 0.50
            
            carbs = carb_cals / 4
            fats = fat_cals / 9
            
            macros = {
                "calories": round(target_calories),
                "protein_g": round(protein),
                "carbs_g": round(carbs),
                "fats_g": round(fats),
                "surplus": round(target_calories - tdee)
            }
        
        elif goal == "Mantenimiento":
            target_calories = tdee
            protein = lean_mass_kg * 1.8
            protein_cals = protein * 4
            
            remaining_cals = target_calories - protein_cals
            carb_cals = remaining_cals * 0.50
            fat_cals = remaining_cals * 0.50
            
            carbs = carb_cals / 4
            fats = fat_cals / 9
            
            macros = {
                "calories": round(target_calories),
                "protein_g": round(protein),
                "carbs_g": round(carbs),
                "fats_g": round(fats)
            }
        
        # Calculate fiber: ~12g per 1000 kcal
        macros["fiber_g"] = round(12 * macros["calories"] / 1000)
        
        return macros

# ============================================================================
# FOOD DATABASE
# ============================================================================

FOOD_DATABASE = {
    "Proteínas": {
        "Pechuga de Pollo (cocida)": {"peso_100kcal": 65, "protein_g": 20, "carbs_g": 0, "fats_g": 2.5},
        "Molida de Res 90-10": {"peso_100kcal": 55, "protein_g": 15, "carbs_g": 0, "fats_g": 5},
        "Atún en agua": {"peso_100kcal": 100, "protein_g": 25, "carbs_g": 0, "fats_g": 0.5},
        "Huevo (clara)": {"peso_100kcal": 240, "protein_g": 26, "carbs_g": 1.8, "fats_g": 0.2},
        "Yogur Griego": {"peso_100kcal": 165, "protein_g": 15, "carbs_g": 3.3, "fats_g": 0},
        "Queso Cottage": {"peso_100kcal": 140, "protein_g": 17, "carbs_g": 3.2, "fats_g": 1},
        "Proteína en Polvo": {"peso_100kcal": 30, "protein_g": 25, "carbs_g": 1, "fats_g": 1},
        "Tilapia (cocida)": {"peso_100kcal": 75, "protein_g": 21, "carbs_g": 0, "fats_g": 1},
        "Tofu Extra Firme": {"peso_100kcal": 100, "protein_g": 11, "carbs_g": 2, "fats_g": 5.5},
    },
    "Carbohidratos": {
        "Papas (cocidas)": {"peso_100kcal": 100, "protein_g": 3, "carbs_g": 23, "fats_g": 0.1},
        "Arroz Blanco (cocido)": {"peso_100kcal": 90, "protein_g": 3, "carbs_g": 20, "fats_g": 0.3},
        "Avena": {"peso_100kcal": 25, "protein_g": 4, "carbs_g": 18, "fats_g": 2},
        "Pan Integral": {"peso_100kcal": 40, "protein_g": 5, "carbs_g": 17, "fats_g": 1.5},
        "Quinoa (cocida)": {"peso_100kcal": 90, "protein_g": 4, "carbs_g": 18, "fats_g": 1.5},
        "Sweet Potato": {"peso_100kcal": 100, "protein_g": 1.6, "carbs_g": 21, "fats_g": 0.1},
        "Pasta (cocida)": {"peso_100kcal": 75, "protein_g": 4, "carbs_g": 19, "fats_g": 0.7},
    },
    "Grasas": {
        "Huevo Completo": {"peso_100kcal": 70, "protein_g": 9, "carbs_g": 0.6, "fats_g": 7},
        "Aguacate": {"peso_100kcal": 55, "protein_g": 1, "carbs_g": 4, "fats_g": 9},
        "Almendras": {"peso_100kcal": 15, "protein_g": 3, "carbs_g": 3.1, "fats_g": 8.7},
        "Mantequilla de Cacahuete": {"peso_100kcal": 15, "protein_g": 3, "carbs_g": 3.5, "fats_g": 8},
        "Aceite de Oliva": {"peso_100kcal": 10, "protein_g": 0, "carbs_g": 0, "fats_g": 11.2},
        "Nueces": {"peso_100kcal": 15, "protein_g": 3, "carbs_g": 2, "fats_g": 9.5},
    },
    "Vegetales": {
        "Brócoli": {"peso_100kcal": 250, "protein_g": 7.5, "carbs_g": 14, "fats_g": 1},
        "Espinaca": {"peso_100kcal": 350, "protein_g": 8.75, "carbs_g": 3, "fats_g": 0.7},
        "Zucchini": {"peso_100kcal": 500, "protein_g": 3, "carbs_g": 3.6, "fats_g": 0.4},
        "Pimientos": {"peso_100kcal": 325, "protein_g": 1.3, "carbs_g": 7, "fats_g": 0.4},
        "Espárragos": {"peso_100kcal": 500, "protein_g": 5, "carbs_g": 3.8, "fats_g": 0.2},
        "Zanahoria": {"peso_100kcal": 250, "protein_g": 0.9, "carbs_g": 9, "fats_g": 0.2},
    },
    "Frutas": {
        "Banana": {"peso_100kcal": 100, "protein_g": 1.1, "carbs_g": 23, "fats_g": 0.3},
        "Manzana": {"peso_100kcal": 170, "protein_g": 0.3, "carbs_g": 25, "fats_g": 0.2},
        "Fresas": {"peso_100kcal": 275, "protein_g": 2.2, "carbs_g": 12, "fats_g": 0.5},
        "Arándanos": {"peso_100kcal": 160, "protein_g": 1.5, "carbs_g": 21, "fats_g": 0.5},
        "Mango": {"peso_100kcal": 100, "protein_g": 0.8, "carbs_g": 25, "fats_g": 0.4},
    }
}

CONDIMENTOS = [
    "Hot Sauce", "Mostaza", "Vinagre Balsámico", "Salsa de Soja",
    "Catsup Bajo Azúcar", "Sal/Pimienta", "Cilantro", "Albahaca",
    "Comino", "Paprika", "Curry", "Limón/Lima", "Sriracha"
]

# ============================================================================
# INITIALIZATION
# ============================================================================

if "clients" not in st.session_state:
    st.session_state.clients = {}

if "current_client" not in st.session_state:
    st.session_state.current_client = None

if "menu" not in st.session_state:
    st.session_state.menu = {
        "Desayuno": "",
        "Colación 1": "",
        "Almuerzo": "",
        "Colación 2": "",
        "Cena": ""
    }

# ============================================================================
# MAIN APP
# ============================================================================

st.title("🏋️ Apex Nutrition Generator")
st.markdown("Generador de planes de nutrición personalizados basado en Biolayne Framework")

# Sidebar - Client Management
with st.sidebar:
    st.header("📋 Clientes")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Nuevo Cliente", use_container_width=True):
            st.session_state.current_client = None
    
    with col2:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.menu = {key: "" for key in st.session_state.menu}
    
    # Client list
    if st.session_state.clients:
        selected = st.selectbox(
            "Seleccionar cliente:",
            options=list(st.session_state.clients.keys()),
            key="client_selector"
        )
        if selected:
            st.session_state.current_client = selected

# ============================================================================
# TABS
# ============================================================================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "👤 Perfil Cliente",
    "📊 Cálculos",
    "🍽️ Menú Semanal",
    "📝 Plan de Comidas",
    "🧾 Lista de Compras",
    "📥 PDF Export"
])

# ============================================================================
# TAB 1: PERFIL CLIENTE
# ============================================================================

with tab1:
    st.header("Perfil del Cliente")
    
    col1, col2 = st.columns(2)
    
    with col1:
        nombre = st.text_input("Nombre del Cliente", value=st.session_state.current_client or "")
        edad = st.number_input("Edad", min_value=15, max_value=100, value=30)
        peso_kg = st.number_input("Peso (kg)", min_value=40.0, max_value=200.0, value=70.0)
        altura_cm = st.number_input("Altura (cm)", min_value=140, max_value=230, value=170)
    
    with col2:
        sexo = st.selectbox("Sexo", ["Hombre", "Mujer"])
        grasa_corporal = st.number_input("Grasa Corporal (%)", min_value=5.0, max_value=50.0, value=20.0)
        actividad = st.selectbox("Nivel de Actividad", [
            "Sedentario",
            "Ligero (1-2x/semana)",
            "Moderado (3-4x/semana)",
            "Muy activo (5-6x/semana)",
            "Extremadamente activo"
        ], index=2)
        objetivo = st.selectbox("Objetivo", [
            "Pérdida de Grasa",
            "Ganancia Muscular",
            "Mantenimiento"
        ])
    
    # Preferencias dietéticas
    st.subheader("Preferencias Dietéticas")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        alergia_lacteos = st.checkbox("Alergia/Intolerancia Lácteos")
        alergia_gluten = st.checkbox("Intolerancia Gluten")
    
    with col2:
        vegetariano = st.checkbox("Vegetariano")
        vegano = st.checkbox("Vegano")
    
    with col3:
        alergias_otros = st.text_input("Otras alergias/restricciones")
    
    # Save client
    if st.button("💾 Guardar Cliente", use_container_width=True, type="primary"):
        if nombre:
            st.session_state.clients[nombre] = {
                "edad": edad,
                "peso_kg": peso_kg,
                "altura_cm": altura_cm,
                "sexo": sexo,
                "grasa_corporal": grasa_corporal,
                "actividad": actividad,
                "objetivo": objetivo,
                "alergia_lacteos": alergia_lacteos,
                "alergia_gluten": alergia_gluten,
                "vegetariano": vegetariano,
                "vegano": vegano,
                "alergias_otros": alergias_otros
            }
            st.session_state.current_client = nombre
            st.success(f"✅ Cliente '{nombre}' guardado!")
        else:
            st.error("Ingresa un nombre para el cliente")

# ============================================================================
# TAB 2: CÁLCULOS
# ============================================================================

with tab2:
    st.header("Cálculos Biolayne")
    
    if st.session_state.current_client and st.session_state.current_client in st.session_state.clients:
        client = st.session_state.clients[st.session_state.current_client]
        
        # Calculate
        bmr = BiolayneCalculator.calculate_bmr_muller(
            client["edad"],
            client["peso_kg"],
            client["altura_cm"],
            client["sexo"],
            client["grasa_corporal"]
        )
        
        activity_factor = BiolayneCalculator.get_activity_factor(client["actividad"])
        tdee = BiolayneCalculator.calculate_tdee(bmr, activity_factor)
        
        lean_mass = client["peso_kg"] - (client["peso_kg"] * client["grasa_corporal"] / 100)
        macros = BiolayneCalculator.calculate_macros(tdee, client["objetivo"], client["peso_kg"], lean_mass)
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("BMR", f"{bmr:.0f} kcal")
        with col2:
            st.metric("Activity Factor", f"{activity_factor:.2f}x")
        with col3:
            st.metric("TDEE", f"{tdee:.0f} kcal")
        with col4:
            st.metric("Lean Mass", f"{lean_mass:.1f} kg")
        
        st.divider()
        
        # Macros
        st.subheader("📊 Macros Personalizados")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Calorías", f"{macros['calories']}")
        with col2:
            st.metric("Proteína", f"{macros['protein_g']}g")
        with col3:
            st.metric("Carbos", f"{macros['carbs_g']}g")
        with col4:
            st.metric("Grasas", f"{macros['fats_g']}g")
        with col5:
            st.metric("Fibra", f"{macros['fiber_g']}g")
        
        if "deficit" in macros:
            st.info(f"📉 Déficit: {macros['deficit']} kcal/día")
        elif "surplus" in macros:
            st.info(f"📈 Superávit: {macros['surplus']} kcal/día")
        
        # Store for later use
        st.session_state.current_macros = macros
        st.session_state.current_client_data = client
    
    else:
        st.warning("⚠️ Selecciona un cliente primero en el Tab 'Perfil Cliente'")

# ============================================================================
# TAB 3: MENÚ SEMANAL
# ============================================================================

with tab3:
    st.header("🍽️ Menú Semanal")
    st.markdown("Ingresa el menú que vas a proporcionar al cliente para esta semana")
    
    meals = ["Desayuno", "Colación 1", "Almuerzo", "Colación 2", "Cena"]
    
    col1, col2 = st.columns(2)
    
    for i, meal in enumerate(meals):
        if i % 2 == 0:
            with col1:
                st.session_state.menu[meal] = st.text_area(
                    f"{meal}",
                    value=st.session_state.menu[meal],
                    height=60,
                    placeholder=f"Ej: Pechuga de pollo asada con brócoli y espáragos"
                )
        else:
            with col2:
                st.session_state.menu[meal] = st.text_area(
                    f"{meal}",
                    value=st.session_state.menu[meal],
                    height=60,
                    placeholder=f"Ej: Avena con claras y banana"
                )
    
    st.divider()
    st.subheader("Vista Previa del Menú")
    for meal, desc in st.session_state.menu.items():
        if desc:
            st.write(f"**{meal}**: {desc}")

# ============================================================================
# TAB 4: PLAN DE COMIDAS
# ============================================================================

with tab4:
    st.header("📝 Plan de Comidas Completo")
    
    if "current_macros" in st.session_state and st.session_state.current_client:
        macros = st.session_state.current_macros
        client = st.session_state.current_client_data
        
        st.markdown(f"""
        ### Cliente: {st.session_state.current_client}
        - **Objetivo**: {client['objetivo']}
        - **Calorías**: {macros['calories']} kcal/día
        - **Proteína**: {macros['protein_g']}g | **Carbos**: {macros['carbs_g']}g | **Grasas**: {macros['fats_g']}g
        """)
        
        st.divider()
        
        # Display menu as plan
        st.subheader("Plan de Comidas - Semana")
        
        plan_data = []
        total_cals = 0
        total_protein = 0
        total_carbs = 0
        total_fats = 0
        
        meals_list = ["Desayuno", "Colación 1", "Almuerzo", "Colación 2", "Cena"]
        target_cals_per_meal = macros['calories'] / 5  # Distribute evenly
        
        for meal in meals_list:
            if st.session_state.menu[meal]:
                plan_data.append({
                    "Comida": meal,
                    "Descripción": st.session_state.menu[meal],
                    "Calorías": f"~{int(target_cals_per_meal)}",
                    "Proteína": f"~{int(macros['protein_g']/5)}g",
                    "Carbos": f"~{int(macros['carbs_g']/5)}g",
                    "Grasas": f"~{int(macros['fats_g']/5)}g"
                })
        
        if plan_data:
            df_plan = pd.DataFrame(plan_data)
            st.dataframe(df_plan, use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ Ingresa un menú en el Tab 'Menú Semanal'")
    
    else:
        st.warning("⚠️ Completa el perfil del cliente y cálculos primero")

# ============================================================================
# TAB 5: LISTA DE COMPRAS
# ============================================================================

with tab5:
    st.header("🧾 Lista de Compras")
    
    if st.session_state.current_client and any(st.session_state.menu.values()):
        st.info("📝 Lista de compras basada en el menú semanal (cantidad estimada para 1 semana)")
        
        # Extract ingredients from menu
        shopping_list = {}
        
        for meal, desc in st.session_state.menu.items():
            if desc:
                # This is a simplified extraction - in production, you'd parse more intelligently
                st.markdown(f"**{meal}**: {desc}")
        
        st.divider()
        
        # Organized shopping list by category
        st.subheader("Categorías de Compra")
        
        categories = {
            "🥚 Proteínas": ["pollo", "res", "atún", "huevo", "queso", "yogur"],
            "🌾 Carbohidratos": ["arroz", "papa", "avena", "pan", "quinoa", "pasta"],
            "🌿 Vegetales": ["brócoli", "espinaca", "zucchini", "pimientos", "espárágos"],
            "🍌 Frutas": ["banana", "manzana", "fresas", "arándanos"],
            "🫒 Grasas": ["aceite", "aguacate", "nueces", "almendras"],
            "🧂 Condimentos": CONDIMENTOS
        }
        
        for category, items in categories.items():
            with st.expander(category):
                for item in items:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"☐ {item}")

    else:
        st.warning("⚠️ Ingresa un menú primero")

# ============================================================================
# TAB 6: EXPORT PDF
# ============================================================================

with tab6:
    st.header("📥 Generar PDF")
    
    if st.session_state.current_client and "current_macros" in st.session_state:
        
        if st.button("📄 Generar PDF del Plan", use_container_width=True, type="primary"):
            # Generate PDF
            pdf_buffer = BytesIO()
            doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor("#00ff41"),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            story.append(Paragraph("APEX NUTRITION PLAN", title_style))
            story.append(Spacer(1, 0.2*inch))
            
            client = st.session_state.current_client_data
            macros = st.session_state.current_macros
            
            # Client Info
            client_info = f"""
            <b>Cliente:</b> {st.session_state.current_client} | 
            <b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y')}<br/>
            <b>Edad:</b> {client['edad']} | 
            <b>Peso:</b> {client['peso_kg']}kg | 
            <b>Objetivo:</b> {client['objetivo']}
            """
            story.append(Paragraph(client_info, styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
            
            # Macros Section
            story.append(Paragraph("<b>Macros Personalizados</b>", styles['Heading2']))
            macros_data = [
                ["Calorías", "Proteína", "Carbos", "Grasas", "Fibra"],
                [
                    f"{macros['calories']} kcal",
                    f"{macros['protein_g']}g",
                    f"{macros['carbs_g']}g",
                    f"{macros['fats_g']}g",
                    f"{macros['fiber_g']}g"
                ]
            ]
            macro_table = Table(macros_data)
            macro_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1a1f3a")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#00ff41")),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(macro_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Meal Plan
            story.append(Paragraph("<b>Plan de Comidas Diario</b>", styles['Heading2']))
            
            meals_list = ["Desayuno", "Colación 1", "Almuerzo", "Colación 2", "Cena"]
            meal_plan_data = [["Comida", "Descripción"]]
            
            for meal in meals_list:
                if st.session_state.menu[meal]:
                    meal_plan_data.append([
                        meal,
                        st.session_state.menu[meal][:100] + "..." if len(st.session_state.menu[meal]) > 100 else st.session_state.menu[meal]
                    ])
            
            if len(meal_plan_data) > 1:
                meal_table = Table(meal_plan_data, colWidths=[1.5*inch, 4*inch])
                meal_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1a1f3a")),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#00ff41")),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP')
                ]))
                story.append(meal_table)
            
            # Build PDF
            doc.build(story)
            pdf_buffer.seek(0)
            
            # Download button
            st.download_button(
                label="📥 Descargar PDF",
                data=pdf_buffer,
                file_name=f"Plan_Nutricion_{st.session_state.current_client}_{datetime.now().strftime('%d%m%Y')}.pdf",
                mime="application/pdf"
            )
            
            st.success("✅ PDF generado correctamente")
    
    else:
        st.warning("⚠️ Completa el perfil y el menú primero")

# Footer
st.divider()
st.markdown("""
---
**Apex Nutrition Generator** | Powered by Biolayne Framework & Built With Science
*Generador de planes de nutrición personalizados para Apex Human Labs*
""")
