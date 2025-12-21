/**
 * Akura AI - Main Application Component
 *
 * Teacher's Cockpit - Child-friendly split-screen design for dyslexia correction
 */

import React, { useEffect } from "react";
import { AnalysisProvider, useAnalysis } from "./context/AnalysisContext";
import LeftPanel from "./components/LeftPanel";
import RightPanel from "./components/RightPanel";
import Header from "./components/Header";
import StatusBar from "./components/StatusBar";
import ReportModal from "./components/ReportModal";

function AppContent() {
  const { checkApiStatus, showReport } = useAnalysis();

  // Check API status on mount
  useEffect(() => {
    checkApiStatus();
  }, [checkApiStatus]);

  return (
    <div className="min-h-screen fun-gradient flex flex-col relative overflow-hidden">
      {/* Animated Blob Decorations */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
        <div className="blob-1 top-0 left-0" />
        <div className="blob-2 top-1/4 right-0" />
        <div className="blob-3 bottom-0 left-1/3" />
      </div>

      {/* Header */}
      <Header />

      {/* Main Content - Responsive Split Screen */}
      <main className="flex-1 container mx-auto px-3 sm:px-4 py-4 sm:py-6 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6 h-full">
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
