import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  BarChart, Bar, LineChart, Line, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts';
import { FaChartLine, FaChartBar, FaChartPie, FaFire, FaSyncAlt, FaSearch } from 'react-icons/fa';
import api from '../api';

const VIOLET_PALETTE = ['#8b5cf6', '#6366f1', '#06b6d4', '#ec4899', '#f59e0b', '#10b981', '#ef4444', '#3b82f6', '#a855f7', '#14b8a6'];

function GlassTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: 'rgba(13,13,36,0.95)', border: '1px solid rgba(139,92,246,0.3)', borderRadius: 10, padding: '10px 14px', backdropFilter: 'blur(12px)' }}>
      {label && <p className="text-xs text-dark-400 mb-1">{label}</p>}
      {payload.map((p, i) => (
        <p key={i} className="text-sm font-semibold" style={{ color: p.color || '#8b5cf6' }}>
          {typeof p.value === 'number' ? p.value.toLocaleString() : p.value}
        </p>
      ))}
    </div>
  );
}

function StatCard({ icon: Icon, label, value, sub, accent = '#8b5cf6' }) {
  return (
    <motion.div className="glass-card p-5 stat-card overflow-hidden" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs text-dark-500 uppercase tracking-wide mb-2">{label}</p>
          <p className="text-3xl font-heading font-bold text-white">{value}</p>
          {sub && <p className="text-xs text-dark-400 mt-1">{sub}</p>}
        </div>
        <div className="w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: `${accent}22` }}>
          <Icon className="w-5 h-5" style={{ color: accent }} />
        </div>
      </div>
    </motion.div>
  );
}

function ChartSection({ title, icon: Icon, children, delay = 0 }) {
  return (
    <motion.div className="glass-card p-6" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay }}>
      <div className="flex items-center gap-3 mb-6">
        <div className="w-9 h-9 rounded-xl bg-primary-500/15 border border-primary-500/25 flex items-center justify-center">
          <Icon className="w-4 h-4 text-primary-400" />
        </div>
        <h2 className="font-heading text-lg font-semibold text-white">{title}</h2>
      </div>
      {children}
    </motion.div>
  );
}

export default function Analytics() {
  const [trends, setTrends] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [searching, setSearching] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    setError('');
    try {
      const [trendsRes, statsRes] = await Promise.all([
        api.post('/analytics/trends', { time_period: 'monthly', papers: [] }),
        api.get('/analytics/stats').catch(() => ({ data: null })),
      ]);
      setTrends(trendsRes.data);
      setStats(statsRes.data);
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setSearching(true);
    try {
      const res = await api.post(`/search?query=${encodeURIComponent(searchQuery)}&top_k=5`);
      setSearchResults(res.data);
    } catch (e) {
      toast.error('Search failed');
    } finally {
      setSearching(false);
    }
  };

  const topicData = trends
    ? Object.entries(trends.topic_frequency).sort(([, a], [, b]) => b - a).map(([name, value]) => ({ name: name.replace(' ', '\n'), value, fullName: name }))
    : [];

  const growthData = trends
    ? Object.entries(trends.research_growth).sort(([a], [b]) => a.localeCompare(b)).map(([year, papers]) => ({ year: String(year).slice(0, 4), papers }))
    : [];

  const pieData = trends
    ? trends.top_categories.slice(0, 8).map((cat, i) => ({ name: cat, value: Math.max(20, 100 - i * 11) }))
    : [];

  if (loading) return (
    <div className="flex flex-col items-center justify-center py-32 space-y-4">
      <div className="spinner" />
      <p className="text-dark-400 text-sm animate-pulse">Loading analytics...</p>
    </div>
  );

  if (error) return (
    <div className="max-w-md mx-auto text-center py-24 space-y-4">
      <div className="glass-card p-8">
        <p className="text-rose-400 mb-4 text-sm">{error}</p>
        <button onClick={fetchData} className="btn-primary"><FaSyncAlt className="w-4 h-4" /> Retry</button>
      </div>
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-16">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="font-heading text-4xl font-bold text-white">
            Research <span className="gradient-text">Analytics</span>
          </h1>
          <p className="text-dark-400 mt-1">Trends and insights from research papers</p>
        </div>
        <button onClick={fetchData} className="btn-ghost text-sm"><FaSyncAlt className="w-3.5 h-3.5" /> Refresh</button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        <StatCard icon={FaChartBar} label="Papers Analysed" value={(stats?.total_papers_analyzed || 0).toLocaleString()} accent="#8b5cf6" />
        <StatCard icon={FaFire} label="Research Topics" value={stats?.top_topics || 0} accent="#6366f1" />
        <StatCard icon={FaChartLine} label="Categories" value={stats?.top_categories || 0} accent="#06b6d4" />
        <StatCard icon={FaChartPie} label="Avg Year" value={stats?.average_year || 'N/A'} accent="#ec4899" />
      </div>

      <div className="glass-card p-4">
        <div className="flex gap-3">
          <div className="flex-1 flex items-center gap-2 px-4 py-2 rounded-xl bg-dark-800 border border-dark-600">
            <FaSearch className="w-4 h-4 text-dark-400" />
            <input
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSearch()}
              placeholder="Semantic search across papers..."
              className="flex-1 bg-transparent text-sm text-white placeholder-dark-500 outline-none"
            />
          </div>
          <button onClick={handleSearch} disabled={searching} className="btn-primary text-sm">
            {searching ? 'Searching...' : 'Search'}
          </button>
        </div>
      </div>

      {searchResults && (
        <div className="glass-card p-6 space-y-3">
          <h3 className="font-heading text-lg font-semibold text-white">Search Results</h3>
          {searchResults.results?.length > 0 ? searchResults.results.map((r, i) => (
            <div key={i} className="p-3 rounded-lg bg-dark-800 border border-dark-700">
              <p className="text-sm text-white font-medium">{r.section || 'Unknown Section'}</p>
              <p className="text-xs text-dark-400 mt-1 line-clamp-2">{r.content?.substring(0, 200)}...</p>
              <p className="text-xs text-dark-500 mt-1">Score: {(r.score * 100).toFixed(0)}% {r.page ? `- Page ${r.page}` : ''}</p>
            </div>
          )) : <p className="text-dark-400 text-sm">No results found.</p>}
        </div>
      )}

      <ChartSection title="Topic Frequency Analysis" icon={FaChartBar} delay={0.1}>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={topicData} margin={{ top: 5, right: 20, left: 0, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="name" tick={{ fill: '#64748b', fontSize: 11 }} angle={-20} textAnchor="end" height={50} interval={0} />
            <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
            <Tooltip content={<GlassTooltip />} />
            <Bar dataKey="value" radius={[6, 6, 0, 0]}>
              {topicData.map((_, i) => <Cell key={i} fill={VIOLET_PALETTE[i % VIOLET_PALETTE.length]} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </ChartSection>

      {growthData.length > 0 && (
        <ChartSection title="Research Growth Over Time" icon={FaChartLine} delay={0.2}>
          <ResponsiveContainer width="100%" height={260}>
            <AreaChart data={growthData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
              <defs>
                <linearGradient id="growthGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#8b5cf6" stopOpacity={0.5} />
                  <stop offset="100%" stopColor="#8b5cf6" stopOpacity={0.03} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="year" tick={{ fill: '#64748b', fontSize: 12 }} />
              <YAxis tick={{ fill: '#64748b', fontSize: 12 }} />
              <Tooltip content={<GlassTooltip />} />
              <Area type="monotone" dataKey="papers" stroke="#8b5cf6" strokeWidth={2.5} fill="url(#growthGrad)" dot={{ r: 4, fill: '#8b5cf6', strokeWidth: 0 }} activeDot={{ r: 6 }} />
            </AreaChart>
          </ResponsiveContainer>
        </ChartSection>
      )}

      {trends?.emerging_topics?.length > 0 && (
        <ChartSection title="Emerging Research Topics" icon={FaFire} delay={0.3}>
          <div className="space-y-3">
            {trends.emerging_topics.map((topic, i) => {
              const pct = Math.max(25, 100 - i * 11);
              return (
                <div key={i} className="flex items-center gap-3">
                  <span className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0" style={{ background: `${VIOLET_PALETTE[i % VIOLET_PALETTE.length]}22`, color: VIOLET_PALETTE[i % VIOLET_PALETTE.length] }}>{i + 1}</span>
                  <div className="flex-1">
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-dark-200 capitalize">{topic.replace(/-/g, ' ')}</span>
                      <span className="text-dark-500 text-xs">{pct}%</span>
                    </div>
                    <div className="progress-bar">
                      <motion.div className="progress-fill" style={{ width: 0, background: VIOLET_PALETTE[i % VIOLET_PALETTE.length] }} animate={{ width: `${pct}%` }} transition={{ duration: 0.8, delay: 0.3 + i * 0.08 }} />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </ChartSection>
      )}

      {trends?.publication_trends?.publications?.length > 0 && (
        <ChartSection title="Publication Trends by Year" icon={FaChartLine} delay={0.4}>
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={trends.publication_trends.years.map((y, i) => ({ year: String(y), publications: trends.publication_trends.publications[i] }))} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="year" tick={{ fill: '#64748b', fontSize: 12 }} />
              <YAxis tick={{ fill: '#64748b', fontSize: 12 }} />
              <Tooltip content={<GlassTooltip />} />
              <Line type="monotone" dataKey="publications" stroke="#06b6d4" strokeWidth={2.5} dot={{ r: 4, fill: '#06b6d4' }} activeDot={{ r: 6 }} />
            </LineChart>
          </ResponsiveContainer>
        </ChartSection>
      )}
    </div>
  );
}
