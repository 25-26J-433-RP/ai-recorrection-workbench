/**
 * Akura AI - Status Bar Component
 *
 * Clean, minimal footer
 */

import React from "react";
import { Wifi, WifiOff, Cpu } from "lucide-react";
import { useAnalysis } from "../context/AnalysisContext";

function StatusBar() {
  const { apiStatus, modelUsed, totalErrors, correctedCount } = useAnalysis();

  return (
    <footer className="bg-white border-t border-neutral-200 text-xs py-2 px-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between text-neutral-400">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5">
            {apiStatus === "online" ? (
              <Wifi className="w-3 h-3 text-green-500" />
            ) : (
              <WifiOff className="w-3 h-3 text-amber-500" />
            )}
            <span>{apiStatus === "online" ? "Connected" : "Demo mode"}</span>
          </div>
          {modelUsed && (
            <div className="flex items-center gap-1.5">
              <Cpu className="w-3 h-3" />
              <span className="truncate max-w-[150px]">{modelUsed}</span>
            </div>
          )}
        </div>
        <div className="flex items-center gap-4">
          {totalErrors > 0 && (
            <span>
              {correctedCount}/{totalErrors} corrected
            </span>
          )}
          <span>Akura AI v1.0</span>
        </div>
      </div>
    </footer>
  );
}

export default StatusBar;
