import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Navbar from './components/Navbar';
import ErrorBoundary from './components/ErrorBoundary';
import { PaperProvider } from './context/PaperContext';
import { ChatProvider } from './context/ChatContext';

const Home = lazy(() => import('./pages/Home'));
const Upload = lazy(() => import('./pages/Upload'));
const Summary = lazy(() => import('./pages/Summary'));
const SimilarPapers = lazy(() => import('./pages/SimilarPapers'));
const Chat = lazy(() => import('./pages/Chat'));
const Analytics = lazy(() => import('./pages/Analytics'));

function LoadingFallback() {
  return (
    <div className="flex flex-col items-center justify-center py-32 space-y-4">
      <div className="spinner" />
      <p className="text-dark-400 text-sm animate-pulse">Loading...</p>
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <PaperProvider>
          <ChatProvider>
            <div className="bg-mesh" aria-hidden="true" />
            <div className="min-h-screen text-slate-100">
              <Navbar />
              <main className="pt-16">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
                  <Suspense fallback={<LoadingFallback />}>
                    <Routes>
                      <Route path="/" element={<Home />} />
                      <Route path="/upload" element={<Upload />} />
                      <Route path="/summary" element={<Summary />} />
                      <Route path="/similar" element={<SimilarPapers />} />
                      <Route path="/chat" element={<Chat />} />
                      <Route path="/analytics" element={<Analytics />} />
                      <Route path="*" element={<Navigate to="/" replace />} />
                    </Routes>
                  </Suspense>
                </div>
              </main>
            </div>
          </ChatProvider>
        </PaperProvider>
        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: 'rgba(13,13,36,0.95)',
              border: '1px solid rgba(139,92,246,0.3)',
              color: '#f1f5f9',
              backdropFilter: 'blur(12px)',
              borderRadius: '12px',
              fontSize: '0.875rem',
            },
            success: { iconTheme: { primary: '#8b5cf6', secondary: '#f1f5f9' } },
            error: { iconTheme: { primary: '#ef4444', secondary: '#f1f5f9' } },
          }}
        />
      </Router>
    </ErrorBoundary>
  );
}

export default App;
