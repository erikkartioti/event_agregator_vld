// Векторный стиль под тайлы из Tippecanoe (см. tiles/build_tiles.sh).
// Имена source-layer совпадают с -L в скрипте: landuse, water, roads, buildings.
export function buildStyle() {
  const tiles = `${window.location.origin}/tiles/vladikavkaz/{z}/{x}/{y}`;
  const road = (id, filter, color, w) => ({
    id,
    type: "line",
    source: "base",
    "source-layer": "roads",
    filter,
    layout: { "line-cap": "round", "line-join": "round" },
    paint: { "line-color": color, "line-width": w },
  });

  return {
    version: 8,
    glyphs: "https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf",
    sources: {
      base: { type: "vector", tiles: [tiles], minzoom: 0, maxzoom: 14 },
    },
    layers: [
      { id: "bg", type: "background", paint: { "background-color": "#eef0eb" } },
      {
        id: "landuse", type: "fill", source: "base", "source-layer": "landuse",
        paint: { "fill-color": "#dfe6d6" },
      },
      {
        id: "water", type: "fill", source: "base", "source-layer": "water",
        paint: { "fill-color": "#b9d4dc" },
      },
      {
        id: "buildings", type: "fill", source: "base", "source-layer": "buildings", minzoom: 14,
        paint: { "fill-color": "#d9d6cc", "fill-outline-color": "#c4c0b3" },
      },
      road("roads-minor", ["match", ["get", "highway"], ["residential", "service", "unclassified", "living_street"], true, false],
        "#ffffff", ["interpolate", ["linear"], ["zoom"], 12, 0.6, 18, 7]),
      road("roads-major", ["match", ["get", "highway"], ["primary", "secondary", "tertiary", "trunk"], true, false],
        "#f2c879", ["interpolate", ["linear"], ["zoom"], 10, 1, 18, 12]),
    ],
  };
}
