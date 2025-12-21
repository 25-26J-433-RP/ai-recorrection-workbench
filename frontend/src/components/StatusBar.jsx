/**
 * Akura AI - Status Bar Component
 *
 * Child-friendly footer with fun status indicators
 */

import React from "react";
import { Wifi, WifiOff, Cpu, Activity, Heart } from "lucide-react";
import { useAnalysis } from "../context/AnalysisContext";

function StatusBar() {
  const { apiStatus, isDemoMode, modelUsed, totalErrors, correctedCount } =
    useAnalysis();

  const getModelDisplayName = () => {
    if (!modelUsed) return null;
    if (modelUsed.includes("akura") || modelUsed.includes("llama")) {
      return "🤖 Akura AI";
    }
    if (modelUsed === "demo-mode") return "🎮 Demo";
    if (modelUsed.includes("gemini")) return "✨ Gemini";
    return modelUsed;
  };

  return (
    <footer className="bg-primary-800 text-primary-100 text-sm py-2 px-4 relative z-10">
      <div className="container mx-auto">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-2">
          {/* Left - Connection Status */}
          <div className="flex items-center gap-3 sm:gap-4">
            <div className="flex items-center gap-1.5">
              {apiStatus === "online" ? (
                <Wifi className="w-4 h-4 text-green-400" />
              ) : (
                <WifiOff className="w-4 h-4 text-amber-400" />
              )}
              <span className={apiStatus === "online" ? "text-green-400 font-bold" : "text-amber-400 font-bold"}>
                {apiStatus === "online"
                  ? "🟢 Connected!"
                  : apiStatus === "offline"
                  ? "🟡 Demo Mode"
                  : "⏳ Connecting..."}
              </span>
            </div>

            {modelUsed && (
              <div className="flex items-center gap-1.5">
                <Cpu className="w-4 h-4 text-primary-300" />
                <span className="text-primary-200 font-medium">{getModelDisplayName()}</span>
              </div>
            )}
          </div>

          {/* Center - Brand */}
          <div className="hidden md:flex items-center gap-2 text-primary-300 font-medium">
            <span>Made with</span>
            <Heart className="w-4 h-4 text-red-400 animate-pulse" />
            <span>for learners • Akura AI v1.0</span>
          </div>

          {/* Right - Quick Stats */}
          <div className="flex items-center gap-3 sm:gap-4">
            {totalErrors > 0 && (
              <div className="flex items-center gap-1.5 text-green-400 font-bold">
                <Activity className="w-4 h-4" />
                <span>
                  ✅ {correctedCount}/{totalErrors}
                </span>
              </div>
            )}
            <span className="text-primary-400">© 2024</span>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default StatusBar;
