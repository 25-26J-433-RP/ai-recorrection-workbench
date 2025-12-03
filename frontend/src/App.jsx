/**
 * Akura AI - Main Application Component
 * 
 * Teacher's Cockpit - Split-screen design for dyslexia correction workflow
 */

import React, { useEffect } from 'react';
import { AnalysisProvider, useAnalysis } from './context/AnalysisContext';
import LeftPanel from './components/LeftPanel';
import RightPanel from './components/RightPanel';
import Header from './components/Header';
import StatusBar from './components/StatusBar';
import ReportModal from './components/ReportModal';

function AppContent() {
  const { checkApiStatus, showReport } = useAnalysis();
  
  // Check API status on mount
  useEffect(() => {
    checkApiStatus();
  }, [checkApiStatus]);
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex flex-col">
      {/* Header */}
      <Header />
      
      {/* Main Content - Split Screen */}
      <main className="flex-1 container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-full">
          {/* Left Panel - Input */}
          <LeftPanel />
          
          {/* Right Panel - Interactive Editor */}
          <RightPanel />
        </div>
      </main>
      
      {/* Status Bar */}
      <StatusBar />
      
      {/* Report Modal */}
      {showReport && <ReportModal />}
    </div>
  );
}

function App() {
  return (
    <AnalysisProvider>
      <AppContent />
    </AnalysisProvider>
  );
}

export default App;
