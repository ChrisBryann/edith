import { useState, useEffect, useRef } from 'react'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isDemo, setIsDemo] = useState(false);
  const [status, setStatus] = useState(null);
  const bottomRef = useRef(null);

  const [events, setEvents] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);

  // Initial Checks & Data Fetching
  useEffect(() => {
    fetch(`${API_URL}/system-status`)
      .then(res => res.json())
      .then(data => setStatus(data))
      .catch(err => console.error("API Error", err));

    fetch(`${API_URL}/config-status`)
      .then(res => res.json())
      .then(data => setIsDemo(data.use_mock_data))
      .catch(err => console.error("Config Error", err));

    // Fetch Calendar Events
    fetch(`${API_URL}/calendar-events`)
      .then(res => res.json())
      .then(data => setEvents(data))
      .catch(err => console.error("Events Error", err));
  }, []);

  // Auto-scroll
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Click Outside Handler for Flashcard
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (selectedEvent &&
        !event.target.closest('.event-flashcard') &&
        !event.target.closest('.history-item')) {
        setSelectedEvent(null);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [selectedEvent]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/ask-question`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: userMsg.content }),
      });

      const data = await response.json();

      const aiMsg = {
        role: 'assistant',
        content: data.answer,
        sources: data.sources
      };
      setMessages(prev => [...prev, aiMsg]);

    } catch (error) {
      console.error("Error asking question:", error);
      setMessages(prev => [...prev, { role: 'assistant', content: "Sorry, I couldn't reach the server." }]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatTime = (isoString) => {
    try {
      return new Date(isoString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch (e) { return ""; }
  };

  return (
    <>
      <div className="sidebar">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <img src="/edith_logo.svg" alt="edith" style={{ height: '32px' }} />
          </div>
          {isDemo && <span className="demo-badge">Demo Mode</span>}
        </div>



        <div style={{ flex: 1, overflowY: 'auto' }}>
          <div style={{ padding: '0 0 0.5rem', color: 'var(--text-secondary)', fontSize: '0.75rem', fontWeight: 600 }}>TODAY'S AGENDA</div>

          {events.length === 0 ? (
            <div style={{ fontSize: '0.8rem', color: '#666', fontStyle: 'italic' }}>No events scheduled</div>
          ) : (
            events.map((evt, i) => (
              <div
                key={i}
                className={`history-item ${selectedEvent === evt ? 'selected' : ''}`}
                onClick={() => setSelectedEvent(selectedEvent === evt ? null : evt)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  marginBottom: '12px',
                  cursor: 'pointer',
                  backgroundColor: selectedEvent === evt ? 'var(--bg-secondary)' : 'transparent',
                  borderRadius: '6px',
                  padding: '8px',
                  transition: 'all 0.2s'
                }}
              >
                <div style={{
                  width: '4px', height: '32px', borderRadius: '2px',
                  backgroundColor: evt.account_source === 'work_main' ? '#60a5fa' : '#34d399',
                  flexShrink: 0
                }}></div>
                <div style={{ overflow: 'hidden' }}>
                  <div style={{ fontSize: '0.9rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', fontWeight: 500 }}>
                    {evt.summary}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#888' }}>
                    {formatTime(evt.start)} - {formatTime(evt.end)}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Status Footer */}
        <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '1rem', marginTop: 'auto' }}>
          {status && (
            <div style={{ fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '8px', color: status.is_authenticated ? '#4ade80' : '#f87171' }}>
              <div style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: 'currentColor' }}></div>
              {status.is_authenticated ? 'Online & Synced' : 'Disconnected'}
            </div>
          )}
        </div>
      </div>

      <div className="main-content">
        <div className="chat-container">
          {messages.length === 0 && (
            <div className="welcome-msg">
              <div style={{ width: 64, height: 64, borderRadius: '50%', background: 'var(--bg-input)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1rem', fontSize: '2rem' }}>👋</div>
              <h1>How can I help you today?</h1>
            </div>
          )}

          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role}`}>
              <div className="avatar">
                {msg.role === 'user' ? 'U' : 'E'}
              </div>
              <div className="message-content">
                <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>

                {/* Citations */}
                {msg.sources && msg.sources.length > 0 && (
                  <div className="citation-box">
                    <div className="citation-header">📚 Sources</div>
                    {msg.sources.map((source, i) => (
                      <div key={i} className="citation-item">
                        <div style={{ fontWeight: 'bold', fontSize: '0.9rem' }}>{source.metadata.subject}</div>
                        <div style={{ fontSize: '0.8rem', color: '#888' }}>
                          From: {source.metadata.sender} • {source.metadata.date?.substring(0, 10)}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          <div ref={bottomRef} />
        </div>

        <form className="input-area" onSubmit={sendMessage}>
          <div className="input-box">
            <input
              type="text"
              placeholder="Message edith..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              autoFocus
            />
            <button type="submit" className="btn-send" disabled={isLoading || !input.trim()}>
              {isLoading ? '▪' : '↑'}
            </button>
          </div>
        </form>
      </div>

      {/* Event Details Flashcard (Modeless) */}
      {selectedEvent && (
        <div className="event-flashcard">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '0.8rem' }}>
            <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 600 }}>{selectedEvent.summary}</h3>
            <button
              onClick={() => setSelectedEvent(null)}
              style={{
                background: 'none', border: 'none', fontSize: '1.2rem',
                cursor: 'pointer', color: 'var(--text-secondary)', padding: '0 4px'
              }}>×</button>
          </div>

          <div style={{ marginBottom: '0.8rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
              <span>🕒</span>
              <span style={{ fontWeight: 500 }}>{formatTime(selectedEvent.start)} - {formatTime(selectedEvent.end)}</span>
            </div>
            {selectedEvent.location && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span>📍</span>
                <span>{selectedEvent.location}</span>
              </div>
            )}
          </div>

          <div style={{
            background: 'var(--bg-secondary)',
            padding: '0.8rem',
            borderRadius: '8px',
            fontSize: '0.9rem',
            lineHeight: '1.5',
            border: '1px solid var(--border-color)' /* Subtle border */
          }}>
            {selectedEvent.description || "No additional details provided."}
          </div>
        </div>
      )}
    </>
  )
}

export default App
