/**
 * Akura AI - Header Component
 *
 * Child-friendly header with playful styling and educational theme
 */

import React, { useState } from "react";
import { BookOpen, FileText, RefreshCw, Menu, X, Sparkles, Star } from "lucide-react";
import { useAnalysis } from "../context/AnalysisContext";
import { Button, Badge } from "./ui";

function Header() {
  const { toggleReport, reset, analysisComplete, isDemoMode, apiStatus } =
    useAnalysis();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="bg-white/90 backdrop-blur-md shadow-lg border-b-2 border-primary-200 sticky top-0 z-40">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          {/* Logo & Title - Child-friendly with emoji */}
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center shadow-lg shadow-primary-500/30 animate-bounce-soft">
              <BookOpen className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-xl sm:text-2xl font-extrabold text-primary-700 flex items-center gap-2">
                Akura AI
                <Sparkles className="w-5 h-5 text-accent-yellow animate-pulse" />
              </h1>
              <p className="text-xs sm:text-sm text-primary-500 hidden sm:block font-medium">
                ✨ Your Smart Learning Helper ✨
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
                className={`w-2.5 h-2.5 rounded-full ${
                  apiStatus === "online"
                    ? "bg-green-500 animate-pulse"
                    : apiStatus === "offline"
                    ? "bg-amber-500"
                    : "bg-gray-400"
                }`}
              />
              {apiStatus === "online"
                ? "🟢 Ready to Help!"
                : apiStatus === "offline"
                ? "🟡 Demo Mode"
                : "⏳ Connecting..."}
            </Badge>
            {apiStatus === "online" && (
              <Badge variant="star">
                <Star className="w-4 h-4" />
                Akura AI Model
              </Badge>
            )}
          </div>

          {/* Desktop: Actions */}
          <div className="hidden md:flex items-center gap-2">
            {analysisComplete && (
              <Button variant="outline" size="sm" onClick={toggleReport}>
                <FileText className="w-4 h-4" />
                <span>📊 Report</span>
              </Button>
            )}
            <Button variant="ghost" size="sm" onClick={reset} title="Start over">
              <RefreshCw className="w-4 h-4" />
              <span>🔄 New</span>
            </Button>
          </div>

          {/* Mobile: Hamburger Menu */}
          <button
            className="md:hidden p-2 rounded-xl bg-primary-100 hover:bg-primary-200 transition-colors"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? (
              <X className="w-6 h-6 text-primary-600" />
            ) : (
              <Menu className="w-6 h-6 text-primary-600" />
            )}
          </button>
        </div>

        {/* Mobile Menu Dropdown */}
        {mobileMenuOpen && (
          <div className="md:hidden mt-4 pb-2 border-t-2 border-primary-100 pt-4 space-y-3 animate-fade-in">
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
                      : "bg-gray-400"
                  }`}
                />
                {apiStatus === "online"
                  ? "🟢 Ready!"
                  : apiStatus === "offline"
                  ? "🟡 Demo"
                  : "⏳ Wait..."}
              </Badge>
              {apiStatus === "online" && (
                <Badge variant="star">
                  <Star className="w-3 h-3" />
                  AI Active
                </Badge>
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
                  <span>📊 Report</span>
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
                <span>🔄 New</span>
              </Button>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}

export default Header;
