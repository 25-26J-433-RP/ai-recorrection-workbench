/**
 * Akura AI - Header Component
 *
 * Clean, minimal header with simple status indicators
 */

import React, { useState } from "react";
import { Brain, FileText, RefreshCw, Menu, X } from "lucide-react";
import { useAnalysis } from "../context/AnalysisContext";
import { Button, Badge } from "./ui";

function Header() {
  const { toggleReport, reset, analysisComplete, apiStatus } = useAnalysis();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="bg-white border-b border-neutral-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-md bg-neutral-900 flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-neutral-900">Akura AI</h1>
              <p className="text-xs text-neutral-500 hidden sm:block">
                Dyslexia Correction Engine
              </p>
            </div>
          </div>

          {/* Status */}
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
                className={`w-1.5 h-1.5 rounded-full ${
                  apiStatus === "online"
                    ? "bg-green-500"
                    : apiStatus === "offline"
                    ? "bg-amber-500"
                    : "bg-neutral-400"
                }`}
              />
              {apiStatus === "online"
                ? "Online"
                : apiStatus === "offline"
                ? "Demo"
                : "Connecting"}
            </Badge>
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
              Reset
            </Button>
          </div>

          {/* Mobile menu */}
          <button
            className="md:hidden p-2 text-neutral-600 hover:bg-neutral-100 rounded-md"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        {/* Mobile dropdown */}
        {mobileMenuOpen && (
          <div className="md:hidden mt-3 pt-3 border-t border-neutral-100 space-y-2">
            <div className="flex items-center gap-2">
              <Badge variant={apiStatus === "online" ? "online" : "offline"}>
                <span
                  className={`w-1.5 h-1.5 rounded-full ${
                    apiStatus === "online" ? "bg-green-500" : "bg-amber-500"
                  }`}
                />
                {apiStatus === "online" ? "Online" : "Demo"}
              </Badge>
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
                Reset
              </Button>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}

export default Header;
