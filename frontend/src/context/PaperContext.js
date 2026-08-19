import React, { createContext, useContext, useState, useCallback } from 'react';

const PaperContext = createContext(null);

export function PaperProvider({ children }) {
  const [paperData, setPaperData] = useState(() => {
    try {
      const saved = localStorage.getItem('paperAnalysis');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const savePaper = useCallback((data) => {
    setPaperData(data);
    localStorage.setItem('paperAnalysis', JSON.stringify(data));
  }, []);

  const clearPaper = useCallback(() => {
    setPaperData(null);
    localStorage.removeItem('paperAnalysis');
  }, []);

  return (
    <PaperContext.Provider value={{ paperData, savePaper, clearPaper }}>
      {children}
    </PaperContext.Provider>
  );
}

export function usePaper() {
  const ctx = useContext(PaperContext);
  if (!ctx) throw new Error('usePaper must be used within PaperProvider');
  return ctx;
}
