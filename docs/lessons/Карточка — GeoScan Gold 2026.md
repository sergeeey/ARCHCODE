---
tags:
  - project-card
  - geoscan
  - geospatial
created: '2026-04-12'
---
# GeoScan Gold 2026 (v3.0)

**Одно предложение:** Spectral anomaly detection для gold mineral prospecting через Sentinel-2 satellite imagery в Бестобе, Казахстан.
**Статус:** Active (P1 complete, P2 partial)
**Стек:** Python 3.11, numpy/scipy, rasterio, geopandas, IsolationForest, DBSCAN, folium
**Где:** E:\Geosran Gold  2026
**Тесты:** 179 passing

## Главный результат
414+ anomaly zone candidates. Spectral features (NDVI, BSI, Clay, Iron Oxide). Anti-hallucination rules. 5-20% expected true positive rate — честно задокументировано.

## Переиспользуемые компоненты
- SyntheticDetector — guards against synthetic data in production
- Temporal nanmedian compositing на Sentinel-2 tiles

up:: [[Каталог всех проектов 2026]]
