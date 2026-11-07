import { useEffect, useMemo, useState } from "react";
import { fetchEvents } from "./api.js";
import MapView from "./components/MapView.jsx";
import EventList from "./components/EventList.jsx";
import AssistantChat from "./components/AssistantChat.jsx";

const PERIODS = { all: "Все", today: "Сегодня", week: "Неделя" };

function inPeriod(e, period) {
  if (period === "all") return true;
  const t = new Date(e.start ?? 0);
  const now = new Date();
  const dayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const to = new Date(dayStart.getTime() + (period === "today" ? 1 : 7) * 864e5);
  return t >= dayStart && t < to;
}

export default function App() {
  const [events, setEvents] = useState([]);
  const [error, setError] = useState(null);
  const [query, setQuery] = useState("");
  const [period, setPeriod] = useState("all");
  const [selectedId, setSelectedId] = useState(null);
  const [tab, setTab] = useState("events");

  const load = () =>
    fetchEvents().then(setEvents).catch((e) => setError(e.message));
  useEffect(() => { load(); }, []);

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    return events.filter(
      (e) => inPeriod(e, period) &&
        (!q || `${e.title} ${e.address} ${e.description}`.toLowerCase().includes(q))
    );
  }, [events, query, period]);

  async function handleCreated(saved) {
    await load();
    if (saved?.id != null) setSelectedId(saved.id);
    setTab("events");
  }

  return (
    <div className="layout">
      <aside className="panel">
        <header>
          <h1>События Владикавказа</h1>
          <div className="tabs" role="tablist">
            <button role="tab" aria-selected={tab === "events"} onClick={() => setTab("events")}>События</button>
            <button role="tab" aria-selected={tab === "assistant"} onClick={() => setTab("assistant")}>Ассистент</button>
          </div>
        </header>

        {tab === "events" ? (
          <>
            <div className="filters">
              <input
                type="search" value={query} placeholder="Название или улица"
                onChange={(e) => setQuery(e.target.value)} aria-label="Поиск"
              />
              <div className="chips">
                {Object.entries(PERIODS).map(([k, label]) => (
                  <button key={k} className={k === period ? "chip on" : "chip"} onClick={() => setPeriod(k)}>
                    {label}
                  </button>
                ))}
              </div>
            </div>
            {error && <p className="error">Не удалось загрузить события: {error}</p>}
            <EventList events={visible} selectedId={selectedId} onSelect={setSelectedId} />
          </>
        ) : (
          <AssistantChat onCreated={handleCreated} />
        )}
      </aside>
      <MapView events={visible} selectedId={selectedId} onSelect={setSelectedId} />
    </div>
  );
}
