/**
 * Akura AI - Main Application Component
 *
 * Clean, minimal split-screen design for dyslexia correction
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

  useEffect(() => {
    checkApiStatus();
  }, [checkApiStatus]);

  return (
    <div className="min-h-screen bg-neutral-50 flex flex-col">
      <Header />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-full">
          <LeftPanel />
          <RightPanel />
        </div>
      </main>

      <StatusBar />

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
