import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FaSun, FaMoon, FaBars, FaTimes,
  FaHome, FaUpload, FaFileAlt, FaComments, FaChartLine, FaSearch
} from 'react-icons/fa';

const navItems = [
  { path: '/',          label: 'Home',        icon: FaHome },
  { path: '/upload',    label: 'Upload',      icon: FaUpload },
  { path: '/summary',   label: 'Summary',     icon: FaFileAlt },
  { path: '/similar',   label: 'Similar',     icon: FaSearch },
  { path: '/chat',      label: 'Chat',        icon: FaComments },
  { path: '/analytics', label: 'Analytics',   icon: FaChartLine },
];

export default function Navbar() {
  const [isDark, setIsDark] = useState(true);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const location = useLocation();

  // always dark by default
  useEffect(() => {
    document.documentElement.classList.add('dark');
    setIsDark(true);
  }, []);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const toggleTheme = () => {
    setIsDark(d => !d);
    document.documentElement.classList.toggle('dark');
  };

  return (
    <motion.nav
      initial={{ y: -80, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? 'bg-dark-900/90 backdrop-blur-xl border-b border-primary-500/20 shadow-glass'
          : 'bg-dark-950/60 backdrop-blur-md border-b border-white/5'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="relative w-9 h-9 flex-shrink-0">
              <div className="absolute inset-0 rounded-xl bg-gradient-main opacity-80 group-hover:opacity-100 transition-opacity" />
              <div className="absolute inset-0 rounded-xl flex items-center justify-center">
                <span className="text-white font-bold text-sm leading-none">AI</span>
              </div>
              <div className="absolute -inset-1 rounded-xl bg-gradient-main opacity-20 blur group-hover:opacity-40 transition-opacity" />
            </div>
            <span className="hidden sm:block font-heading font-bold text-sm text-white leading-tight max-w-[180px] lg:max-w-none">
              Research Intelligence<span className="gradient-text"> Engine</span>
            </span>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-1">
            {navItems.map(item => {
              const active = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`relative flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    active
                      ? 'text-primary-300 bg-primary-500/15'
                      : 'text-dark-400 hover:text-white hover:bg-white/5'
                  }`}
                >
                  <item.icon className={`w-3.5 h-3.5 ${active ? 'text-primary-400' : ''}`} />
                  {item.label}
                  {active && (
                    <motion.div
                      layoutId="nav-indicator"
                      className="absolute inset-0 rounded-lg border border-primary-500/30"
                      transition={{ type: 'spring', bounce: 0.2, duration: 0.4 }}
                    />
                  )}
                </Link>
              );
            })}
          </div>

          {/* Right Controls */}
          <div className="flex items-center gap-2">
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 hover:border-primary-500/30 transition-all duration-200"
              aria-label="Toggle theme"
            >
              {isDark
                ? <FaSun  className="w-4 h-4 text-yellow-400" />
                : <FaMoon className="w-4 h-4 text-dark-400"   />
              }
            </button>

            {/* Mobile toggle */}
            <button
              onClick={() => setMobileOpen(o => !o)}
              className="md:hidden p-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 transition-all duration-200"
              aria-label="Menu"
            >
              {mobileOpen
                ? <FaTimes className="w-4 h-4 text-white" />
                : <FaBars  className="w-4 h-4 text-dark-400" />
              }
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="md:hidden overflow-hidden border-t border-white/5 bg-dark-950/95 backdrop-blur-xl"
          >
            <div className="px-4 py-3 flex flex-col gap-1">
              {navItems.map(item => {
                const active = location.pathname === item.path;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={() => setMobileOpen(false)}
                    className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                      active
                        ? 'bg-primary-500/15 text-primary-300 border border-primary-500/25'
                        : 'text-dark-400 hover:text-white hover:bg-white/5'
                    }`}
                  >
                    <item.icon className="w-4 h-4" />
                    {item.label}
                  </Link>
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  );
}
