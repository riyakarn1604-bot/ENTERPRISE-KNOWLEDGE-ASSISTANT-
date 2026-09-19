import React, { useState, useRef, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Send, Bot, User, BookOpen, FileText, Zap, Sparkles } from 'lucide-react';
import './index.css';

const API_URL = 'http://localhost:8000/ask';

const SUGGESTION_CHIPS = [
  { icon: '📋', label: 'Annual leave policy' },
  { icon: '🏠', label: 'Remote work rules' },
  { icon: '💻', label: 'IT security guidelines' },
  { icon: '📦', label: 'EchoSound product setup' },
  { icon: '🤝', label: 'Code of conduct' },
  { icon: '🌡️', label: 'SmartThermo manual' },
];

function formatTime(date) {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function SourceItem({ src }) {
  const score = Math.round(Math.max(0, Math.min(100, ((2.0 - src.distance) / 2.0) * 100)));
  const scoreColor = score >= 80 ? '#10b981' : score >= 60 ? '#22d3ee' : '#f59e0b';

  return (
    <li className="source-item">
      <div className="source-left">
        <div className="source-doc-icon">
          <FileText size={11} />
        </div>
        <span className="source-name">{src.source}</span>
      </div>
      <div className="source-score">
        <div className="score-bar-track">
          <div
            className="score-bar-fill"
            style={{ width: `${score}%`, background: `linear-gradient(90deg, #6366f1, ${scoreColor})` }}
          />
        </div>
        <span className="score-label" style={{ color: scoreColor }}>{score}%</span>
      </div>
    </li>
  );
}

function MessageBubble({ msg }) {
  const isAssistant = msg.role === 'assistant';
  return (
    <div className={`message-wrapper ${msg.role}`}>
      <div className="avatar">
        {isAssistant ? <Bot size={18} /> : <User size={18} />}
      </div>
      <div className="message-body">
        <div className="message-label">
          {isAssistant ? 'Nexus AI' : 'You'}
        </div>
        <div className={`message-content ${msg.error ? 'error' : ''}`}>
          <p className="text">{msg.content}</p>
          {msg.sources && msg.sources.length > 0 && (
            <div className="sources-container">
              <div className="sources-header">
                <BookOpen size={11} />
                Knowledge Sources
              </div>
              <ul className="sources-list">
                {msg.sources.map((src, idx) => (
                  <SourceItem key={idx} src={src} />
                ))}
              </ul>
            </div>
          )}
        </div>
        {msg.timestamp && (
          <div className="message-meta">
            {isAssistant && <Zap size={10} />}
            {formatTime(msg.timestamp)}
          </div>
        )}
      </div>
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="message-wrapper assistant">
      <div className="avatar">
        <Bot size={18} />
      </div>
      <div className="message-body">
        <div className="message-label">Nexus AI</div>
        <div className="message-content">
          <div className="typing-indicator">
            <div className="typing-dots">
              <div className="typing-dot" />
              <div className="typing-dot" />
              <div className="typing-dot" />
            </div>
            <span>Searching knowledge base…</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function WelcomeScreen({ onChipClick }) {
  return (
    <div className="welcome-screen">
      <div className="welcome-orb">
        <Sparkles size={38} />
      </div>
      <div className="welcome-text">
        <h2>How can I help you today?</h2>
        <p>
          Ask me anything about HR policies, IT guidelines,
          or product documentation. I retrieve answers directly from your
          company's knowledge base.
        </p>
      </div>
      <div className="welcome-chips">
        {SUGGESTION_CHIPS.map((chip, idx) => (
          <button
            key={idx}
            id={`chip-${idx}`}
            className="chip"
            onClick={() => onChipClick(chip.label)}
          >
            <span className="chip-icon">{chip.icon}</span>
            {chip.label}
          </button>
        ))}
      </div>
    </div>
  );
}

function App() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading, scrollToBottom]);

  const handleSubmit = useCallback(async (queryText) => {
    const text = (queryText || query).trim();
    if (!text || loading) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: text,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setQuery('');
    setLoading(true);

    try {
      const response = await axios.post(API_URL, { query: text });
      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.data.answer,
        sources: response.data.sources,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error fetching answer:', error);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'assistant',
          content:
            'I encountered an error while searching the knowledge base. Please make sure the backend server is running at localhost:8000.',
          sources: [],
          error: true,
          timestamp: new Date(),
        },
      ]);
    } finally {
      setLoading(false);
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [query, loading]);

  const handleFormSubmit = (e) => {
    e.preventDefault();
    handleSubmit();
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleChipClick = (chipText) => {
    setQuery(chipText);
    handleSubmit(chipText);
  };

  const showWelcome = messages.length === 0 && !loading;

  return (
    <div className="app-container">
      {/* Header */}
      <header className="header">
        <div className="header-brand">
          <div className="header-logo">
            <Bot size={20} />
          </div>
          <div className="header-title-group">
            <span className="header-title">Nexus AI</span>
            <span className="header-subtitle">Enterprise Knowledge Assistant</span>
          </div>
        </div>
        <div className="header-status" id="status-indicator">
          <div className="status-dot" />
          RAG Engine Online
        </div>
      </header>

      {/* Chat */}
      <main className="chat-container" id="chat-main">
        <div className="messages-list">
          {showWelcome && <WelcomeScreen onChipClick={handleChipClick} />}
          {messages.map((msg) => (
            <MessageBubble key={msg.id} msg={msg} />
          ))}
          {loading && <TypingIndicator />}
          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* Input */}
      <footer className="input-area">
        <form onSubmit={handleFormSubmit} className="input-form" id="chat-form">
          <div className="input-wrapper">
            <textarea
              ref={inputRef}
              id="chat-input"
              className="text-input"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about leave policies, IT security, product manuals…"
              disabled={loading}
              rows={1}
            />
            <div className="input-hint">
              Press <kbd className="kbd">Enter</kbd> to send &nbsp;·&nbsp; <kbd className="kbd">Shift+Enter</kbd> for new line
            </div>
          </div>
          <button
            type="submit"
            id="send-button"
            className="send-btn"
            disabled={!query.trim() || loading}
            aria-label="Send message"
          >
            <Send size={20} />
          </button>
        </form>
        <p className="footer-note">
          Answers are grounded in company documents via FAISS vector retrieval · Hallucination-resistant RAG pipeline
        </p>
      </footer>
    </div>
  );
}

export default App;
