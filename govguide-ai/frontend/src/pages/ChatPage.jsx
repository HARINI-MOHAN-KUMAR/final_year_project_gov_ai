import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, 
  Sparkles, 
  Bot, 
  User, 
  BookOpen, 
  ExternalLink, 
  HelpCircle,
  RotateCcw
} from 'lucide-react';
import api from '../api/client';
import { useAuthStore } from '../store/authStore';

export default function ChatPage() {
  const { user, language } = useAuthStore();
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: `Namaste! 🙏 I am your GovGuide AI Assistant. I can help you find government schemes, understand eligibility criteria, and explain what documents you need.\n\nHow can I help you today?`,
      sources: [],
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const starterPrompts = [
    'I am a farmer with 2 acres of land in UP. What schemes can I get?',
    'What is the income limit for PM Awas Yojana Gramin?',
    'How do I apply for Ayushman Bharat (PM-JAY) health insurance?',
    'What schemes provide education loans or scholarships for girls?',
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (textToSend) => {
    const text = textToSend || input;
    if (!text.trim() || loading) return;

    const userMsg = { role: 'user', content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await api.post('/chat/message', {
        content: text,
        message: text,
        language: language || 'en',
      });

      const botMsg = {
        role: 'assistant',
        content: res.data.content || res.data.response || res.data.reply || res.data.message || 'I have searched the scheme database for your query.',
        sources: res.data.sources || res.data.referenced_schemes || [],
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an issue connecting to the knowledge engine. Please check that the backend is running.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setMessages([
      {
        role: 'assistant',
        content: `Conversation restarted. Feel free to ask about any central or state government scheme!`,
        sources: [],
      },
    ]);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 h-[calc(100vh-140px)] flex flex-col space-y-4">
      {/* Chat Header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-sm flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-amber-500 p-0.5 flex items-center justify-center">
            <div className="w-full h-full bg-indigo-900 rounded-[10px] flex items-center justify-center text-white">
              <Bot className="w-5 h-5 text-indigo-300" />
            </div>
          </div>
          <div>
            <h1 className="font-bold text-slate-900 text-sm sm:text-base flex items-center space-x-1.5">
              <span>GovGuide Multilingual Scheme AI</span>
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            </h1>
            <p className="text-xs text-slate-500">RAG Grounded in 50+ Welfare Schemes</p>
          </div>
        </div>

        <button
          onClick={handleClear}
          className="p-2 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition-colors"
          title="Reset conversation"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
      </div>

      {/* Message List */}
      <div className="flex-1 overflow-y-auto bg-slate-100/60 rounded-2xl border border-slate-200/80 p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex items-start space-x-2.5 max-w-[85%] ${
              msg.role === 'user' ? 'ml-auto flex-row-reverse space-x-reverse' : ''
            }`}
          >
            {/* Avatar */}
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${
                msg.role === 'user' ? 'bg-indigo-600 text-white' : 'bg-slate-900 text-amber-400'
              }`}
            >
              {msg.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>

            {/* Bubble */}
            <div
              className={`rounded-2xl p-4 text-sm leading-relaxed shadow-xs ${
                msg.role === 'user'
                  ? 'bg-indigo-600 text-white rounded-tr-none'
                  : 'bg-white text-slate-800 border border-slate-200/80 rounded-tl-none'
              }`}
            >
              <div className="whitespace-pre-line">{msg.content}</div>

              {/* Referenced sources */}
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-3 pt-3 border-t border-slate-100">
                  <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-1 flex items-center space-x-1">
                    <BookOpen className="w-3 h-3 text-indigo-500" />
                    <span>Referenced Scheme Catalog:</span>
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {msg.sources.map((s, i) => (
                      <span
                        key={i}
                        className="text-[11px] font-semibold bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded-md border border-indigo-100"
                      >
                        {typeof s === 'string' ? s : s.name || s.id}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-start space-x-2.5 max-w-[85%]">
            <div className="w-8 h-8 rounded-full bg-slate-900 text-amber-400 flex items-center justify-center shrink-0">
              <Bot className="w-4 h-4" />
            </div>
            <div className="bg-white rounded-2xl rounded-tl-none p-4 border border-slate-200 shadow-xs flex items-center space-x-2">
              <span className="w-2 h-2 rounded-full bg-indigo-600 animate-bounce"></span>
              <span className="w-2 h-2 rounded-full bg-indigo-600 animate-bounce [animation-delay:0.2s]"></span>
              <span className="w-2 h-2 rounded-full bg-indigo-600 animate-bounce [animation-delay:0.4s]"></span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Starter Prompts */}
      {messages.length <= 2 && (
        <div className="flex flex-wrap gap-2 text-xs">
          {starterPrompts.map((prompt, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(prompt)}
              className="px-3 py-1.5 rounded-full bg-white border border-slate-300 text-slate-700 hover:border-indigo-400 hover:text-indigo-600 transition-colors shadow-2xs"
            >
              💬 {prompt}
            </button>
          ))}
        </div>
      )}

      {/* Input Box */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="bg-white rounded-2xl border border-slate-200 p-2 shadow-sm flex items-center space-x-2"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about scheme eligibility, documents, or subsidies..."
          className="flex-1 px-3 py-2 text-sm text-slate-800 focus:outline-hidden bg-transparent"
        />
        <button
          type="submit"
          disabled={!input.trim() || loading}
          className="p-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 text-white rounded-xl shadow-xs transition-colors shrink-0"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
}
