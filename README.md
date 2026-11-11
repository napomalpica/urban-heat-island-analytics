*Read the [English version below](#english-version)*

# Urban Heat Island (UHI) Analytics Pipeline

Este repositorio contiene el código fuente para procesar, analizar y clasificar la Isla de Calor Urbana (UHI) utilizando datos satelitales y de reanálisis climático. 

El proyecto toma datos espaciales brutos, corrige vacíos de información por nubosidad, aplica algoritmos de clustering y genera un modelo de datos estructurado listo para ser consumido por herramientas de Business Intelligence.

## Pipeline de datos

El flujo de trabajo se divide en dos componentes técnicos:

### 1. Extracción y procesamiento (Python / Google Earth Engine)
El script principal (`01_uhi_preprocessing_pipeline.ipynb`) realiza las siguientes operaciones:
- **Fusión de sensores:** Extrae series temporales de Sentinel-2 (NDVI, 10m) y Landsat 8/9 (LST, 30m) utilizando la API de Google Earth Engine.
- **Variables macroclimáticas:** Integra datos de temperatura del aire a 2 metros y humedad volumétrica del suelo provenientes de ERA5-Land.
- **Tratamiento de nulos:** Implementa un método de interpolación temporal para corregir lecturas perdidas por alta cobertura de nubes, generando columnas de auditoría para trazar los datos proyectados.
- **Clustering:** Aplica K-Means (k=3) sobre las variables estandarizadas para clasificar las zonas en tres niveles relativos de vulnerabilidad térmica.

### 2. Visualización y modelado (Power BI)
El archivo CSV resultante alimenta un dashboard interactivo que cruza las variables espaciales y categoriza dinámicamente los niveles de riesgo (ej. estrés hídrico del suelo) mediante fórmulas DAX, basándose en umbrales de literatura científica.

## Dashboard

Vista general del panel implementado para el cruce de variables ambientales:

<p align="center">
  <img src="dashboard.png" alt="Vista del Dashboard en Power BI" width="100%">
</p>

## Notas metodológicas y limitaciones

Para interpretar correctamente los resultados de este modelo, es necesario considerar las siguientes limitaciones físicas y espaciales:

- **LST vs. T2m:** La temperatura de superficie (Landsat) mide la radiación de los materiales, que siempre será significativamente mayor a la temperatura del aire durante el día. El modelo no las iguala, sino que evalúa su desacoplamiento estacional.
- **Escala de ERA5:** Los datos de reanálisis tienen una resolución nativa de aproximadamente 9 km. Se utilizan como un indicador de la tendencia macroclimática (balance hídrico estacional) y no como mediciones microclimáticas a nivel de calle.
- **MAUP (Modifiable Areal Unit Problem):** Al realizar reducciones espaciales (medias) a nivel de distrito o código postal, se asume una dilución de los microclimas internos, promediando zonas altamente asfaltadas con parques urbanos dentro del mismo polígono.

---

<a name="english-version"></a>
# Urban Heat Island (UHI) Analytics Pipeline (English)

This repository contains the source code to process, analyze, and classify the Urban Heat Island (UHI) effect using satellite and climate reanalysis data. 

The project takes raw spatial data, corrects missing information due to cloud cover, applies clustering algorithms, and outputs a structured data model ready for Business Intelligence tools.

## Data Pipeline

The workflow is divided into two technical components:

### 1. Extraction and processing (Python / Google Earth Engine)
The main script (`01_uhi_preprocessing_pipeline.ipynb`) performs the following operations:
- **Sensor fusion:** Extracts time series from Sentinel-2 (NDVI, 10m) and Landsat 8/9 (LST, 30m) using the Google Earth Engine API.
- **Macroclimatic variables:** Integrates 2-meter air temperature and volumetric soil moisture data from ERA5-Land.
- **Null treatment:** Implements a temporal interpolation method to correct missing readings due to high cloud cover, generating audit columns to track projected data.
- **Clustering:** Applies K-Means (k=3) on standardized variables to classify zones into three relative levels of thermal vulnerability.

### 2. Visualization and modeling (Power BI)
The resulting CSV file feeds an interactive dashboard that cross-references spatial variables and dynamically categorizes risk levels (e.g., soil water stress) using DAX formulas, based on thresholds from scientific literature.

## Dashboard

Overview of the implemented dashboard for cross-referencing environmental variables:

<p align="center">
  <img src="dashboard.png" alt="Power BI Dashboard View" width="100%">
</p>

## Methodological notes and limitations

To correctly interpret the results of this model, the following physical and spatial limitations must be considered:

- **LST vs. T2m:** Land Surface Temperature (Landsat) measures the radiation of materials, which will always be significantly higher than the air temperature during the day. The model does not equate them, but rather evaluates their seasonal decoupling.
- **ERA5 Scale:** Reanalysis data has a native resolution of approximately 9 km. They are used as an indicator of macroclimatic trends (seasonal water balance) and not as street-level microclimatic measurements.
- **MAUP (Modifiable Areal Unit Problem):** By performing spatial reductions (averages) at the district or postal code level, the model assumes a dilution of internal microclimates, averaging highly paved areas with urban parks within the same polygon.
