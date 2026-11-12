*Read the [English version below](#english-version)*

# Análisis y Observatorio de Islas de Calor Urbano (UHI)

Este repositorio contiene el flujo de trabajo completo para extraer, procesar y visualizar el fenómeno de Isla de Calor Urbana (UHI) y la exposición térmica de la población a partir de imágenes satelitales y datos demográficos. 

Aunque el caso de estudio principal está configurado para los **20 arrondissements de París (1er al 20ème)** entre 2016 y 2026, la estructura está pensada para poder replicarse en cualquier otra ciudad.

---

## Organización del repositorio (Dos Etapas)

El proyecto se divide en dos fases independientes pero complementarias:

* **`uhi_data_pipeline.ipynb` (Etapa 1 — Extracción y procesamiento de datos):** Notebook en Python conectado a Google Earth Engine que filtra la nubosidad, procesa las colecciones satelitales (Landsat 8/9, Sentinel-2, ERA5-Land y WorldPop) y genera la serie histórica consolidada por distrito para su análisis estadístico o uso en herramientas como Power BI.
* **`etapa_2_observatorio/` (Etapa 2 — Visor cartográfico web en tiempo real):** Aplicación interactiva desarrollada en Streamlit y Folium (disponible en español, francés e inglés). Conecta en vivo con los servidores de Google Earth Engine para dibujar los píxeles reales de calor (resolución de 30x30 metros) sobre el mapa de calles y edificios de la ciudad, superponiendo los límites administrativos, gráficos de evolución histórica y tablas de datos descargables.

---

## ¿Qué mide cada indicador? (Guía rápida)

Para que la herramienta sea útil tanto en análisis técnico como en gestión urbana, el observatorio resume la información en cuatro variables:

1. **Temperatura de Superficie — LST (°C):** Es el calor directo que emiten los tejados, el asfalto y el suelo al calentarse con el sol, medido por el sensor térmico de los satélites Landsat 8 y 9 cada 30 metros. No debe confundirse con la temperatura del aire a la sombra: mide qué materiales y calles acumulan más calor.
2. **Índice de Vegetación — NDVI (escala de -1 a +1):** Mide la presencia y densidad de árboles y áreas verdes mediante el satélite Sentinel-2 (a 10 metros de detalle). Valores cercanos a `0` corresponden a piedra, cemento o asfalto; valores por encima de `0.40` indican parques arbolados.
3. **Exposición Demográfica (Habitantes):** Número de residentes permanentes dentro de cada distrito (datos de WorldPop). Permite diferenciar entre una zona industrial muy cálida pero deshabitada y un barrio residencial denso donde el calor afecta a miles de personas.
4. **Índice de Vulnerabilidad Urbana — UVI (0 a 100 puntos):** Indicador sintético pensado para priorizar intervenciones urbanas (como arbolado o adaptación de espacios públicos). Combina en una sola escala la temperatura superficial (50%), el déficit de vegetación (30%) y la población residente (20%).

---

## Cómo ejecutar el observatorio (Etapa 2) en tu computadora

1. Clona este repositorio y entra en la carpeta de la segunda etapa:
   `git clone https://github.com/napomalpica/urban-heat-island-analytics.git`
   `cd urban-heat-island-analytics/etapa_2_observatorio`

2. Instala las librerías de Python requeridas:
   `pip install -r requirements.txt`

3. **Credenciales de Google Earth Engine:** Para procesar los píxeles satelitales en vivo, crea una cuenta de servicio (*Service Account*) en Google Cloud con permisos de Earth Engine, descarga su clave privada JSON y guárdala dentro de `etapa_2_observatorio/` con el nombre `gee_credentials.json`. Luego actualiza el correo de tu cuenta de servicio en la función `init_ee()` dentro de `app.py`.

4. Inicia la aplicación:
   `streamlit run app.py`

---

## Cómo adaptar este proyecto a otra ciudad

1. **Generar los datos (Etapa 1):** Ejecuta el notebook `uhi_data_pipeline.ipynb` reemplazando la geometría de estudio por los polígonos de los barrios o comunas de la nueva ciudad para exportar su archivo `uhi_timeseries_master.csv`.
2. **Actualizar el visor (Etapa 2):** En `etapa_2_observatorio/app.py`, cambia las coordenadas centrales de París (`[48.8566, 2.3522]`) por las de tu ciudad y reemplaza la dirección del archivo GeoJSON en `load_paris_geojson()` por los límites municipales correspondientes.

---

<a name="english-version"></a>

# Urban Heat Island (UHI) Analytics & Observatory

This repository provides a complete workflow to extract, process, and visualize Urban Heat Islands (UHI) and population heat exposure using multi-sensor satellite telemetry and spatial demographic data.

While the primary case study covers the **20 arrondissements of Paris (1er to 20ème)** from 2016 to 2026, the entire pipeline is region-agnostic and can be replicated in any city worldwide.

---

## Repository Structure (Two-Stage Workflow)

The project is organized into two distinct stages:

* **`uhi_data_pipeline.ipynb` (Stage 1 — Cloud ETL & Data Pipeline):** Python notebook powered by Google Earth Engine that applies cloud masking, aggregates satellite collections (Landsat 8/9, Sentinel-2, ERA5-Land, and WorldPop) across municipal polygons, and exports the master time-series dataset for statistical modeling or Power BI dashboards.
* **`etapa_2_observatorio/` (Stage 2 — Interactive Pixel & Vector Web Observatory):** Web application built with Streamlit and Folium (with full toggle between French, English, and Spanish). It connects directly to Google Earth Engine to render 30x30m thermal pixels over city streets and building footprints, combined with administrative boundaries, multi-year charts, and exportable data tables.

---

## Plain-Language Guide to the Indicators

1. **Land Surface Temperature — LST (°C):** Direct radiative heat emitted by roofs, streets, and ground surfaces under solar radiation, measured by Landsat 8/9 thermal sensors at 30-meter resolution. It reflects how hot urban materials get rather than ambient air temperature.
2. **Vegetation Index — NDVI (-1 to +1):** Quantifies the density and health of trees and green cover using Sentinel-2 imagery (10-meter resolution). Values near `0` indicate bare stone or asphalt; values above `0.40` indicate wooded parks.
3. **Demographic Exposure (Inhabitants):** Permanent resident population per district (WorldPop). This separates hot but uninhabited industrial zones from densely populated neighborhoods facing severe heat stress.
4. **Urban Vulnerability Index — UVI (0 to 100 points):** Practical composite score designed to help prioritize climate adaptation measures. It combines surface heat (50%), lack of vegetation (30%), and resident population (20%) into a single 0–100 scale.

---

## Running Stage 2 Locally

1. Clone this repository and navigate to the Stage 2 directory:
   `git clone https://github.com/napomalpica/urban-heat-island-analytics.git`
   `cd urban-heat-island-analytics/etapa_2_observatorio`

2. Install the required libraries:
   `pip install -r requirements.txt`

3. **Google Earth Engine Credentials:** Create a Google Cloud Service Account enabled for Earth Engine, download its JSON private key as `gee_credentials.json` inside `etapa_2_observatorio/`, and set your service account email inside `init_ee()` in `app.py`.

4. Launch the dashboard:
   `streamlit run app.py`

---

## Scientific References & Data Sources

* **Land Surface Temperature (LST):** U.S. Geological Survey (USGS) & NASA — *Landsat 8/9 OLI/TIRS Collection 2 Level-2 Science Products (`ST_B10`, 30m)*. Calibration formula: `LST (°C) = (ST_B10 * 0.00341802 + 149.0) - 273.15`. https://doi.org/10.5066/P9OGBGM6
* **Surface Reflectance & Vegetation (NDVI):** European Space Agency (ESA) / Copernicus — *Sentinel-2 MSI Level-2A (Bands B8 NIR and B4 Red, 10m)*. https://dataspace.copernicus.eu/
* **Climate Reanalysis:** ECMWF — *ERA5-Land Hourly and Monthly Data*. https://cds.climate.copernicus.eu/
* **Spatial Demography:** Tatem, A. J. (2017). *WorldPop, open data for spatial demography*. Scientific Data, 4, 170004. https://www.worldpop.org/
* **Municipal Boundaries:** Mairie de Paris — *Open Data Paris (Arrondissements 1er au 20ème)*. https://opendata.paris.fr/
* **Reference Literature:**
  * Oke, T. R. (1982). *The energetic basis of the urban heat island*. Quarterly Journal of the Royal Meteorological Society, 108(455), 1–24.
  * Atelier Parisien d'Urbanisme — APUR (2023). *Les îlots de chaleur urbains à Paris : diagnostic et adaptation climatique*.
  * Gorelick, N., et al. (2017). *Google Earth Engine: Planetary-scale geospatial analysis for everyone*. Remote Sensing of Environment, 202, 18–27.
