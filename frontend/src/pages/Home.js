import React, { useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  FaUpload, FaChartLine, FaBrain, FaComments,
  FaSearch, FaFileAlt, FaArrowRight, FaStar
} from 'react-icons/fa';

/* ──────────────────────────── Particle Canvas ────────────────────────────── */
function ParticleCanvas() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animId;
    let w, h;

    const resize = () => {
      w = canvas.width  = canvas.offsetWidth;
      h = canvas.height = canvas.offsetHeight;
    };
    resize();
    window.addEventListener('resize', resize);

    const PARTICLE_COUNT = 90;
    const particles = Array.from({ length: PARTICLE_COUNT }, () => ({
      x: Math.random() * w,
      y: Math.random() * h,
      r: Math.random() * 1.5 + 0.3,
      dx: (Math.random() - 0.5) * 0.25,
      dy: (Math.random() - 0.5) * 0.25,
      opacity: Math.random() * 0.6 + 0.2,
    }));

    function draw() {
      ctx.clearRect(0, 0, w, h);
      particles.forEach(p => {
        p.x = (p.x + p.dx + w) % w;
        p.y = (p.y + p.dy + h) % h;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(139,92,246,${p.opacity})`;
        ctx.fill();
      });
      // draw connecting lines
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const a = particles[i], b = particles[j];
          const dist = Math.hypot(a.x - b.x, a.y - b.y);
          if (dist < 100) {
            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            ctx.strokeStyle = `rgba(139,92,246,${0.08 * (1 - dist / 100)})`;
            ctx.lineWidth = 0.5;
            ctx.stroke();
          }
        }
      }
      animId = requestAnimationFrame(draw);
    }
    draw();
    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', resize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 w-full h-full pointer-events-none"
      aria-hidden="true"
    />
  );
}

/* ──────────────────────────── Animated Counter ──────────────────────────── */
function AnimatedStat({ value, label, suffix = '' }) {
  const ref = useRef(null);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const num = parseFloat(value.replace(/[^\d.]/g, ''));
    const duration = 1800;
    const start = performance.now();
    const frame = ts => {
      const progress = Math.min((ts - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = (value.includes('K')
        ? (eased * num / 1000).toFixed(0) + 'K+'
        : value.includes('%')
        ? (eased * num).toFixed(1) + '%'
        : Math.round(eased * num) + (suffix || ''));
      if (progress < 1) requestAnimationFrame(frame);
    };
    const obs = new IntersectionObserver(([e]) => {
      if (e.isIntersecting) { requestAnimationFrame(frame); obs.disconnect(); }
    }, { threshold: 0.5 });
    obs.observe(el);
    return () => obs.disconnect();
  }, [value, suffix]);

  return (
    <div className="glass-card p-6 text-center stat-card group">
      <div
        ref={ref}
        className="text-3xl font-heading font-bold gradient-text mb-2"
      >
        {value}
      </div>
      <div className="text-sm text-dark-400 font-medium">{label}</div>
    </div>
  );
}

/* ──────────────────────────── Feature Card ──────────────────────────────── */
const features = [
  {
    Icon: FaUpload,
    title: 'Smart PDF Upload',
    desc: 'Upload research papers and extract structured content automatically with AI-driven parsing.',
    to: '/upload',
    color: 'violet',
    gradient: 'from-violet-500 to-purple-600',
    bg: 'rgba(139,92,246,0.12)',
    border: 'rgba(139,92,246,0.3)',
  },
  {
    Icon: FaBrain,
    title: 'AI Summarization',
    desc: 'Generate executive summaries, section-wise breakdowns, and key findings in seconds.',
    to: '/summary',
    color: 'indigo',
    gradient: 'from-indigo-500 to-blue-600',
    bg: 'rgba(99,102,241,0.12)',
    border: 'rgba(99,102,241,0.3)',
  },
  {
    Icon: FaSearch,
    title: 'Similar Papers',
    desc: 'Discover related research using FAISS vector similarity search across thousands of papers.',
    to: '/similar',
    color: 'cyan',
    gradient: 'from-cyan-500 to-teal-600',
    bg: 'rgba(6,182,212,0.12)',
    border: 'rgba(6,182,212,0.3)',
  },
  {
    Icon: FaComments,
    title: 'RAG Chatbot',
    desc: 'Have intelligent conversations with your paper using retrieval-augmented generation.',
    to: '/chat',
    color: 'pink',
    gradient: 'from-pink-500 to-rose-600',
    bg: 'rgba(236,72,153,0.12)',
    border: 'rgba(236,72,153,0.3)',
  },
  {
    Icon: FaChartLine,
    title: 'Trend Analytics',
    desc: 'Explore emerging research trends and topic frequencies from curated arXiv data.',
    to: '/analytics',
    color: 'amber',
    gradient: 'from-amber-500 to-orange-600',
    bg: 'rgba(245,158,11,0.12)',
    border: 'rgba(245,158,11,0.3)',
  },
  {
    Icon: FaFileAlt,
    title: 'Research Gaps',
    desc: 'Auto-detect limitations, open problems, and future research directions from any paper.',
    to: '/upload',
    color: 'green',
    gradient: 'from-emerald-500 to-green-600',
    bg: 'rgba(16,185,129,0.12)',
    border: 'rgba(16,185,129,0.3)',
  },
];

const containerVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.1 } },
};
const cardVariants = {
  hidden:  { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: 'easeOut' } },
};

export default function Home() {
  return (
    <div className="max-w-7xl mx-auto space-y-24 pb-20">
      {/* ── Hero ── */}
      <section className="relative min-h-[70vh] flex items-center justify-center overflow-hidden rounded-3xl">
        {/* Particle background */}
        <div
          className="absolute inset-0 rounded-3xl"
          style={{
            background: 'radial-gradient(ellipse 80% 60% at 50% 50%, rgba(139,92,246,0.15) 0%, transparent 70%)',
          }}
        />
        <ParticleCanvas />

        {/* Glow orbs */}
        <div className="absolute top-10 left-10 w-72 h-72 rounded-full blur-3xl pointer-events-none"
          style={{ background: 'rgba(139,92,246,0.08)' }} />
        <div className="absolute bottom-10 right-10 w-64 h-64 rounded-full blur-3xl pointer-events-none"
          style={{ background: 'rgba(6,182,212,0.06)' }} />

        <motion.div
          className="relative z-10 text-center px-4 py-16 max-w-4xl mx-auto"
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        >
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2, duration: 0.5 }}
            className="inline-flex items-center gap-2 mb-6"
          >
            <span className="badge badge-violet flex items-center gap-1.5">
              <FaStar className="w-3 h-3 text-yellow-400" />
              AI-Powered Research Intelligence
            </span>
          </motion.div>

          {/* Headline */}
          <h1 className="font-heading text-5xl md:text-7xl font-bold leading-tight mb-6">
            <span className="text-white">Unlock Insights From</span>
            <br />
            <span className="gradient-text">Research Papers</span>
          </h1>

          <p className="text-dark-400 text-lg md:text-xl max-w-2xl mx-auto leading-relaxed mb-10">
            Upload any PDF — get instant AI summaries, similar paper recommendations,
            trend analytics, and an intelligent chatbot powered by RAG.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/upload" className="btn-primary text-base px-8 py-3.5 rounded-xl group">
              <FaUpload className="w-4 h-4" />
              Upload a Paper
              <FaArrowRight className="w-3 h-3 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link to="/analytics" className="btn-secondary text-base px-8 py-3.5 rounded-xl">
              <FaChartLine className="w-4 h-4" />
              Explore Analytics
            </Link>
          </div>
        </motion.div>
      </section>

      {/* ── Stats ── */}
      <section>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <AnimatedStat value="61K+" label="Papers Analyzed" />
          <AnimatedStat value="47"    label="Research Topics" />
          <AnimatedStat value="96.4%" label="AI Accuracy Rate" />
          <AnimatedStat value="24"    label="Available 24/7" suffix="/7" />
        </div>
      </section>

      {/* ── Features ── */}
      <section>
        <motion.div
          className="text-center mb-14"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="font-heading text-4xl font-bold text-white mb-4">
            Powerful <span className="gradient-text">AI Features</span>
          </h2>
          <p className="text-dark-400 max-w-xl mx-auto">
            Everything you need to extract maximum value from research papers — built on cutting-edge AI
          </p>
        </motion.div>

        <motion.div
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
        >
          {features.map((f, i) => (
            <motion.div key={i} variants={cardVariants}>
              <Link to={f.to} className="block group h-full">
                <div
                  className="h-full p-6 rounded-2xl border transition-all duration-300 cursor-pointer"
                  style={{
                    background: f.bg,
                    borderColor: f.border,
                    boxShadow: '0 4px 24px rgba(0,0,0,0.3)',
                  }}
                  onMouseEnter={e => {
                    e.currentTarget.style.transform = 'translateY(-4px)';
                    e.currentTarget.style.boxShadow = `0 12px 40px rgba(0,0,0,0.4), 0 0 30px ${f.border}`;
                  }}
                  onMouseLeave={e => {
                    e.currentTarget.style.transform = '';
                    e.currentTarget.style.boxShadow = '0 4px 24px rgba(0,0,0,0.3)';
                  }}
                >
                  <div
                    className={`w-12 h-12 rounded-xl bg-gradient-to-br ${f.gradient} flex items-center justify-center mb-5 shadow-lg`}
                  >
                    <f.Icon className="w-5 h-5 text-white" />
                  </div>
                  <h3 className="font-heading text-lg font-semibold text-white mb-2 group-hover:gradient-text transition-all">
                    {f.title}
                  </h3>
                  <p className="text-dark-400 text-sm leading-relaxed">{f.desc}</p>
                  <div className="mt-4 flex items-center gap-1 text-xs font-semibold" style={{ color: f.border }}>
                    Explore <FaArrowRight className="w-3 h-3 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              </Link>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* ── CTA Banner ── */}
      <motion.section
        initial={{ opacity: 0, scale: 0.98 }}
        whileInView={{ opacity: 1, scale: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
        className="relative overflow-hidden rounded-3xl p-10 md:p-16 text-center"
        style={{
          background: 'linear-gradient(135deg, rgba(139,92,246,0.25) 0%, rgba(99,102,241,0.2) 50%, rgba(6,182,212,0.15) 100%)',
          border: '1px solid rgba(139,92,246,0.35)',
        }}
      >
        <div className="absolute inset-0 rounded-3xl overflow-hidden pointer-events-none">
          <div className="absolute -top-20 -left-20 w-64 h-64 rounded-full blur-3xl"
            style={{ background: 'rgba(139,92,246,0.15)' }} />
          <div className="absolute -bottom-20 -right-20 w-64 h-64 rounded-full blur-3xl"
            style={{ background: 'rgba(6,182,212,0.1)' }} />
        </div>
        <div className="relative z-10">
          <h2 className="font-heading text-3xl md:text-4xl font-bold text-white mb-4">
            Ready to Analyze Your Research?
          </h2>
          <p className="text-dark-300 text-lg mb-8 max-w-xl mx-auto">
            Upload your first PDF and experience the power of AI-driven paper intelligence.
          </p>
          <Link to="/upload" className="btn-primary text-base px-10 py-4 rounded-xl">
            <FaUpload className="w-4 h-4" />
            Get Started — It's Free
          </Link>
        </div>
      </motion.section>
    </div>
  );
}
