/**
 * Akura AI - Status Bar Component
 *
 * Grammarly-style minimal footer
 */

import React from "react";
import { Circle, Cpu } from "lucide-react";
import { useAnalysis } from "../context/AnalysisContext";

function StatusBar() {
  const { apiStatus, modelUsed } = useAnalysis();

  const getModelDisplayName = () => {
    if (!modelUsed) return null;
    if (modelUsed.includes("akura") || modelUsed.includes("llama")) {
      return "Akura LLaMA 8B";
    }
    if (modelUsed === "demo-mode") return "Demo Mode";
    if (modelUsed.includes("gemini")) return "Gemini";
    return modelUsed;
  };

  return (
    <footer className="bg-white border-t border-neutral-200 py-2 px-4 text-xs">
      <div className="max-w-6xl mx-auto flex items-center justify-between text-neutral-400">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5">
            <Circle
              className={`w-2 h-2 ${
                apiStatus === "online"
                  ? "fill-grammarly-green text-grammarly-green"
                  : "fill-grammarly-orange text-grammarly-orange"
              }`}
            />
            <span>{apiStatus === "online" ? "Connected" : "Demo mode"}</span>
          </div>
          {getModelDisplayName() && (
            <div className="flex items-center gap-1.5">
              <Cpu className="w-3 h-3" />
              <span>{getModelDisplayName()}</span>
            </div>
          )}
        </div>
        <span>Akura v1.0</span>
      </div>
    </footer>
  );
}

export default StatusBar;
