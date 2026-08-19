import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import toast from 'react-hot-toast';
import {
  FaFileAlt, FaBrain, FaLightbulb, FaStar,
  FaUpload, FaSearch, FaExclamationTriangle, FaChevronDown
} from 'react-icons/fa';
import api from '../api';
import { usePaper } from '../context/PaperContext';

const BADGE_COLORS = ['badge-violet', 'badge-cyan', 'badge-pink', 'badge-green', 'badge-violet', 'badge-cyan'];

function SectionAccordion({ title, icon: Icon, children, defaultOpen = false, accent = 'violet' }) {
  const [open, setOpen] = useState(defaultOpen);
  const colors = {
    violet: { border: 'rgba(139,92,246,0.35)', icon: 'text-violet-400', bg: 'rgba(139,92,246,0.08)' },
    cyan: { border: 'rgba(6,182,212,0.35)', icon: 'text-cyan-400', bg: 'rgba(6,182,212,0.08)' },
    pink: { border: 'rgba(236,72,153,0.35)', icon: 'text-pink-400', bg: 'rgba(236,72,153,0.08)' },
    green: { border: 'rgba(34,197,94,0.35)', icon: 'text-emerald-400', bg: 'rgba(34,197,94,0.08)' },
  };
  const c = colors[accent] || colors.violet;
  return (
    <div className="rounded-2xl overflow-hidden" style={{ border: `1px solid ${c.border}`, background: c.bg }}>
      <button onClick={() => setOpen(o => !o)} className="w-full flex items-center justify-between px-6 py-5 text-left">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: `${c.border.replace('0.35', '0.2')}` }}>
            <Icon className={`w-4 h-4 ${c.icon}`} />
          </div>
          <h2 className="font-heading text-lg font-semibold text-white">{title}</h2>
        </div>
        <motion.div animate={{ rotate: open ? 180 : 0 }} transition={{ duration: 0.2 }}>
          <FaChevronDown className="w-4 h-4 text-dark-400" />
        </motion.div>
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.3, ease: 'easeInOut' }} className="overflow-hidden">
            <div className="px-6 pb-6 border-t" style={{ borderColor: c.border.replace('0.35', '0.15') }}>
              <div className="pt-4">{children}</div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function Summary() {
  const { paperData } = usePaper();
  const [gaps, setGaps] = useState(null);
  const [gapsLoading, setGapsLoading] = useState(false);

  const detectGaps = async () => {
    if (!paperData?.full_text) {
      toast.error('No paper text available');
      return;
    }
    setGapsLoading(true);
    try {
      const res = await api.post('/gaps', { paper_text: paperData.full_text });
      setGaps(res.data);
      toast.success('Research gaps detected!');
    } catch (e) {
      toast.error('Gap detection failed');
    } finally {
      setGapsLoading(false);
    }
  };

  if (!paperData) {
    return (
      <div className="max-w-4xl mx-auto text-center py-24 space-y-6">
        <div className="w-20 h-20 mx-auto rounded-2xl bg-primary-500/10 border border-primary-500/25 flex items-center justify-center">
          <FaFileAlt className="w-9 h-9 text-primary-400" />
        </div>
        <h1 className="font-heading text-3xl font-bold text-white">No Analysis Found</h1>
        <p className="text-dark-400 max-w-sm mx-auto">Upload a research paper first to view its AI-generated summary.</p>
        <Link to="/upload" className="btn-primary inline-flex mt-2">
          <FaUpload className="w-4 h-4" /> Upload Paper
        </Link>
      </div>
    );
  }

  const metadata = paperData.metadata || {};
  const summaries = paperData.summaries || {};

  return (
    <motion.div className="max-w-5xl mx-auto space-y-6 pb-16" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.4 }}>
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="font-heading text-4xl font-bold text-white">
            Paper <span className="gradient-text">Analysis</span>
          </h1>
          <p className="text-dark-400 mt-1">AI-generated insights from your research paper</p>
        </div>
        <div className="flex gap-3">
          <button onClick={detectGaps} disabled={gapsLoading} className="btn-secondary">
            {gapsLoading
              ? <><div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" /> Detecting...</>
              : <><FaSearch className="w-3.5 h-3.5" /> Detect Gaps</>
            }
          </button>
          <Link to="/chat" className="btn-primary">
            <FaBrain className="w-3.5 h-3.5" /> Chat with Paper
          </Link>
        </div>
      </div>

      <div className="glass-card p-6">
        <h2 className="font-heading text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <FaFileAlt className="w-4 h-4 text-primary-400" /> Paper Information
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div>
            <p className="text-xs text-dark-500 uppercase tracking-wide mb-1">Title</p>
            <p className="text-white font-medium leading-snug">{metadata.title || 'Unknown Title'}</p>
          </div>
          <div>
            <p className="text-xs text-dark-500 uppercase tracking-wide mb-1">Authors</p>
            <p className="text-dark-300 text-sm">{metadata.authors?.join(', ') || 'Unknown'}</p>
          </div>
          {metadata.year && (
            <div>
              <p className="text-xs text-dark-500 uppercase tracking-wide mb-1">Year</p>
              <p className="text-dark-300 text-sm">{metadata.year}</p>
            </div>
          )}
          {metadata.venue && (
            <div>
              <p className="text-xs text-dark-500 uppercase tracking-wide mb-1">Venue</p>
              <p className="text-dark-300 text-sm">{metadata.venue}</p>
            </div>
          )}
          {metadata.keywords?.length > 0 && (
            <div className="md:col-span-2">
              <p className="text-xs text-dark-500 uppercase tracking-wide mb-2">Keywords</p>
              <div className="flex flex-wrap gap-2">
                {metadata.keywords.map((kw, i) => (
                  <span key={i} className={`badge ${BADGE_COLORS[i % BADGE_COLORS.length]}`}>{kw}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      <SectionAccordion title="Executive Summary" icon={FaBrain} defaultOpen accent="violet">
        <div className="text-dark-300 leading-relaxed prose prose-invert max-w-none">
          <ReactMarkdown>{summaries.executive_summary || ''}</ReactMarkdown>
        </div>
      </SectionAccordion>

      {summaries.key_findings?.length > 0 && (
        <SectionAccordion title="Key Findings" icon={FaLightbulb} defaultOpen accent="cyan">
          <ul className="space-y-3">
            {summaries.key_findings.map((f, i) => (
              <li key={i} className="flex items-start gap-3">
                <span className="w-6 h-6 rounded-full bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center flex-shrink-0 mt-0.5 text-xs font-bold text-cyan-400">{i + 1}</span>
                <div className="text-dark-300 text-sm leading-relaxed">
                  <ReactMarkdown>{f}</ReactMarkdown>
                </div>
              </li>
            ))}
          </ul>
        </SectionAccordion>
      )}

      {summaries.key_contributions?.length > 0 && (
        <SectionAccordion title="Key Contributions" icon={FaStar} accent="pink">
          <ul className="space-y-3">
            {summaries.key_contributions.map((c, i) => (
              <li key={i} className="flex items-start gap-3">
                <FaStar className="w-3.5 h-3.5 text-pink-400 flex-shrink-0 mt-1" />
                <div className="text-dark-300 text-sm leading-relaxed">
                  <ReactMarkdown>{c}</ReactMarkdown>
                </div>
              </li>
            ))}
          </ul>
        </SectionAccordion>
      )}

      {Object.keys(summaries.section_summaries || {}).length > 0 && (
        <SectionAccordion title="Section Summaries" icon={FaFileAlt} accent="green">
          <div className="space-y-5">
            {Object.entries(summaries.section_summaries).map(([sec, text]) => (
              <div key={sec} className="border-l-2 border-emerald-500/40 pl-4">
                <h3 className="text-sm font-semibold text-emerald-300 capitalize mb-1">{sec.replace(/_/g, ' ')}</h3>
                <div className="text-dark-400 text-sm leading-relaxed">
                  <ReactMarkdown>{text}</ReactMarkdown>
                </div>
              </div>
            ))}
          </div>
        </SectionAccordion>
      )}

      <AnimatePresence>
        {gaps && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
            <SectionAccordion title="Research Gaps & Future Directions" icon={FaExclamationTriangle} defaultOpen accent="pink">
              <div className="space-y-4">
                {gaps.gaps?.length > 0 ? gaps.gaps.map((gap, i) => (
                  <div key={i} className="rounded-xl p-4" style={{
                    background: gap.severity === 'High' ? 'rgba(239,68,68,0.08)' : gap.severity === 'Medium' ? 'rgba(245,158,11,0.08)' : 'rgba(139,92,246,0.08)',
                    border: `1px solid ${gap.severity === 'High' ? 'rgba(239,68,68,0.25)' : gap.severity === 'Medium' ? 'rgba(245,158,11,0.25)' : 'rgba(139,92,246,0.25)'}`,
                  }}>
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`text-xs font-bold uppercase tracking-wide ${
                        gap.severity === 'High' ? 'text-rose-400' : gap.severity === 'Medium' ? 'text-amber-400' : 'text-violet-400'
                      }`}>{gap.severity || 'Medium'}</span>
                      <span className="text-xs text-dark-500">{gap.category}</span>
                      <span className="text-xs text-dark-600 ml-auto">Confidence: {Math.round((gap.confidence || 0.5) * 100)}%</span>
                    </div>
                    <p className="text-sm text-dark-300 leading-relaxed">{gap.gap}</p>
                    <p className="text-xs text-dark-500 mt-2 italic">Type: {gap.type?.replace(/_/g, ' ')}</p>
                  </div>
                )) : (
                  <p className="text-dark-400 text-sm">No research gaps detected.</p>
                )}
              </div>
            </SectionAccordion>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
