const fmt = new Intl.DateTimeFormat("ru-RU", {
  day: "numeric", month: "long", hour: "2-digit", minute: "2-digit",
});

export function formatWhen(iso) {
  if (!iso) return "время не указано";
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? iso : fmt.format(d);
}

export default function EventList({ events, selectedId, onSelect }) {
  if (!events.length) {
    return <p className="empty">Событий по этим условиям нет. Измените фильтр или создайте событие через ассистента.</p>;
  }
  return (
    <ul className="events">
      {events.map((e) => (
        <li key={e.id}>
          <button
            className={e.id === selectedId ? "event active" : "event"}
            onClick={() => onSelect(e.id)}
          >
            <span className="event-title">{e.title}</span>
            <span className="event-meta">{formatWhen(e.start)}</span>
            {e.address && <span className="event-meta">{e.address}</span>}
          </button>
        </li>
      ))}
    </ul>
  );
}
