import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import { FaPaperPlane, FaRobot, FaUser, FaUpload, FaTrash, FaBook } from 'react-icons/fa';
import { Link } from 'react-router-dom';
import api from '../api';
import { usePaper } from '../context/PaperContext';

function TypingIndicator() {
  return (
    <div className="flex items-end gap-3 max-w-[85%]">
      <div className="w-9 h-9 flex-shrink-0 rounded-xl bg-gradient-to-br from-primary-500/20 to-primary-700/20 border border-primary-500/25 flex items-center justify-center">
        <FaRobot className="w-4 h-4 text-primary-400" />
      </div>
      <div className="chat-bubble-ai px-5 py-4">
        <div className="flex items-center gap-1.5">
          <span className="typing-dot" />
          <span className="typing-dot" />
          <span className="typing-dot" />
        </div>
      </div>
    </div>
  );
}

const SUGGESTED = [
  'What is the main contribution of this paper?',
  'What datasets were used?',
  'What are the key findings?',
  'What are the limitations?',
  'Describe the methodology.',
];

const CHAT_MODES = [
  { value: 'researcher', label: 'Researcher', desc: 'Technical details' },
  { value: 'student', label: 'Student', desc: 'Simplified' },
  { value: 'beginner', label: 'Beginner', desc: 'Plain English' },
  { value: 'executive', label: 'Executive', desc: 'High-level' },
];

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [chatMode, setChatMode] = useState('researcher');
  const { paperData } = usePaper();
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (paperData) {
      setMessages([{
        id: 1,
        role: 'ai',
        text: `Hello! I've loaded your paper **"${paperData.metadata?.title || 'Research Paper'}"**. Ask me anything about it!`,
        ts: new Date(),
      }]);
    }
  }, [paperData]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const sendMessage = async (text) => {
    const question = (text || input).trim();
    if (!question) return;

    const userMsg = { id: Date.now(), role: 'user', text: question, ts: new Date() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await api.post('/chat', {
        question,
        paper_text: paperData?.full_text || undefined,
        paper_id: paperData?.file_id || undefined,
        sections: paperData?.sections || undefined,
        title: paperData?.metadata?.title,
        top_k: 8,
        rerank_top_k: 5,
        chat_mode: chatMode,
      });

      const aiMsg = {
        id: Date.now() + 1,
        role: 'ai',
        text: res.data.answer,
        sources: res.data.sources,
        total_time: res.data.total_time,
        ts: new Date(),
      };
      setMessages(prev => [...prev, aiMsg]);
    } catch (e) {
      const errMsg = {
        id: Date.now() + 1,
        role: 'ai',
        text: "Sorry, I couldn't process that. Please try again.",
        ts: new Date(),
      };
      setMessages(prev => [...prev, errMsg]);
      toast.error('Chat request failed');
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const clearChat = () => {
    setMessages(paperData ? [{
      id: 1,
      role: 'ai',
      text: `Chat cleared. I still have your paper loaded. Ask me anything!`,
      ts: new Date(),
    }] : []);
    toast.success('Chat cleared');
  };

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  };

  return (
    <div className="max-w-4xl mx-auto pb-8 flex flex-col" style={{ height: 'calc(100vh - 110px)' }}>
      <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
        <div>
          <h1 className="font-heading text-3xl font-bold text-white">
            Chat with <span className="gradient-text">Paper</span>
          </h1>
          <p className="text-dark-400 text-sm mt-0.5">RAG-powered Q&A with citation-backed answers</p>
        </div>
        <div className="flex gap-2 items-center">
          {messages.length > 1 && (
            <button onClick={clearChat} className="btn-ghost text-xs">
              <FaTrash className="w-3 h-3" /> Clear
            </button>
          )}
        </div>
      </div>

      <div className="mb-3 flex gap-2 flex-wrap">
        {CHAT_MODES.map(mode => (
          <button
            key={mode.value}
            onClick={() => setChatMode(mode.value)}
            className={`text-xs px-3 py-1.5 rounded-full border transition-all ${
              chatMode === mode.value
                ? 'border-primary-500 bg-primary-500/15 text-primary-300'
                : 'border-dark-700 text-dark-400 hover:border-primary-500/30'
            }`}
          >
            {mode.label}
          </button>
        ))}
      </div>

      {!paperData && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mb-4 px-4 py-3 rounded-xl flex items-center gap-3" style={{ background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.25)' }}>
          <FaBook className="w-4 h-4 text-amber-400 flex-shrink-0" />
          <p className="text-amber-300 text-sm">No paper loaded. Upload a paper to get context-aware answers.</p>
        </motion.div>
      )}

      <div className="flex-1 overflow-y-auto glass-card p-5 space-y-4 min-h-0">
        <AnimatePresence initial={false}>
          {messages.map(msg => (
            <motion.div key={msg.id} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }} className={`flex items-end gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
              <div className={`w-9 h-9 flex-shrink-0 rounded-xl flex items-center justify-center ${
                msg.role === 'user' ? 'bg-gradient-to-br from-primary-500 to-primary-700' : 'bg-gradient-to-br from-primary-500/20 to-primary-700/20 border border-primary-500/25'
              }`}>
                {msg.role === 'user' ? <FaUser className="w-4 h-4 text-white" /> : <FaRobot className="w-4 h-4 text-primary-400" />}
              </div>
              <div className={`max-w-[80%] ${msg.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-ai'} px-5 py-3.5`}>
                <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.text}</p>
                {msg.sources?.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-white/10">
                    <p className="text-xs font-semibold opacity-60 mb-1.5">Sources</p>
                    {msg.sources.slice(0, 3).map((s, i) => (
                      <div key={i} className="text-xs opacity-50 mb-1">
                        <span className="text-primary-400">[{i + 1}]</span> {s.section || 'Unknown'} {s.page ? `- Page ${s.page}` : ''} (Score: {(s.score * 100).toFixed(0)}%)
                      </div>
                    ))}
                  </div>
                )}
                {msg.total_time > 0 && (
                  <p className="text-xs text-dark-600 mt-1">Response time: {msg.total_time.toFixed(2)}s</p>
                )}
                <p className={`text-xs mt-2 ${msg.role === 'user' ? 'text-white/40' : 'text-dark-500'}`}>
                  {msg.ts?.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        {loading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>

      {messages.length <= 1 && (
        <div className="my-3 flex gap-2 flex-wrap">
          {SUGGESTED.map((q, i) => (
            <button key={i} onClick={() => sendMessage(q)} className="text-xs px-3 py-1.5 rounded-full border border-primary-500/25 text-primary-300 hover:border-primary-500/50 hover:bg-primary-500/10 transition-all">
              {q}
            </button>
          ))}
        </div>
      )}

      <div className="mt-3 glass-card p-3 flex gap-3 items-end">
        <textarea
          ref={inputRef}
          rows={1}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Ask anything about the paper..."
          className="flex-1 resize-none bg-transparent text-sm text-white placeholder-dark-500 outline-none py-2 px-1 max-h-28 min-h-[36px]"
          style={{ lineHeight: '1.5' }}
          onInput={e => { e.target.style.height = 'auto'; e.target.style.height = e.target.scrollHeight + 'px'; }}
        />
        <motion.button
          onClick={() => sendMessage()}
          disabled={loading || !input.trim()}
          whileTap={{ scale: 0.92 }}
          className="btn-primary p-3 rounded-xl disabled:opacity-40 flex-shrink-0"
        >
          {loading
            ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            : <FaPaperPlane className="w-4 h-4" />
          }
        </motion.button>
      </div>
    </div>
  );
}
