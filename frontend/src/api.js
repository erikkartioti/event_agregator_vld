// Весь контакт с бэкендом — здесь. Если JSON у MapController отличается,
// правьте только normalizeEvent() и toPayload().
const BASE = import.meta.env.VITE_API_BASE ?? "";

async function request(path, options) {
  const res = await fetch(BASE + path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`${res.status} ${await res.text().catch(() => "")}`);
  return res.status === 204 ? null : res.json();
}

export function normalizeEvent(e) {
  const loc = e.location ?? e.geoLocation ?? {};
  return {
    id: e.id,
    title: e.title ?? e.name ?? "Без названия",
    description: e.description ?? "",
    start: e.startTime ?? e.start ?? e.dateStart ?? e.date ?? null,
    end: e.endTime ?? e.end ?? e.dateEnd ?? null,
    address: loc.address ?? e.address ?? "",
    lat: Number(loc.latitude ?? loc.lat ?? e.latitude ?? e.lat),
    lon: Number(loc.longitude ?? loc.lon ?? loc.lng ?? e.longitude ?? e.lon),
  };
}

function toPayload(ev) {
  return {
    title: ev.title,
    description: ev.description ?? "",
    startTime: ev.startTime,
    endTime: ev.endTime ?? null,
    location: { latitude: ev.latitude, longitude: ev.longitude, address: ev.address },
  };
}

export async function fetchEvents() {
  const data = await request("/api/events");
  return (Array.isArray(data) ? data : data.content ?? [])
    .map(normalizeEvent)
    .filter((e) => Number.isFinite(e.lat) && Number.isFinite(e.lon));
}

export async function createEvent(draft) {
  return request("/api/events", { method: "POST", body: JSON.stringify(toPayload(draft)) });
}

export async function askAssistant(messages) {
  return request("/api/assistant", { method: "POST", body: JSON.stringify({ messages }) });
}
