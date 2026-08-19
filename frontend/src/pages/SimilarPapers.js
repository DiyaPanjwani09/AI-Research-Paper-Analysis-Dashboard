import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import { FaSearch, FaUpload, FaStar } from 'react-icons/fa';
import { Link } from 'react-router-dom';
import api from '../api';
import { usePaper } from '../context/PaperContext';

const SCORE_COLOR = (s) => {
  if (s >= 0.8) return { color: '#10b981', bg: 'rgba(16,185,129,0.12)', border: 'rgba(16,185,129,0.3)' };
  if (s >= 0.5) return { color: '#f59e0b', bg: 'rgba(245,158,11,0.12)', border: 'rgba(245,158,11,0.3)' };
  return { color: '#ef4444', bg: 'rgba(239,68,68,0.12)', border: 'rgba(239,68,68,0.3)' };
};

function PaperCard({ paper, index }) {
  const sc = SCORE_COLOR(paper.similarity_score);
  const pct = Math.round(paper.similarity_score * 100);
  return (
    <motion.div className="glass-card p-6 group" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: index * 0.07 }}>
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <h3 className="font-heading text-white font-semibold text-base leading-snug mb-2 group-hover:gradient-text transition-all">
            {paper.title || `Research Paper #${paper.paper_id}`}
          </h3>
          <p className="text-dark-400 text-xs mb-2">{paper.authors || ''}</p>
          <p className="text-dark-400 text-sm leading-relaxed line-clamp-3 mb-4">
            {paper.abstract || 'No description available.'}
          </p>
          {paper.reasons?.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {paper.reasons.map((reason, i) => (
                <span key={i} className="text-xs px-2 py-1 rounded-full bg-primary-500/10 text-primary-300 border border-primary-500/20">
                  {reason}
                </span>
              ))}
            </div>
          )}
        </div>
        <div className="flex-shrink-0 w-16 h-16 rounded-2xl flex items-center justify-center text-sm font-bold font-heading" style={{ background: sc.bg, border: `1px solid ${sc.border}`, color: sc.color }}>
          {pct}%
        </div>
      </div>
      <div className="mt-4 flex items-center justify-between">
        <div className="flex items-center gap-1">
          {[...Array(5)].map((_, i) => (
            <FaStar key={i} className={`w-3 h-3 ${i < Math.round(paper.similarity_score * 5) ? 'text-yellow-400' : 'text-dark-700'}`} />
          ))}
          <span className="text-xs text-dark-500 ml-1">similarity</span>
        </div>
        <span className="text-xs text-dark-500">ID: {paper.paper_id?.substring(0, 8)}</span>
      </div>
    </motion.div>
  );
}

export default function SimilarPapers() {
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [topK, setTopK] = useState(5);
  const { paperData } = usePaper();

  const fetchSimilar = async () => {
    if (!paperData) { toast.error('Please upload a paper first'); return; }
    setLoading(true);
    setPapers([]);
    try {
      const res = await api.post('/recommend', {
        paper_text: paperData.full_text || '',
        top_k: topK,
      });
      setPapers(res.data.similar_papers || []);
      setTotal(res.data.total_papers_in_db || 0);
      toast.success(`Found ${res.data.similar_papers?.length || 0} similar papers`);
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Recommendation failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-16">
      <motion.div className="text-center" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="font-heading text-4xl font-bold text-white mb-2">
          Similar <span className="gradient-text">Papers</span>
        </h1>
        <p className="text-dark-400">Semantic similarity search with explanation</p>
      </motion.div>

      <motion.div className="glass-card p-6 flex flex-wrap items-center gap-4" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
        <div className="flex items-center gap-3 flex-1 min-w-[200px]">
          <label className="text-sm text-dark-400 whitespace-nowrap">Results:</label>
          <input type="range" min={3} max={10} value={topK} onChange={e => setTopK(Number(e.target.value))} className="flex-1 accent-violet-500" />
          <span className="text-primary-400 font-semibold w-4 text-center">{topK}</span>
        </div>
        <div className="flex gap-3">
          {!paperData && (
            <Link to="/upload" className="btn-secondary text-sm">
              <FaUpload className="w-3.5 h-3.5" /> Upload Paper
            </Link>
          )}
          <button onClick={fetchSimilar} disabled={loading} className="btn-primary text-sm">
            {loading
              ? <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Searching...</>
              : <><FaSearch className="w-3.5 h-3.5" /> Find Similar</>
            }
          </button>
        </div>
      </motion.div>

      {total > 0 && (
        <p className="text-xs text-dark-500 text-center">
          Searching across {total.toLocaleString()} papers
        </p>
      )}

      {!loading && papers.length === 0 && (
        <motion.div className="text-center py-16 space-y-4" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <div className="w-16 h-16 mx-auto rounded-2xl bg-primary-500/10 border border-primary-500/20 flex items-center justify-center">
            <FaSearch className="w-7 h-7 text-primary-400" />
          </div>
          <p className="text-dark-400">Click "Find Similar" to discover related papers</p>
        </motion.div>
      )}

      <AnimatePresence>
        {papers.length > 0 && (
          <motion.div className="space-y-4" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <p className="text-sm text-dark-400">
              Showing <span className="text-white font-semibold">{papers.length}</span> similar papers
            </p>
            {papers.map((p, i) => <PaperCard key={p.paper_id} paper={p} index={i} />)}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
