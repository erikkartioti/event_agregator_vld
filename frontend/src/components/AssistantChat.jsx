import { useRef, useState, useEffect } from "react";
import { askAssistant, createEvent } from "../api.js";
import { formatWhen } from "./EventList.jsx";

export default function AssistantChat({ onCreated }) {
  const [messages, setMessages] = useState([]); // {role, content}
  const [draft, setDraft] = useState(null);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const bottom = useRef(null);

  useEffect(() => bottom.current?.scrollIntoView({ block: "end" }), [messages, draft]);

  async function send(e) {
    e.preventDefault();
    const text = input.trim();
    if (!text || busy) return;
    const next = [...messages, { role: "user", content: text }];
    setMessages(next);
    setInput("");
    setDraft(null);
    setBusy(true);
    try {
      const res = await askAssistant(next);
      setMessages([...next, { role: "assistant", content: res.reply }]);
      setDraft(res.action?.type === "create_event" ? res.action.event : null);
    } catch (err) {
      setMessages([...next, { role: "assistant", content: `Ассистент недоступен: ${err.message}` }]);
    } finally {
      setBusy(false);
    }
  }

  async function confirm() {
    setBusy(true);
    try {
      const saved = await createEvent(draft);
      setMessages((m) => [...m, { role: "assistant", content: "Событие создано." }]);
      setDraft(null);
      onCreated(saved);
    } catch (err) {
      setMessages((m) => [...m, { role: "assistant", content: `Не удалось сохранить: ${err.message}` }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="chat">
      <div className="chat-log">
        {!messages.length && (
          <p className="hint">
            Напишите, что и где создать. Например: «Создай концерт на проспекте Мира, 12 в субботу в 19:00».
          </p>
        )}
        {messages.map((m, i) => (
          <p key={i} className={`msg ${m.role}`}>{m.content}</p>
        ))}
        {draft && (
          <div className="draft">
            <strong>{draft.title}</strong>
            <span>{formatWhen(draft.startTime)}</span>
            <span>{draft.address}</span>
            <div className="draft-actions">
              <button onClick={confirm} disabled={busy}>Создать событие</button>
              <button className="ghost" onClick={() => setDraft(null)}>Отмена</button>
            </div>
          </div>
        )}
        <div ref={bottom} />
      </div>
      <form onSubmit={send} className="chat-form">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Что создать?"
          aria-label="Сообщение ассистенту"
        />
        <button disabled={busy || !input.trim()}>{busy ? "…" : "Отправить"}</button>
      </form>
    </section>
  );
}
