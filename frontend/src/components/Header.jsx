/**
 * Akura AI - Header Component
 *
 * Grammarly-inspired clean header with correct model name
 */

import React, { useState } from "react";
import { Brain, FileText, RefreshCw, Menu, X, Circle } from "lucide-react";
import { useAnalysis } from "../context/AnalysisContext";
import { Button, Badge } from "./ui";

function Header() {
  const { toggleReport, reset, analysisComplete, apiStatus, modelUsed } = useAnalysis();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Get clean model name
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
    <header className="bg-white border-b border-neutral-200">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-3">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-grammarly-green flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-neutral-900">Akura</h1>
              <p className="text-xs text-neutral-500 hidden sm:block">
                Sinhala Writing Assistant
              </p>
            </div>
          </div>

          {/* Center - Model & Status */}
          <div className="hidden md:flex items-center gap-3">
            <Badge variant={apiStatus === "online" ? "online" : "offline"}>
              <Circle
                className={`w-2 h-2 ${
                  apiStatus === "online" ? "fill-grammarly-green text-grammarly-green" : "fill-grammarly-orange text-grammarly-orange"
                }`}
              />
              {apiStatus === "online" ? "Connected" : "Demo"}
            </Badge>
            {getModelDisplayName() && (
              <Badge variant="default">
                {getModelDisplayName()}
              </Badge>
            )}
          </div>

          {/* Actions */}
          <div className="hidden md:flex items-center gap-2">
            {analysisComplete && (
              <Button variant="outline" size="sm" onClick={toggleReport}>
                <FileText className="w-4 h-4" />
                Report
              </Button>
            )}
            <Button variant="ghost" size="sm" onClick={reset}>
              <RefreshCw className="w-4 h-4" />
              New
            </Button>
          </div>

          {/* Mobile */}
          <button
            className="md:hidden p-2 text-neutral-600 hover:bg-neutral-100 rounded-md"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        {/* Mobile dropdown */}
        {mobileMenuOpen && (
          <div className="md:hidden mt-3 pt-3 border-t border-neutral-100 space-y-3">
            <div className="flex items-center gap-2 flex-wrap">
              <Badge variant={apiStatus === "online" ? "online" : "offline"}>
                <Circle
                  className={`w-2 h-2 ${
                    apiStatus === "online" ? "fill-grammarly-green text-grammarly-green" : "fill-grammarly-orange text-grammarly-orange"
                  }`}
                />
                {apiStatus === "online" ? "Connected" : "Demo"}
              </Badge>
              {getModelDisplayName() && (
                <Badge variant="default">{getModelDisplayName()}</Badge>
              )}
            </div>
            <div className="flex gap-2">
              {analysisComplete && (
                <Button
                  variant="outline"
                  size="sm"
                  className="flex-1"
                  onClick={() => {
                    toggleReport();
                    setMobileMenuOpen(false);
                  }}
                >
                  <FileText className="w-4 h-4" />
                  Report
                </Button>
              )}
              <Button
                variant="ghost"
                size="sm"
                className="flex-1"
                onClick={() => {
                  reset();
                  setMobileMenuOpen(false);
                }}
              >
                <RefreshCw className="w-4 h-4" />
                New
              </Button>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}

export default Header;
