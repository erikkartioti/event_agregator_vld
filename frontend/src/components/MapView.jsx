import { useEffect, useRef } from "react";
import maplibregl from "maplibre-gl";
import { buildStyle } from "../mapStyle.js";

const CENTER = [44.6678, 43.0241]; // Владикавказ
const SRC = "events";

function toGeoJSON(events) {
  return {
    type: "FeatureCollection",
    features: events.map((e) => ({
      type: "Feature",
      geometry: { type: "Point", coordinates: [e.lon, e.lat] },
      properties: { id: e.id },
    })),
  };
}

export default function MapView({ events, selectedId, onSelect }) {
  const container = useRef(null);
  const mapRef = useRef(null);
  const readyRef = useRef(false);
  const popupRef = useRef(null);
  const eventsRef = useRef(events);
  const onSelectRef = useRef(onSelect);
  eventsRef.current = events;
  onSelectRef.current = onSelect;

  useEffect(() => {
    const map = new maplibregl.Map({
      container: container.current,
      style: buildStyle(),
      center: CENTER,
      zoom: 12.5,
      maxZoom: 19,
    });
    mapRef.current = map;
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "bottom-right");

    map.on("load", () => {
      map.addSource(SRC, {
        type: "geojson",
        data: toGeoJSON(eventsRef.current),
        cluster: true,
        clusterRadius: 48,
        clusterMaxZoom: 15,
      });
      map.addLayer({
        id: "clusters", type: "circle", source: SRC, filter: ["has", "point_count"],
        paint: {
          "circle-color": "#1d6f7a",
          "circle-radius": ["step", ["get", "point_count"], 16, 10, 22, 50, 28],
          "circle-stroke-width": 3, "circle-stroke-color": "#ffffff",
        },
      });
      map.addLayer({
        id: "cluster-count", type: "symbol", source: SRC, filter: ["has", "point_count"],
        layout: {
          "text-field": ["get", "point_count_abbreviated"],
          "text-font": ["Open Sans Semibold"],
          "text-size": 13,
        },
        paint: { "text-color": "#ffffff" },
      });
      map.addLayer({
        id: "event-point", type: "circle", source: SRC, filter: ["!", ["has", "point_count"]],
        paint: {
          "circle-color": ["case", ["==", ["get", "id"], -1], "#1d6f7a", "#e0a100"],
          "circle-radius": 9, "circle-stroke-width": 3, "circle-stroke-color": "#1f2a2e",
        },
      });

      map.on("click", "clusters", async (e) => {
        const f = map.queryRenderedFeatures(e.point, { layers: ["clusters"] })[0];
        const zoom = await map.getSource(SRC).getClusterExpansionZoom(f.properties.cluster_id);
        map.easeTo({ center: f.geometry.coordinates, zoom });
      });
      map.on("click", "event-point", (e) => onSelectRef.current(e.features[0].properties.id));
      ["clusters", "event-point"].forEach((l) => {
        map.on("mouseenter", l, () => (map.getCanvas().style.cursor = "pointer"));
        map.on("mouseleave", l, () => (map.getCanvas().style.cursor = ""));
      });
      readyRef.current = true;
      map.getSource(SRC).setData(toGeoJSON(eventsRef.current));
    });

    return () => { map.remove(); mapRef.current = null; readyRef.current = false; };
  }, []);

  useEffect(() => {
    if (readyRef.current) mapRef.current.getSource(SRC).setData(toGeoJSON(events));
  }, [events]);

  useEffect(() => {
    const map = mapRef.current;
    popupRef.current?.remove();
    if (!map || selectedId == null) return;
    const ev = events.find((e) => e.id === selectedId);
    if (!ev) return;
    map.flyTo({ center: [ev.lon, ev.lat], zoom: Math.max(map.getZoom(), 16), speed: 1.4 });

    // textContent вместо innerHTML — названия приходят из парсеров и от пользователей
    const box = document.createElement("div");
    const h = document.createElement("strong");
    h.textContent = ev.title;
    const p = document.createElement("p");
    p.textContent = ev.address;
    box.append(h, p);
    popupRef.current = new maplibregl.Popup({ offset: 14, closeButton: false })
      .setLngLat([ev.lon, ev.lat]).setDOMContent(box).addTo(map);
  }, [selectedId, events]);

  return <div ref={container} className="map" />;
}
