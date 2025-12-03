/**
 * Akura AI - Right Panel Component (Interactive Editor)
 * 
 * Displays tokenized text with interactive error tokens.
 * Shows analysis results with clickable correction UI.
 */

import React from 'react';
import { CheckCircle2, XCircle, AlertTriangle, Sparkles, Copy, Check } from 'lucide-react';
import { useAnalysis } from '../context/AnalysisContext';
import { WORD_STATES, PATTERN_COLORS } from '../constants';
import ErrorToken from './ErrorToken';

function RightPanel() {
  const { 
    tokens, 
    isAnalyzing, 
    analysisComplete,
    totalErrors,
    correctedCount,
    ignoredCount,
    pendingCount,
    processingTime,
    modelUsed,
    getFinalText,
  } = useAnalysis();
  
  const [copied, setCopied] = React.useState(false);
  
  // Copy final text to clipboard
  const handleCopy = async () => {
    const finalText = getFinalText();
    await navigator.clipboard.writeText(finalText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  
  // Render placeholder when no analysis
  if (!analysisComplete && !isAnalyzing) {
    return (
      <div className="bg-white rounded-2xl shadow-lg border border-slate-200 flex flex-col h-[calc(100vh-200px)] min-h-[500px]">
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="text-center">
            <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-indigo-100 to-purple-100 flex items-center justify-center">
              <Sparkles className="w-10 h-10 text-indigo-500" />
            </div>
            <h3 className="text-lg font-semibold text-slate-700 mb-2">
              Ready to Analyze
            </h3>
            <p className="text-sm text-slate-500 max-w-xs mx-auto">
              Enter text in the left panel and click "Analyze" to see AI-powered dyslexia pattern detection.
            </p>
          </div>
        </div>
      </div>
    );
  }
  
  // Render loading state
  if (isAnalyzing) {
    return (
      <div className="bg-white rounded-2xl shadow-lg border border-slate-200 flex flex-col h-[calc(100vh-200px)] min-h-[500px]">
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="text-center">
            <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-indigo-100 to-purple-100 flex items-center justify-center">
              <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            </div>
            <h3 className="text-lg font-semibold text-slate-700 mb-2">
              Analyzing Patterns...
            </h3>
            <p className="text-sm text-slate-500">
              Our AI is detecting dyslexia patterns in the text
            </p>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="bg-white rounded-2xl shadow-lg border border-slate-200 flex flex-col h-[calc(100vh-200px)] min-h-[500px]">
      {/* Panel Header */}
      <div className="px-6 py-4 border-b border-slate-100">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-purple-500" />
              විශ්ලේෂණ ප්‍රතිඵල
            </h2>
            <p className="text-sm text-slate-500 mt-1">
              Click on highlighted words to review corrections
            </p>
          </div>
          
          {/* Copy Button */}
          <button
            onClick={handleCopy}
            className="flex items-center gap-2 px-3 py-1.5 text-sm bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg transition-colors"
          >
            {copied ? (
              <>
                <Check className="w-4 h-4 text-green-500" />
                <span>Copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-4 h-4" />
                <span>Copy Result</span>
              </>
            )}
          </button>
        </div>
        
        {/* Stats Bar */}
        <div className="flex items-center gap-4 mt-3 text-sm">
          <div className="flex items-center gap-1.5 text-red-600">
            <AlertTriangle className="w-4 h-4" />
            <span>{totalErrors} errors</span>
          </div>
          <div className="flex items-center gap-1.5 text-green-600">
            <CheckCircle2 className="w-4 h-4" />
            <span>{correctedCount} corrected</span>
          </div>
          <div className="flex items-center gap-1.5 text-slate-500">
            <XCircle className="w-4 h-4" />
            <span>{ignoredCount} ignored</span>
          </div>
          {pendingCount > 0 && (
            <div className="flex items-center gap-1.5 text-amber-600">
              <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
              <span>{pendingCount} pending</span>
            </div>
          )}
        </div>
      </div>
      
      {/* Interactive Text Area */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="text-xl leading-relaxed sinhala-text" dir="auto">
          {tokens.map((token) => {
            if (token.type === 'whitespace') {
              return <span key={token.id}>{token.displayWord}</span>;
            }
            
            if (token.type === 'error') {
              return <ErrorToken key={token.id} token={token} />;
            }
            
            // Normal word
            return (
              <span key={token.id} className="text-slate-800">
                {token.displayWord}
              </span>
            );
          })}
        </div>
      </div>
      
      {/* Footer Info */}
      <div className="px-6 py-3 bg-slate-50 border-t border-slate-100 rounded-b-2xl">
        <div className="flex items-center justify-between text-xs text-slate-500">
          <span>Model: {modelUsed}</span>
          <span>Processing time: {processingTime?.toFixed(0)}ms</span>
        </div>
      </div>
    </div>
  );
}

export default RightPanel;
