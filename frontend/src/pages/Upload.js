import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useDropzone } from 'react-dropzone';
import toast from 'react-hot-toast';
import {
  FaUpload, FaFilePdf, FaTimes, FaCheck,
  FaBrain, FaSearch, FaComments, FaArrowRight
} from 'react-icons/fa';
import api from '../api';
import { usePaper } from '../context/PaperContext';

const MAX_SIZE_MB = 50;

const features = [
  { Icon: FaBrain, title: 'Smart Parsing', desc: 'Extracts title, authors, abstract, and all sections automatically.' },
  { Icon: FaSearch, title: 'AI Analysis', desc: 'Generates summaries, keywords, and research gap detection.' },
  { Icon: FaComments, title: 'Fast Processing', desc: 'Full insights delivered in seconds via our optimised pipeline.' },
];

export default function Upload() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [done, setDone] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusText, setStatusText] = useState('');
  const navigate = useNavigate();
  const { savePaper } = usePaper();

  const onDrop = useCallback((accepted) => {
    const f = accepted[0];
    if (!f) return;
    if (f.type !== 'application/pdf') {
      toast.error('Only PDF files are supported');
      return;
    }
    if (f.size > MAX_SIZE_MB * 1024 * 1024) {
      toast.error(`File too large. Maximum size is ${MAX_SIZE_MB}MB`);
      return;
    }
    setFile(f);
    setDone(false);
    setProgress(0);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1,
    disabled: uploading,
    maxSize: MAX_SIZE_MB * 1024 * 1024,
  });

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setProgress(0);

    const stages = [
      { pct: 15, text: 'Uploading PDF...' },
      { pct: 35, text: 'Parsing document...' },
      { pct: 55, text: 'Extracting metadata...' },
      { pct: 75, text: 'Generating summary...' },
      { pct: 90, text: 'Indexing for search...' },
      { pct: 100, text: 'Finalizing...' },
    ];

    let stageIdx = 0;
    const advanceStage = () => {
      if (stageIdx < stages.length) {
        setProgress(stages[stageIdx].pct);
        setStatusText(stages[stageIdx].text);
        stageIdx++;
      }
    };

    const progressInterval = setInterval(advanceStage, 800);

    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await api.post('/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 180000,
      });

      clearInterval(progressInterval);
      setProgress(100);
      setStatusText('Complete!');

      savePaper(response.data);
      setDone(true);
      toast.success('Paper analysed successfully!');
      setTimeout(() => navigate('/summary'), 1200);
    } catch (err) {
      clearInterval(progressInterval);
      setProgress(0);
      setStatusText('');
      const msg = err.response?.data?.detail || 'Upload failed. Please try again.';
      toast.error(msg);
    } finally {
      setUploading(false);
    }
  };

  const clearFile = (e) => {
    e.stopPropagation();
    setFile(null);
    setDone(false);
    setProgress(0);
    setStatusText('');
  };

  const isUploading = uploading && !done;

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-16">
      <motion.div className="text-center" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
        <h1 className="font-heading text-4xl md:text-5xl font-bold text-white mb-3">
          Upload Research <span className="gradient-text">Paper</span>
        </h1>
        <p className="text-dark-400 text-lg max-w-xl mx-auto">
          Drop your PDF to get AI-powered insights instantly
        </p>
      </motion.div>

      <motion.div className="glass-card p-8" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: 0.1 }}>
        <div
          {...getRootProps()}
          className={`drop-zone p-12 text-center cursor-pointer transition-all duration-300 ${
            isDragActive ? 'active' : ''
          } ${isUploading ? 'pointer-events-none opacity-60' : ''}`}
        >
          <input {...getInputProps()} />
          <AnimatePresence mode="wait">
            {file ? (
              <motion.div key="file" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.9 }} className="flex flex-col items-center gap-4">
                <div className="relative">
                  <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-red-500 to-rose-600 flex items-center justify-center shadow-lg">
                    <FaFilePdf className="w-10 h-10 text-white" />
                  </div>
                  {!isUploading && (
                    <button onClick={clearFile} className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-dark-700 border border-dark-600 flex items-center justify-center hover:bg-red-500/30 transition-colors">
                      <FaTimes className="w-3 h-3 text-dark-400" />
                    </button>
                  )}
                </div>
                <div>
                  <p className="font-semibold text-white text-lg">{file.name}</p>
                  <p className="text-dark-400 text-sm mt-1">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
              </motion.div>
            ) : (
              <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="flex flex-col items-center gap-4">
                <motion.div animate={{ y: [0, -8, 0] }} transition={{ duration: 2.5, repeat: Infinity, ease: 'easeInOut' }} className="w-20 h-20 rounded-2xl bg-gradient-to-br from-primary-500/20 to-primary-700/20 border border-primary-500/30 flex items-center justify-center">
                  <FaUpload className="w-9 h-9 text-primary-400" />
                </motion.div>
                <div>
                  <p className="font-semibold text-white text-xl">
                    {isDragActive ? 'Drop it here!' : 'Drag & drop your PDF'}
                  </p>
                  <p className="text-dark-400 text-sm mt-1">or click to browse — max {MAX_SIZE_MB} MB</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <AnimatePresence>
          {isUploading && (
            <motion.div key="progress" initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }} className="mt-6 space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-dark-400">{statusText}</span>
                <span className="text-primary-400 font-semibold">{progress}%</span>
              </div>
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${progress}%` }} />
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {done && (
            <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="mt-6 flex items-center gap-3 px-5 py-4 rounded-xl" style={{ background: 'rgba(34,197,94,0.1)', border: '1px solid rgba(34,197,94,0.3)' }}>
              <FaCheck className="w-5 h-5 text-emerald-400 flex-shrink-0" />
              <p className="text-emerald-300 font-medium text-sm">Paper analysed! Redirecting to Summary...</p>
            </motion.div>
          )}
        </AnimatePresence>

        <div className="mt-8 flex justify-center">
          <motion.button
            onClick={handleUpload}
            disabled={!file || isUploading}
            whileHover={{ scale: file && !isUploading ? 1.03 : 1 }}
            whileTap={{ scale: 0.98 }}
            className="btn-primary text-base px-10 py-4 rounded-xl disabled:opacity-40"
          >
            {isUploading ? (
              <>
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Analysing...
              </>
            ) : (
              <>
                <FaUpload className="w-4 h-4" />
                Upload &amp; Analyse
                <FaArrowRight className="w-3.5 h-3.5" />
              </>
            )}
          </motion.button>
        </div>
      </motion.div>

      <motion.div className="grid grid-cols-1 md:grid-cols-3 gap-4" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: 0.3 }}>
        {features.map((f, i) => (
          <div key={i} className="glass-card p-5 flex gap-4 items-start">
            <div className="w-10 h-10 flex-shrink-0 rounded-xl bg-primary-500/15 border border-primary-500/25 flex items-center justify-center">
              <f.Icon className="w-4 h-4 text-primary-400" />
            </div>
            <div>
              <h3 className="font-semibold text-white text-sm mb-1">{f.title}</h3>
              <p className="text-dark-400 text-xs leading-relaxed">{f.desc}</p>
            </div>
          </div>
        ))}
      </motion.div>
    </div>
  );
}
