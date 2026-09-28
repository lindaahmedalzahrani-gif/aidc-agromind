import { useEffect, useRef, useState } from 'react';
import { useLanguage } from '../../i18n/LanguageContext';
import { sendChatMessage } from '../../services/chatService';
import type { ChatMessage, DiagnosisContext } from '../../types';
import './ChatPanel.css';

interface ChatPanelProps {
  context: DiagnosisContext | null;
}

function makeId() {
  return Math.random().toString(36).slice(2, 10);
}

export function ChatPanel({ context }: ChatPanelProps) {
  const { t, language } = useLanguage();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isSending, setIsSending] = useState(false);
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages, isSending]);

  const submit = async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || isSending) return;

    const userMessage: ChatMessage = { id: makeId(), role: 'user', text: trimmed };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsSending(true);

    try {
      const { reply, isMock } = await sendChatMessage({ message: trimmed, language, context });
      setMessages((prev) => [...prev, { id: makeId(), role: 'assistant', text: reply, isMock }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: makeId(),
          role: 'assistant',
          text: t.diagnose.errorBody,
          isMock: false,
        },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <section id="chat" className="section chat">
      <div className="container chat__inner">
        <h2 className="chat__heading">{t.chat.heading}</h2>
        <p className="chat__lead">{t.chat.lead}</p>

        {context && (context.crop || context.disease) && (
          <div className="chat__context">
            <span>{t.chat.contextLabel}</span>
            <strong>
              {[context.crop, context.disease].filter(Boolean).join(' · ')}
            </strong>
          </div>
        )}

        <div className="chat__panel">
          <div className="chat__list" ref={listRef}>
            {messages.length === 0 && <p className="chat__empty">{t.chat.emptyState}</p>}
            {messages.map((m) => (
              <div key={m.id} className={`chat__bubble chat__bubble--${m.role}`}>
                <p>{m.text}</p>
                {m.isMock && <span className="chat__mock-tag">{t.chat.mockNotice}</span>}
              </div>
            ))}
            {isSending && (
              <div className="chat__bubble chat__bubble--assistant chat__bubble--pending">
                <span className="chat__dot" />
                <span className="chat__dot" />
                <span className="chat__dot" />
              </div>
            )}
          </div>

          <div className="chat__suggestions">
            {t.chat.suggestions.map((s) => (
              <button key={s} type="button" onClick={() => submit(s)} disabled={isSending}>
                {s}
              </button>
            ))}
          </div>

          <form
            className="chat__form"
            onSubmit={(e) => {
              e.preventDefault();
              submit(input);
            }}
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={t.chat.placeholder}
              aria-label={t.chat.placeholder}
            />
            <button type="submit" disabled={isSending || !input.trim()}>
              {t.chat.send}
            </button>
          </form>
        </div>
      </div>
    </section>
  );
}
