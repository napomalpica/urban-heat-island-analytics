*Read the [English version below](#english-version)*

# Análisis y Observatorio de Islas de Calor Urbano (UHI)

Este repositorio contiene el flujo de trabajo completo para extraer, procesar y visualizar el fenómeno de Isla de Calor Urbana (UHI) y la exposición térmica de la población a partir de imágenes satelitales y datos demográficos. 

Aunque el caso de estudio principal está configurado para los **20 arrondissements de París (1er al 20ème)** entre 2016 y 2026, la arquitectura está diseñada para ser replicable en cualquier otra ciudad.

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

## Cómo ejecutar el observatorio (Etapa 2) en local

1. Clona este repositorio y entra en la carpeta de la segunda etapa:
   ```bash
   git clone [https://github.com/napomalpica/urban-heat-island-analytics.git](https://github.com/napomalpica/urban-heat-island-analytics.git)
   cd urban-heat-island-analytics/etapa_2_observatorio
