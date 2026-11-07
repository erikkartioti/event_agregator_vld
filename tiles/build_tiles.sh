#!/usr/bin/env bash
# OSM-выгрузка -> GeoJSON -> векторные тайлы (Tippecanoe) -> vladikavkaz.mbtiles
# Нужны: osmium-tool, tippecanoe. Выгрузка РСО-Алании: https://download.geofabrik.de/russia/north-caucasus-fed-district.html
set -euo pipefail

PBF="${1:-north-caucasus-fed-district-latest.osm.pbf}"
BBOX="44.45,42.90,44.90,43.15"   # lon_min,lat_min,lon_max,lat_max — Владикавказ с окрестностями
OUT="vladikavkaz.mbtiles"

osmium extract -b "$BBOX" "$PBF" -o city.osm.pbf --overwrite

# Отдельный слой на каждый тип объектов; --geometry-type нужен для osmium export
osmium tags-filter city.osm.pbf w/highway -o roads.osm.pbf --overwrite
osmium tags-filter city.osm.pbf wr/building -o buildings.osm.pbf --overwrite
osmium tags-filter city.osm.pbf wr/natural=water wr/waterway=riverbank w/waterway=river -o water.osm.pbf --overwrite
osmium tags-filter city.osm.pbf wr/landuse wr/leisure=park -o landuse.osm.pbf --overwrite

for l in roads buildings water landuse; do
  osmium export "$l.osm.pbf" -f geojsonseq --geometry-types="$([ $l = roads ] && echo linestring || ([ $l = water ] && echo linestring,polygon || echo polygon))" -o "$l.geojsonseq" --overwrite
done

tippecanoe -o "$OUT" --force \
  -Z0 -z14 \
  --drop-densest-as-needed --extend-zooms-if-still-dropping \
  --coalesce-smallest-as-needed --simplify-only-low-zooms \
  --read-parallel \
  -L roads:roads.geojsonseq \
  -L buildings:buildings.geojsonseq \
  -L water:water.geojsonseq \
  -L landuse:landuse.geojsonseq

echo "Готово: $OUT. Положите в ./tiles-data/ — Martin отдаст по /vladikavkaz/{z}/{x}/{y}"
