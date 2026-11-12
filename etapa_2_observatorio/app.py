import streamlit as st
import pandas as pd
import plotly.express as px
import ee
import folium
from streamlit_folium import st_folium
import requests

# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS SOBRIOS
st.set_page_config(page_title="Urban Heat Island Observatory | Paris", layout="wide")

st.markdown("""
    <style>
    .block-container {padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1440px;}
    h1, h2, h3, h4 {font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; font-weight: 600; letter-spacing: -0.02em;}
    div[data-testid="metric-container"] {
        background-color: #11141c;
        border: 1px solid #262b38;
        padding: 14px 18px;
        border-radius: 4px;
    }
    .glossary-box {
        background-color: #11141c;
        border-left: 3px solid #3b82f6;
        padding: 12px 16px;
        font-size: 0.86rem;
        line-height: 1.45;
        color: #d1d5db;
        border-radius: 0 4px 4px 0;
        height: 100%;
    }
    .glossary-title {font-weight: 600; color: #ffffff; display: block; margin-bottom: 4px;}
    .ref-box {
        background-color: #0d1017;
        border: 1px solid #1f2937;
        padding: 20px 24px;
        border-radius: 4px;
        font-size: 0.85rem;
        color: #9ca3af;
        line-height: 1.6;
    }
    </style>
""", unsafe_allow_html=True)

# Nomenclatura explícita: 1er, 2ème, 3ème ... 20ème
def fmt_arr(val):
    n = int(val)
    return "1er" if n == 1 else f"{n}ème"

# 2. DICCIONARIO MULTILINGÜE (ES / FR / EN)
TRANSLATIONS = {
    "ES": {
        "title": "Observatorio de Isla de Calor Urbana (UHI) y Vulnerabilidad Térmica — París",
        "subtitle": "Integración de telemetría satelital Landsat 8/9 (píxeles de 30m), índice vegetal Sentinel-2 (10m) y exposición demográfica comunal.",
        "g_lst_t": "LST (Temperatura de Superficie)",
        "g_lst_d": "Calor radiante real emitido por techos, calles y suelo (°C) medido a 30m de resolución. Refleja el calentamiento de los materiales urbanos.",
        "g_ndvi_t": "NDVI (Índice de Vegetación)",
        "g_ndvi_d": "Escala de -1 a +1 que cuantifica la densidad de biomasa vegetal. Valores < 0.15 indican asfalto o piedra; valores > 0.40 indican parques arbolados.",
        "g_pop_t": "Exposición Demográfica",
        "g_pop_d": "Población residente permanente por arrondissement (WorldPop). Pondera el volumen de ciudadanos expuestos directamente al estrés térmico.",
        "g_uvi_t": "Índice UVI (0 a 100 pts)",
        "g_uvi_d": "Métrica compuesta de prioridad: 50% temperatura superficial (LST) + 30% déficit vegetal (1 - NDVI) + 20% densidad poblacional.",
        "sb_lang": "Idioma / Langue / Language",
        "sb_params": "Parámetros de Estudio",
        "sb_years": "Periodo de análisis (Años)",
        "sb_years_help": "Selecciona un rango multianual o coloca ambos cursores en el mismo año para evaluar un año puntual.",
        "sb_month": "Mes de evaluación comparativa",
        "sb_arr": "Arrondissements (1er al 20ème)",
        "sb_map_cfg": "Capas Cartográficas",
        "sb_basemap": "Mapa base (Calles y Edificios)",
        "sb_opacity": "Opacidad de píxeles térmicos (Landsat)",
        "sb_opacity_help": "Un valor entre 0.40 y 0.55 permite ver con nitidez las calles, avenidas y edificios debajo de la mancha térmica.",
        "sb_borders": "Mostrar límites comunales (1er - 20ème)",
        "sb_labels": "Superponer nombres de calles y barrios",
        "warn_arr": "Por favor selecciona al menos un arrondissement en el menú lateral.",
        "kpi1": "LST Media Comunal",
        "kpi2": "Índice UVI Promedio",
        "kpi3": "Arrondissement Más Crítico",
        "kpi4": "Cobertura Vegetal (NDVI)",
        "kpi5": "Población Analizada",
        "active_zones": "arrondissements activos",
        "map_title": "Cartografía Térmica a Nivel de Píxel (30m) y Estructura Urbana — Veranos",
        "map_caption": "Pasa el cursor sobre cualquier arrondissement para auditar sus métricas, o haz zoom para inspeccionar calles y edificios.",
        "scale_1": "22 °C (Río Sena / Bosques)",
        "scale_2": "28 °C (Parques arbolados)",
        "scale_3": "33 °C (Tejido residencial)",
        "scale_4": "38 °C (Grandes ejes viales / Estaciones)",
        "scale_5": "44+ °C (Cubiertas industriales / Asfalto denso)",
        "rank_title": "Clasificación por Índice de Vulnerabilidad (UVI)",
        "rank_caption": "Ordenado de mayor a menor riesgo térmico combinado. El color indica la temperatura superficial media (°C).",
        "tab1": "Serie Temporal Multianual",
        "tab2": "Matriz Estacional (Mes vs. Arrondissement)",
        "tab3": "Correlación Vegetación vs. Temperatura",
        "tab4": "Datos Tabulares y Descarga",
        "t1_sub": "Evolución Mensual Comparada",
        "t1_radio": "Variable a representar en la serie histórica:",
        "t2_sub": "Matriz de Temperatura Superficial Media (°C)",
        "t2_cap": "Cada celda muestra la temperatura superficial promedio (°C) por arrondissement y mes durante el periodo activo.",
        "t3_sub": "Efecto de Enfriamiento Vegetal y Exposición Demográfica",
        "t3_cap": "Eje X: Índice Vegetal (NDVI) | Eje Y: Temperatura Superficial (°C) | Tamaño: Población | Color: Índice UVI.",
        "t4_sub": "Tabla de Datos Auditables por Arrondissement",
        "dl_btn": "Descargar tabla filtrada (CSV)",
        "ref_title": "Referencias Científicas, Fuentes de Datos y Metodología Reproducible",
        "months": {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"},
        "months_short": ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    },
    "FR": {
        "title": "Observatoire des Îlots de Chaleur Urbains (ICU) et Vulnérabilité Thermique — Paris",
        "subtitle": "Intégration de la télédétection spatiale Landsat 8/9 (pixels de 30m), de l'indice de végétation Sentinel-2 (10m) et de la démographie par arrondissement.",
        "g_lst_t": "LST (Température de Surface)",
        "g_lst_d": "Chaleur radiative réelle émise par les toitures, la voirie et les sols (°C) à 30m de résolution. Mesure l'échauffement des matériaux urbains.",
        "g_ndvi_t": "NDVI (Indice de Végétation)",
        "g_ndvi_d": "Échelle de -1 à +1 mesurant la densité et la vigueur végétale. < 0.15 indique le bâti minéral ou l'asphalte ; > 0.40 indique les parcs boisés.",
        "g_pop_t": "Exposition Démographique",
        "g_pop_d": "Population résidente permanente par arrondissement (WorldPop). Pondère le volume d'habitants directement soumis au stress thermique.",
        "g_uvi_t": "Indice UVI (0 à 100 pts)",
        "g_uvi_d": "Indice synthétique de vulnérabilité : 50% température de surface (LST) + 30% déficit végétal (1 - NDVI) + 20% densité de population.",
        "sb_lang": "Langue / Idioma / Language",
        "sb_params": "Paramètres d'Étude",
        "sb_years": "Période d'analyse (Années)",
        "sb_years_help": "Sélectionnez une plage pluriannuelle ou placez les deux curseurs sur la même année pour une analyse annuelle.",
        "sb_month": "Mois d'évaluation comparative",
        "sb_arr": "Arrondissements (1er au 20ème)",
        "sb_map_cfg": "Couches Cartographiques",
        "sb_basemap": "Fond de carte (Voirie et Bâti)",
        "sb_opacity": "Opacité des pixels thermiques (Landsat)",
        "sb_opacity_help": "Une valeur entre 0.40 et 0.55 permet de distinguer clairement les rues, avenues et bâtiments sous la couche thermique.",
        "sb_borders": "Afficher les limites des arrondissements",
        "sb_labels": "Superposer les noms des rues et quartiers",
        "warn_arr": "Veuillez sélectionner au moins un arrondissement dans le panneau latéral.",
        "kpi1": "LST Moyenne Communale",
        "kpi2": "Indice UVI Moyen",
        "kpi3": "Arrondissement le Plus Critique",
        "kpi4": "Couverture Végétale (NDVI)",
        "kpi5": "Population Analysée",
        "active_zones": "arrondissements actifs",
        "map_title": "Cartographie Thermique à l'Échelle du Pixel (30m) et Trame Urbaine — Étés",
        "map_caption": "Survolez un arrondissement pour consulter ses indicateurs, ou zoomez pour inspecter la voirie et les bâtiments.",
        "scale_1": "22 °C (Seine / Bois urbains)",
        "scale_2": "28 °C (Parcs arborés)",
        "scale_3": "33 °C (Tissu résidentiel)",
        "scale_4": "38 °C (Grands axes / Gares)",
        "scale_5": "44+ °C (Toitures industrielles / Asphalte)",
        "rank_title": "Classement par Indice de Vulnérabilité (UVI)",
        "rank_caption": "Classé du risque combiné le plus élevé au plus faible. La couleur indique la température de surface moyenne (°C).",
        "tab1": "Série Temporelle Pluriannuelle",
        "tab2": "Matrice Saisonnière (Mois vs. Arrondissement)",
        "tab3": "Corrélation Végétation vs. Température",
        "tab4": "Données Tabulaires et Export",
        "t1_sub": "Dynamique Mensuelle Comparée",
        "t1_radio": "Indicateur à afficher sur la série historique :",
        "t2_sub": "Matrice de Température de Surface Moyenne (°C)",
        "t2_cap": "Chaque cellule indique la température de surface moyenne (°C) par arrondissement et par mois sur la période sélectionnée.",
        "t3_sub": "Effet de Rafraîchissement Végétal et Exposition Démographique",
        "t3_cap": "Axe X : Indice Végétal (NDVI) | Axe Y : Température de Surface (°C) | Taille : Population | Couleur : Indice UVI.",
        "t4_sub": "Tableau de Données Auditables par Arrondissement",
        "dl_btn": "Télécharger le tableau filtré (CSV)",
        "ref_title": "Références Scientifiques, Sources des Données et Reproductibilité",
        "months": {1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril", 5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août", 9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"},
        "months_short": ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
    },
    "EN": {
        "title": "Urban Heat Island (UHI) & Thermal Vulnerability Observatory — Paris",
        "subtitle": "Integration of Landsat 8/9 satellite telemetry (30m pixels), Sentinel-2 vegetation index (10m), and borough-level demographic exposure.",
        "g_lst_t": "LST (Land Surface Temperature)",
        "g_lst_d": "Radiative skin temperature emitted by roofs, streets, and ground (°C) at 30m resolution. Captures surface material heating.",
        "g_ndvi_t": "NDVI (Vegetation Index)",
        "g_ndvi_d": "Scale from -1 to +1 measuring photosynthetic vegetation density. < 0.15 indicates impervious stone/asphalt; > 0.40 indicates wooded parks.",
        "g_pop_t": "Demographic Exposure",
        "g_pop_d": "Permanent resident population per arrondissement (WorldPop). Weights the volume of citizens directly exposed to thermal stress.",
        "g_uvi_t": "UVI Index (0 to 100 pts)",
        "g_uvi_d": "Composite priority metric: 50% surface temperature (LST) + 30% vegetation deficit (1 - NDVI) + 20% population exposure.",
        "sb_lang": "Language / Langue / Idioma",
        "sb_params": "Study Parameters",
        "sb_years": "Analysis Period (Years)",
        "sb_years_help": "Select a multi-year range or set both sliders to the same year to evaluate a single year.",
        "sb_month": "Comparative Evaluation Month",
        "sb_arr": "Arrondissements (1er to 20ème)",
        "sb_map_cfg": "Cartographic Layers",
        "sb_basemap": "Basemap (Streets & Buildings)",
        "sb_opacity": "Thermal Pixel Opacity (Landsat)",
        "sb_opacity_help": "Setting opacity between 0.40 and 0.55 allows clear visibility of streets, avenues, and building footprints beneath the heat layer.",
        "sb_borders": "Show Arrondissement Boundaries",
        "sb_labels": "Overlay Street & Neighborhood Names",
        "warn_arr": "Please select at least one arrondissement in the sidebar.",
        "kpi1": "Mean Borough LST",
        "kpi2": "Mean UVI Index",
        "kpi3": "Most Critical Arrondissement",
        "kpi4": "Vegetation Cover (NDVI)",
        "kpi5": "Analyzed Population",
        "active_zones": "active arrondissements",
        "map_title": "Pixel-Level Thermal Cartography (30m) & Urban Fabric — Summers",
        "map_caption": "Hover over any arrondissement to inspect its metrics, or zoom in to examine specific streets, rail yards, and buildings.",
        "scale_1": "22 °C (Seine River / Urban Woods)",
        "scale_2": "28 °C (Tree-lined Parks)",
        "scale_3": "33 °C (Residential Fabric)",
        "scale_4": "38 °C (Major Arterials / Rail Stations)",
        "scale_5": "44+ °C (Industrial Roofs / Dense Asphalt)",
        "rank_title": "Vulnerability Index (UVI) Ranking",
        "rank_caption": "Ordered from highest to lowest combined thermal risk. Bar color reflects mean surface temperature (°C).",
        "tab1": "Multi-Year Time Series",
        "tab2": "Seasonal Matrix (Month vs. Arrondissement)",
        "tab3": "Vegetation vs. Temperature Correlation",
        "tab4": "Tabular Data & Export",
        "t1_sub": "Comparative Monthly Dynamics",
        "t1_radio": "Variable to display in historical time series:",
        "t2_sub": "Mean Land Surface Temperature Matrix (°C)",
        "t2_cap": "Each cell displays the mean surface temperature (°C) per arrondissement and month across the selected period.",
        "t3_sub": "Vegetative Cooling Effect & Demographic Exposure",
        "t3_cap": "X-Axis: Vegetation Index (NDVI) | Y-Axis: Surface Temperature (°C) | Bubble Size: Population | Color: UVI Index.",
        "t4_sub": "Auditable Data Table by Arrondissement",
        "dl_btn": "Download filtered table (CSV)",
        "ref_title": "Scientific References, Data Sources & Reproducibility",
        "months": {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"},
        "months_short": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    }
}

# 3. SELECTOR DE IDIOMA EN BARRA LATERAL
lang_code = st.sidebar.radio(
    "🌐 Language / Langue / Idioma",
    options=["FR", "EN", "ES"],
    format_func=lambda x: {"FR": "Français", "EN": "English", "ES": "Español"}[x],
    horizontal=True,
    index=2
)
T = TRANSLATIONS[lang_code]

# 4. ENCABEZADO Y GLOSARIO TÉCNICO
st.title(T["title"])
st.caption(T["subtitle"])

g1, g2, g3, g4 = st.columns(4)
with g1:
    st.markdown(f"""<div class="glossary-box"><span class="glossary-title">{T["g_lst_t"]}</span>{T["g_lst_d"]}</div>""", unsafe_allow_html=True)
with g2:
    st.markdown(f"""<div class="glossary-box"><span class="glossary-title">{T["g_ndvi_t"]}</span>{T["g_ndvi_d"]}</div>""", unsafe_allow_html=True)
with g3:
    st.markdown(f"""<div class="glossary-box"><span class="glossary-title">{T["g_pop_t"]}</span>{T["g_pop_d"]}</div>""", unsafe_allow_html=True)
with g4:
    st.markdown(f"""<div class="glossary-box"><span class="glossary-title">{T["g_uvi_t"]}</span>{T["g_uvi_d"]}</div>""", unsafe_allow_html=True)

st.write("")

import os
import json

# 5. CONEXIÓN HÍBRIDA A GOOGLE EARTH ENGINE (LOCAL JSON PRIMERO, CLOUD SECRETS DESPUÉS)
@st.cache_resource
def init_ee():
    try:
        service_account = 'uhi-streamlit-app@titanium-vision-322421.iam.gserviceaccount.com'
        if os.path.exists('gee_credentials.json'):
            credentials = ee.ServiceAccountCredentials(service_account, 'gee_credentials.json')
        else:
            key_dict = dict(st.secrets["gee_service_account"])
            credentials = ee.ServiceAccountCredentials(service_account, key_data=json.dumps(key_dict))
        ee.Initialize(credentials, project='titanium-vision-322421')
        return True
    except Exception as e:
        return str(e)

auth_status = init_ee()
if auth_status is not True:
    st.error(f"Earth Engine Authentication Error: {auth_status}")
    st.stop()

# 6. CARGA DE DATOS TABULARES Y GEOJSON
@st.cache_data
def load_tabular_data():
    import os
# ...
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "uhi_timeseries_master.csv")
df = pd.read_csv(csv_path)
    for col in ['LST_Landsat_30m', 'NDVI_S2_10m', 'Population_Count']:
        df[f'{col}_norm'] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
    df['NDVI_inv'] = 1 - df['NDVI_S2_10m_norm']
    df['UVI'] = ((0.5 * df['LST_Landsat_30m_norm']) + 
                 (0.3 * df['NDVI_inv']) + 
                 (0.2 * df['Population_Count_norm'])) * 100
    df['zone_num'] = df['zone_id'].astype(int)
    df['arr_label'] = df['zone_num'].apply(fmt_arr)
    df['date'] = pd.to_datetime(df['year'].astype(str) + '-' + df['month'].astype(str).str.zfill(2) + '-01')
    return df

@st.cache_data
def load_paris_geojson():
    url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/arrondissements/exports/geojson"
    return requests.get(url).json()

df = load_tabular_data()
geojson_paris = load_paris_geojson()

# 7. CONTROLES LATERALES
st.sidebar.divider()
st.sidebar.subheader(T["sb_params"])

min_yr, max_yr = int(df['year'].min()), int(df['year'].max())
year_range = st.sidebar.slider(
    T["sb_years"],
    min_value=min_yr,
    max_value=max_yr,
    value=(2020, max_yr),
    help=T["sb_years_help"]
)

selected_month = st.sidebar.selectbox(
    T["sb_month"],
    options=list(T["months"].keys()),
    format_func=lambda x: f"{x:02d} — {T['months'][x]}",
    index=6
)

all_arrs = [fmt_arr(i) for i in sorted(df['zone_num'].unique())]
selected_arrs = st.sidebar.multiselect(
    T["sb_arr"],
    options=all_arrs,
    default=all_arrs
)

if not selected_arrs:
    st.warning(T["warn_arr"])
    st.stop()

st.sidebar.divider()
st.sidebar.subheader(T["sb_map_cfg"])

basemap_catalog = {
    "OpenStreetMap (Calles + Edificios)": "OpenStreetMap",
    "CartoDB Voyager ( Urbano Nítido)": "https://{s}.basemaps.cartocdn.com/rastertiles/voyager_nolabels/{z}/{x}/{y}{r}.png",
    "CartoDB Positron (Gris Claro)": "https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png",
    "Esri World Imagery (Satélite Real)": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
}
selected_basemap = st.sidebar.selectbox(T["sb_basemap"], list(basemap_catalog.keys()), index=0)

raster_opacity = st.sidebar.slider(
    T["sb_opacity"],
    min_value=0.15,
    max_value=0.95,
    value=0.48,
    step=0.05,
    help=T["sb_opacity_help"]
)
show_borders = st.sidebar.checkbox(T["sb_borders"], value=True)
show_street_labels = st.sidebar.checkbox(T["sb_labels"], value=True)

# 8. FILTRADO Y AGREGACIÓN DE DATOS
df_period_all = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1]) & (df['arr_label'].isin(selected_arrs))].copy()
df_month_raw = df_period_all[df_period_all['month'] == selected_month]

df_agg = df_month_raw.groupby(['zone_num', 'arr_label'], as_index=False).agg({
    'LST_Landsat_30m': 'mean',
    'NDVI_S2_10m': 'mean',
    'Population_Count': 'mean',
    'UVI': 'mean'
}).sort_values('zone_num')

period_str = f"{year_range[0]}" if year_range[0] == year_range[1] else f"{year_range[0]}–{year_range[1]}"

# 9. TARJETAS KPI
crit_row = df_agg.loc[df_agg['UVI'].idxmax()]
k1, k2, k3, k4, k5 = st.columns(5)

k1.metric(T["kpi1"], f"{df_agg['LST_Landsat_30m'].mean():.1f} °C", f"Max: {df_agg['LST_Landsat_30m'].max():.1f} °C ({crit_row['arr_label']})")
k2.metric(T["kpi2"], f"{df_agg['UVI'].mean():.1f} / 100", f"Min: {df_agg['UVI'].min():.1f} | Max: {df_agg['UVI'].max():.1f}")
k3.metric(T["kpi3"], f"{crit_row['arr_label']}", f"UVI: {crit_row['UVI']:.1f} pts ({crit_row['LST_Landsat_30m']:.1f} °C)")
k4.metric(T["kpi4"], f"{df_agg['NDVI_S2_10m'].mean():.2f}", f"Min: {df_agg['NDVI_S2_10m'].min():.2f}")
k5.metric(T["kpi5"], f"{int(df_agg['Population_Count'].sum()):,} hab.", f"{len(selected_arrs)} / 20 {T['active_zones']}")

st.write("")

# 10. MOTOR RASTER GOOGLE EARTH ENGINE CON MÁSCARA DE NUBES
@st.cache_data(show_spinner=False)
def get_ee_raster_url(yr_start, yr_end):
    roi = ee.Geometry.Point([2.3522, 48.8566]).buffer(13000)

    def mask_l89_sr(image):
        qa = image.select('QA_PIXEL')
        cloud_shadow_bit_mask = (1 << 4)
        clouds_bit_mask = (1 << 3)
        mask = qa.bitwiseAnd(cloud_shadow_bit_mask).eq(0).And(qa.bitwiseAnd(clouds_bit_mask).eq(0))
        return image.updateMask(mask)

    l8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').filterBounds(roi) \
        .filter(ee.Filter.calendarRange(yr_start, yr_end, 'year')) \
        .filter(ee.Filter.calendarRange(6, 8, 'month')) \
        .map(mask_l89_sr)
    l9 = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2').filterBounds(roi) \
        .filter(ee.Filter.calendarRange(yr_start, yr_end, 'year')) \
        .filter(ee.Filter.calendarRange(6, 8, 'month')) \
        .map(mask_l89_sr)

    landsat = l8.merge(l9)
    image = landsat.median()
    lst_celsius = image.select('ST_B10').multiply(0.00341802).add(149.0).subtract(273.15).clip(roi)

    vis_params = {
        'min': 22,
        'max': 44,
        'palette': [
            '#2b5c8f', '#3885b8', '#59b3d1', '#95d6c6',
            '#e3ecc2', '#fed884', '#fca052', '#ea5c36',
            '#c42528', '#7f000d'
        ]
    }
    map_id_dict = ee.Image(lst_celsius).getMapId(vis_params)
    return map_id_dict['tile_fetcher'].url_format

# 11. SECCIÓN CENTRAL: MAPA MULTICAPA + RANKING
col_map, col_rank = st.columns([1.45, 1], gap="large")

with col_map:
    st.subheader(f"{T['map_title']} ({period_str})")
    st.caption(T["map_caption"])

    df_all_20 = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1]) & (df['month'] == selected_month)] \
        .groupby(['zone_num', 'arr_label'], as_index=False).mean(numeric_only=True)
    stats_lookup = df_all_20.set_index('zone_num').to_dict('index')

    geojson_enriched = {"type": "FeatureCollection", "features": []}
    for feat in geojson_paris['features']:
        f_copy = dict(feat)
        props = dict(f_copy['properties'])
        z_num = int(props.get('c_ar'))
        props['arr_nom'] = fmt_arr(z_num)
        if z_num in stats_lookup:
            s = stats_lookup[z_num]
            props['lst_val'] = f"{s['LST_Landsat_30m']:.1f} °C"
            props['ndvi_val'] = f"{s['NDVI_S2_10m']:.2f}"
            props['pop_val'] = f"{int(s['Population_Count']):,} hab."
            props['uvi_val'] = f"{s['UVI']:.1f} / 100"
        else:
            props['lst_val'] = props['ndvi_val'] = props['pop_val'] = props['uvi_val'] = "N/A"
        f_copy['properties'] = props
        geojson_enriched['features'].append(f_copy)

    # Nivel 1: Mapa Base de Calles y Edificios
    b_url = basemap_catalog[selected_basemap]
    if b_url == "OpenStreetMap":
        m = folium.Map(location=[48.8566, 2.3522], zoom_start=12, tiles="OpenStreetMap")
    else:
        m = folium.Map(location=[48.8566, 2.3522], zoom_start=12, tiles=None)
        folium.TileLayer(tiles=b_url, attr="CartoDB / Esri", name="Base Map", control=False).add_to(m)

    # Nivel 2: Capa de Píxeles Térmicos Landsat (30m) con transparencia para ver edificios debajo
    try:
        tile_url = get_ee_raster_url(year_range[0], year_range[1])
        folium.TileLayer(
            tiles=tile_url,
            attr='USGS Landsat 8/9 | Google Earth Engine',
            name=f'LST 30m ({period_str})',
            overlay=True,
            control=True,
            opacity=raster_opacity
        ).add_to(m)
    except Exception as e:
        st.warning(f"Satellite layer notice: {e}")

    # Nivel 3: Etiquetas de calles y barrios POR ENCIMA del calor para legibilidad urbana
    if show_street_labels:
        folium.TileLayer(
            tiles="https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}{r}.png",
            attr="CartoDB Labels",
            name="Street & Quarter Labels",
            overlay=True,
            control=True,
            opacity=0.90
        ).add_to(m)

    # Nivel 4: Límites vectoriales de los Arrondissements (1er al 20ème)
    if show_borders:
        def style_function(feature):
            arr_nom = feature['properties'].get('arr_nom')
            is_sel = arr_nom in selected_arrs
            filtering_active = len(selected_arrs) < 20
            return {
                'fillColor': '#0ea5e9' if (is_sel and filtering_active) else 'transparent',
                'color': '#0f172a' if is_sel else '#475569',
                'weight': 2.8 if is_sel else 1.2,
                'dashArray': '1' if is_sel else '4, 4',
                'fillOpacity': 0.08 if (is_sel and filtering_active) else 0.0
            }

        def highlight_function(feature):
            return {
                'fillColor': '#ffffff',
                'color': '#dc2626',
                'weight': 3.8,
                'fillOpacity': 0.18
            }

        folium.GeoJson(
            geojson_enriched,
            name="Arrondissements (1er - 20ème)",
            style_function=style_function,
            highlight_function=highlight_function,
            tooltip=folium.GeoJsonTooltip(
                fields=['arr_nom', 'l_ar', 'uvi_val', 'lst_val', 'ndvi_val', 'pop_val'],
                aliases=[
                    'Arrondissement:',
                    'Nom officiel:',
                    f'UVI ({T["months"][selected_month]}):',
                    'LST (Temp. Surface):',
                    'NDVI (Végétation):',
                    'Population:'
                ],
                localize=True,
                style="background-color: #0f172a; color: #f8fafc; font-family: sans-serif; font-size: 12px; padding: 10px; border-radius: 4px; border: 1px solid #38bdf8;"
            )
        ).add_to(m)

    folium.LayerControl(collapsed=True).add_to(m)
    st_folium(m, width=None, height=540, returned_objects=[])

    # Leyenda térmica continua
    st.markdown(f"""
    <div style="background: linear-gradient(to right, #2b5c8f, #59b3d1, #95d6c6, #e3ecc2, #fed884, #fca052, #ea5c36, #c42528, #7f000d); height: 10px; border-radius: 2px; margin-top: 4px;"></div>
    <div style="display: flex; justify-content: space-between; font-size: 11.5px; color: #9ca3af; margin-top: 4px;">
        <span><b>{T['scale_1']}</b></span>
        <span><b>{T['scale_2']}</b></span>
        <span><b>{T['scale_3']}</b></span>
        <span><b>{T['scale_4']}</b></span>
        <span><b>{T['scale_5']}</b></span>
    </div>
    """, unsafe_allow_html=True)

with col_rank:
    st.subheader(f"{T['rank_title']} ({T['months'][selected_month]}, {period_str})")
    st.caption(T["rank_caption"])
    
    df_rank = df_agg.sort_values('UVI', ascending=True).copy()
    
    fig_bar = px.bar(
        df_rank,
        x='UVI',
        y='arr_label',
        orientation='h',
        color='LST_Landsat_30m',
        color_continuous_scale='YlOrRd',
        text=df_rank.apply(lambda r: f"{r['UVI']:.1f} pts ({r['LST_Landsat_30m']:.1f}°C)", axis=1),
        labels={
            'UVI': 'UVI (0-100)',
            'arr_label': 'Arrondissement',
            'LST_Landsat_30m': 'LST (°C)'
        }
    )
    fig_bar.update_traces(textposition='outside', cliponaxis=False)
    fig_bar.update_layout(
        height=585,
        margin=dict(l=0, r=55, t=10, b=10),
        xaxis_range=[0, 110],
        yaxis={'categoryorder': 'array', 'categoryarray': df_rank['arr_label'].tolist()},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        coloraxis_colorbar=dict(title="LST (°C)", thickness=12)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# 12. PESTAÑAS DE ANÁLISIS HISTÓRICO Y ESTADÍSTICO
tab1, tab2, tab3, tab4 = st.tabs([T["tab1"], T["tab2"], T["tab3"], T["tab4"]])

with tab1:
    st.subheader(f"{T['t1_sub']} ({period_str})")
    metric_choice = st.radio(
        T["t1_radio"],
        ["LST_Landsat_30m", "UVI", "NDVI_S2_10m"],
        format_func=lambda x: {
            "LST_Landsat_30m": "LST (°C)",
            "UVI": "UVI (0-100)",
            "NDVI_S2_10m": "NDVI (-1 to +1)"
        }[x],
        horizontal=True
    )
    fig_line = px.line(
        df_period_all.sort_values(['date', 'zone_num']),
        x='date',
        y=metric_choice,
        color='arr_label',
        labels={'date': 'Date', metric_choice: metric_choice, 'arr_label': 'Arrondissement'}
    )
    fig_line.update_layout(height=440, hovermode="x unified", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_line, use_container_width=True)

with tab2:
    st.subheader(f"{T['t2_sub']} ({period_str})")
    st.caption(T["t2_cap"])
    
    df_matrix = df_period_all.groupby(['zone_num', 'arr_label', 'month'], as_index=False)['LST_Landsat_30m'].mean()
    df_pivot = df_matrix.sort_values('zone_num').pivot(index='zone_num', columns='month', values='LST_Landsat_30m')
    df_pivot.index = [fmt_arr(i) for i in df_pivot.index]

    fig_heat = px.imshow(
        df_pivot,
        text_auto=".1f",
        aspect="auto",
        color_continuous_scale="YlOrRd",
        labels=dict(x="Month", y="Arrondissement", color="LST (°C)"),
        x=T["months_short"]
    )
    fig_heat.update_layout(height=540, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_heat, use_container_width=True)

with tab3:
    st.subheader(f"{T['t3_sub']} ({T['months'][selected_month]}, {period_str})")
    st.caption(T["t3_cap"])
    
    fig_scatter = px.scatter(
        df_agg,
        x="NDVI_S2_10m",
        y="LST_Landsat_30m",
        size="Population_Count",
        color="UVI",
        text="arr_label",
        color_continuous_scale="YlOrRd",
        size_max=42,
        labels={
            "NDVI_S2_10m": "NDVI (Sentinel-2)",
            "LST_Landsat_30m": "LST (°C - Landsat 8/9)",
            "Population_Count": "Population",
            "UVI": "UVI Index"
        }
    )
    fig_scatter.update_traces(textposition='top center')
    fig_scatter.update_layout(height=480, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_scatter, use_container_width=True)

with tab4:
    st.subheader(f"{T['t4_sub']} ({T['months'][selected_month]}, {period_str})")
    df_table = df_agg[['arr_label', 'LST_Landsat_30m', 'NDVI_S2_10m', 'Population_Count', 'UVI']].sort_values('UVI', ascending=False).copy()
    df_table.columns = ['Arrondissement', 'LST (°C)', 'NDVI', 'Population', 'UVI (0-100)']
    
    st.dataframe(
        df_table.style.format({
            'LST (°C)': '{:.2f} °C',
            'NDVI': '{:.3f}',
            'Population': '{:,.0f}',
            'UVI (0-100)': '{:.1f}'
        }),
        use_container_width=True,
        height=420,
        hide_index=True
    )
    csv_out = df_table.to_csv(index=False).encode('utf-8')
    st.download_button(
        T["dl_btn"],
        data=csv_out,
        file_name=f"uhi_paris_{period_str}_{selected_month:02d}.csv",
        mime="text/csv"
    )

st.divider()

# 13. PIE DE PÁGINA: REFERENCIAS CIENTÍFICAS Y BIBLIOGRAFÍA
st.subheader(T["ref_title"])
st.markdown("""
<div class="ref-box">
<b>1. Telemetría Térmica (Land Surface Temperature - LST):</b><br>
• U.S. Geological Survey (USGS) & NASA. <i>Landsat 8-9 OLI/TIRS Collection 2 Level-2 Science Products (ST_B10 Surface Temperature)</i>. Resolución espacial: 30 m. Ecuación de calibración radiométrica: $LST (°C) = (DN \\times 0.00341802 + 149.0) - 273.15$. <a href="https://doi.org/10.5066/P9OGBGM6" target="_blank">https://doi.org/10.5066/P9OGBGM6</a><br><br>
<b>2. Cobertura Fotosintética y Vegetación Urbana (NDVI):</b><br>
• European Space Agency (ESA) — Copernicus Programme. <i>Sentinel-2 MSI Level-2A Surface Reflectance (Bandas B8 NIR y B4 Red, resolución 10 m)</i>. $NDVI = (NIR - Red) / (NIR + Red)$. <a href="https://dataspace.copernicus.eu/" target="_blank">https://dataspace.copernicus.eu/</a><br><br>
<b>3. Demografía y Límites Administrativos:</b><br>
• Tatem, A. J. (2017). <i>WorldPop, open data for spatial demography</i>. Scientific Data, 4, 170004. <a href="https://www.worldpop.org/" target="_blank">https://www.worldpop.org/</a><br>
• Ville de Paris — Open Data Paris. <i>Référentiel géographique des Arrondissements de Paris (1er au 20ème)</i>. <a href="https://opendata.paris.fr/" target="_blank">https://opendata.paris.fr/</a><br><br>
<b>4. Marco Teórico de Islas de Calor Urbano (UHI) y Vulnerabilidad:</b><br>
• Oke, T. R. (1982). <i>The energetic basis of the urban heat island</i>. Quarterly Journal of the Royal Meteorological Society, 108(455), 1-24.<br>
• Atelier Parisien d'Urbanisme (APUR). (2023). <i>Les îlots de chaleur urbains à Paris : diagnostic et adaptation climatique</i>. Paris, France.<br>
• Gorelick, N., Hancher, M., Dixon, M., Ilyushchenko, S., Thau, D., & Moore, R. (2017). <i>Google Earth Engine: Planetary-scale geospatial analysis for everyone</i>. Remote Sensing of Environment, 202, 18-27.
</div>
""", unsafe_allow_html=True)
