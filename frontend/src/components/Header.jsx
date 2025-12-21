/**
 * Akura AI - Header Component
 *
 * Application header with logo, title, and navigation
 * Using shadcn/ui components for modern styling
 */

import React, { useState } from "react";
import { Brain, FileText, RefreshCw, Menu, X } from "lucide-react";
import { useAnalysis } from "../context/AnalysisContext";
import { Button, Badge } from "./ui";

function Header() {
  const { toggleReport, reset, analysisComplete, isDemoMode, apiStatus } =
    useAnalysis();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="bg-white/80 backdrop-blur-md shadow-sm border-b border-slate-200 sticky top-0 z-40">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          {/* Logo & Title */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-800 sinhala-text">
                Akura AI
              </h1>
              <p className="text-xs text-slate-500 hidden sm:block">
                Intelligent Dyslexia Correction Engine
              </p>
            </div>
          </div>

          {/* Desktop: Status Indicators */}
          <div className="hidden md:flex items-center gap-3">
            <Badge
              variant={
                apiStatus === "online"
                  ? "online"
                  : apiStatus === "offline"
                  ? "offline"
                  : "connecting"
              }
            >
              <span
                className={`w-2 h-2 rounded-full ${
                  apiStatus === "online"
                    ? "bg-green-500 animate-pulse"
                    : apiStatus === "offline"
                    ? "bg-amber-500"
                    : "bg-slate-400"
                }`}
              />
              {apiStatus === "online"
                ? "AI Online"
                : apiStatus === "offline"
                ? "Demo Mode"
                : "Connecting..."}
            </Badge>
            {apiStatus === "online" && (
              <Badge variant="secondary">
                <span className="w-2 h-2 rounded-full bg-purple-500" />
                Akura LLaMA 8B (Fine-tuned)
              </Badge>
            )}
          </div>

          {/* Desktop: Actions */}
          <div className="hidden md:flex items-center gap-2">
            {analysisComplete && (
              <Button variant="outline" size="sm" onClick={toggleReport}>
                <FileText className="w-4 h-4" />
                <span>View Report</span>
              </Button>
            )}
            <Button variant="ghost" size="sm" onClick={reset} title="Start over">
              <RefreshCw className="w-4 h-4" />
              <span>Reset</span>
            </Button>
          </div>

          {/* Mobile: Hamburger Menu */}
          <button
            className="md:hidden p-2 rounded-lg hover:bg-slate-100"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? (
              <X className="w-6 h-6 text-slate-700" />
            ) : (
              <Menu className="w-6 h-6 text-slate-700" />
            )}
          </button>
        </div>

        {/* Mobile Menu Dropdown */}
        {mobileMenuOpen && (
          <div className="md:hidden mt-4 pb-2 border-t border-slate-100 pt-4 space-y-3 animate-fade-in">
            {/* Mobile Status */}
            <div className="flex flex-wrap gap-2">
              <Badge
                variant={
                  apiStatus === "online"
                    ? "online"
                    : apiStatus === "offline"
                    ? "offline"
                    : "connecting"
                }
              >
                <span
                  className={`w-2 h-2 rounded-full ${
                    apiStatus === "online"
                      ? "bg-green-500 animate-pulse"
                      : apiStatus === "offline"
                      ? "bg-amber-500"
                      : "bg-slate-400"
                  }`}
                />
                {apiStatus === "online"
                  ? "AI Online"
                  : apiStatus === "offline"
                  ? "Demo Mode"
                  : "Connecting..."}
              </Badge>
              {apiStatus === "online" && (
                <Badge variant="secondary">Akura LLaMA 8B</Badge>
              )}
            </div>

            {/* Mobile Actions */}
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
                  <span>View Report</span>
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
                <span>Reset</span>
              </Button>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}

export default Header;
