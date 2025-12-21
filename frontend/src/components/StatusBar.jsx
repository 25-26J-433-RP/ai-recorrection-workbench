/**
 * Akura AI - Status Bar Component
 *
 * Bottom status bar showing connection status and quick stats
 */

import React from "react";
import { Wifi, WifiOff, Server, Activity } from "lucide-react";
import { useAnalysis } from "../context/AnalysisContext";

function StatusBar() {
  const { apiStatus, isDemoMode, modelUsed, totalErrors, correctedCount } =
    useAnalysis();

  return (
    <footer className="bg-slate-800 text-slate-300 text-xs py-2 px-4">
      <div className="container mx-auto flex items-center justify-between">
        {/* Left - Connection Status */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5">
            {apiStatus === "online" ? (
              <Wifi className="w-3.5 h-3.5 text-green-400" />
            ) : (
              <WifiOff className="w-3.5 h-3.5 text-amber-400" />
            )}
            <span>
              {apiStatus === "online"
                ? "Connected"
                : apiStatus === "offline"
                ? "Demo Mode"
                : "Connecting..."}
            </span>
          </div>

          {modelUsed && (
            <div className="flex items-center gap-1.5">
              <Server className="w-3.5 h-3.5 text-purple-400" />
              <span className="text-purple-400">
                {modelUsed.includes("akura") || modelUsed.includes("llama") 
                  ? "Akura LLaMA 8B" 
                  : modelUsed === "demo-mode" 
                  ? "Demo Mode" 
                  : modelUsed.includes("gemini") 
                  ? "Gemini" 
                  : modelUsed}
              </span>
            </div>
          )}
        </div>

        {/* Center - Brand */}
        <div className="text-slate-500">
          Akura AI v1.0 • Intelligent Dyslexia Correction Engine
        </div>

        {/* Right - Quick Stats */}
        <div className="flex items-center gap-4">
          {totalErrors > 0 && (
            <div className="flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-indigo-400" />
              <span>
                {correctedCount}/{totalErrors} corrected
              </span>
            </div>
          )}
          <span className="text-slate-500">© 2024</span>
        </div>
      </div>
    </footer>
  );
}

export default StatusBar;
