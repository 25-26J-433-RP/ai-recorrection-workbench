/**
 * Akura AI - Left Panel Component (Input Module)
 *
 * Text input area with character count and analyze button.
 * Includes image upload for OCR text extraction.
 * Shows helpful tips for teachers.
 */

import React, { useState, useRef } from "react";
import {
  Send,
  AlertCircle,
  Lightbulb,
  FileText,
  Upload,
  Camera,
  X,
  Image as ImageIcon,
  Loader2,
} from "lucide-react";
import { useAnalysis } from "../context/AnalysisContext";
import ocrService from "../services/ocr";

// Sample texts for quick testing
const SAMPLE_TEXTS = [
  {
    title: "නියැදිය 1",
    text: "මම ගෙරද යනව",
    description: "Visual scrambling + grammar",
  },
  {
    title: "නියැදිය 2",
    text: "මං පාලස යනව",
    description: "Spoken form + scrambling",
  },
];

function LeftPanel() {
  const {
    inputText,
    setInputText,
    analyzeText,
    isAnalyzing,
    analysisComplete,
  } = useAnalysis();

  // Image upload state
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedImage, setUploadedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [ocrError, setOcrError] = useState(null);
  const fileInputRef = useRef(null);

  const characterCount = inputText.length;
  const wordCount = inputText.trim() ? inputText.trim().split(/\s+/).length : 0;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputText.trim() && !isAnalyzing) {
      analyzeText();
    }
  };

  const loadSample = (text) => {
    setInputText(text);
  };

  // Handle image file selection
  const handleImageSelect = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file
    const validation = ocrService.validateImage(file);
    if (!validation.valid) {
      setOcrError(validation.error);
      return;
    }

    setOcrError(null);
    setUploadedImage(file);

    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setImagePreview(e.target.result);
    };
    reader.readAsDataURL(file);

    // Extract text using OCR
    setIsUploading(true);
    try {
      const result = await ocrService.extractTextFromImage(file);

      if (result.success) {
        setInputText(result.text);
        if (result.isDemoMode) {
          setOcrError(
            "Demo mode: Using sample text (configure VITE_GEMINI_API_KEY for real OCR)"
          );
        }
      } else {
        setOcrError(result.error || "Failed to extract text from image");
      }
    } catch (error) {
      setOcrError(error.message || "OCR processing failed");
    } finally {
      setIsUploading(false);
    }
  };

  // Clear uploaded image
  const clearImage = () => {
    setUploadedImage(null);
    setImagePreview(null);
    setOcrError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  // Trigger file input click
  const triggerUpload = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-slate-200 flex flex-col h-[calc(100vh-200px)] min-h-[500px]">
      {/* Panel Header */}
      <div className="px-6 py-4 border-b border-slate-100">
        <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
          <FileText className="w-5 h-5 text-indigo-500" />
          පෙළ ඇතුළත් කරන්න
        </h2>
        <p className="text-sm text-slate-500 mt-1">
          Enter student's text or upload an image of their essay
        </p>
      </div>

      {/* Image Upload Section */}
      <div className="px-6 pt-4">
        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp,image/gif"
          onChange={handleImageSelect}
          className="hidden"
        />

        {/* Upload Button & Preview */}
        {!imagePreview ? (
          <button
            type="button"
            onClick={triggerUpload}
            disabled={isUploading || isAnalyzing}
            className="w-full py-4 px-6 border-2 border-dashed border-slate-300 rounded-xl hover:border-indigo-400 hover:bg-indigo-50 transition-all flex flex-col items-center justify-center gap-2 group"
          >
            {isUploading ? (
              <>
                <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
                <span className="text-sm text-indigo-600 font-medium">
                  Extracting Sinhala text...
                </span>
              </>
            ) : (
              <>
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-indigo-100 to-purple-100 flex items-center justify-center group-hover:from-indigo-200 group-hover:to-purple-200 transition-colors">
                  <Camera className="w-6 h-6 text-indigo-600" />
                </div>
                <div className="text-center">
                  <span className="text-sm font-medium text-slate-700 group-hover:text-indigo-700">
                    Upload Essay Image
                  </span>
                  <p className="text-xs text-slate-500 mt-1">
                    Supports JPEG, PNG, WebP • Max 20MB
                  </p>
                </div>
              </>
            )}
          </button>
        ) : (
          <div className="relative rounded-xl overflow-hidden border border-slate-200">
            <img
              src={imagePreview}
              alt="Uploaded essay"
              className="w-full h-32 object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent" />
            <button
              onClick={clearImage}
              className="absolute top-2 right-2 p-1.5 bg-white/90 rounded-full hover:bg-white shadow-sm"
              title="Remove image"
            >
              <X className="w-4 h-4 text-slate-600" />
            </button>
            <div className="absolute bottom-2 left-2 flex items-center gap-1.5 text-white text-xs">
              <ImageIcon className="w-3.5 h-3.5" />
              <span>Text extracted from image</span>
            </div>
          </div>
        )}

        {/* OCR Error Message */}
        {ocrError && (
          <div
            className={`mt-2 px-3 py-2 rounded-lg text-xs flex items-start gap-2 ${
              ocrError.includes("Demo mode")
                ? "bg-amber-50 text-amber-700"
                : "bg-red-50 text-red-700"
            }`}
          >
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <span>{ocrError}</span>
          </div>
        )}

        <div className="flex items-center gap-3 my-3">
          <div className="flex-1 h-px bg-slate-200" />
          <span className="text-xs text-slate-400">or type manually</span>
          <div className="flex-1 h-px bg-slate-200" />
        </div>
      </div>

      {/* Text Input Area */}
      <form onSubmit={handleSubmit} className="flex-1 flex flex-col px-6 pb-6">
        <div className="relative flex-1">
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="ශිෂ්‍යයාගේ පෙළ මෙහි ඇතුළත් කරන්න..."
            className="w-full h-full p-4 text-lg sinhala-text bg-slate-50 border border-slate-200 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all placeholder-slate-400"
            dir="auto"
            disabled={isAnalyzing}
          />

          {/* Character/Word Count */}
          <div className="absolute bottom-3 right-3 flex items-center gap-3 text-xs text-slate-400">
            <span>{wordCount} words</span>
            <span>•</span>
            <span>{characterCount} chars</span>
          </div>
        </div>

        {/* Sample Texts */}
        <div className="mt-4">
          <p className="text-xs text-slate-500 mb-2 flex items-center gap-1">
            <Lightbulb className="w-3 h-3" />
            Quick samples:
          </p>
          <div className="flex flex-wrap gap-2">
            {SAMPLE_TEXTS.map((sample, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => loadSample(sample.text)}
                className="px-3 py-1.5 text-sm bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg transition-colors sinhala-text"
                title={sample.description}
              >
                {sample.title}
              </button>
            ))}
          </div>
        </div>

        {/* Analyze Button */}
        <button
          type="submit"
          disabled={!inputText.trim() || isAnalyzing}
          className={`mt-4 w-full py-3 px-6 rounded-xl font-medium text-white flex items-center justify-center gap-2 transition-all ${
            !inputText.trim() || isAnalyzing
              ? "bg-slate-300 cursor-not-allowed"
              : "bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
          }`}
        >
          {isAnalyzing ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              <span>විශ්ලේෂණය කරමින්...</span>
            </>
          ) : (
            <>
              <Send className="w-5 h-5" />
              <span>විශ්ලේෂණය කරන්න</span>
            </>
          )}
        </button>
      </form>

      {/* Tips Section */}
      <div className="px-6 py-4 bg-gradient-to-r from-amber-50 to-orange-50 border-t border-amber-100 rounded-b-2xl">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-amber-800">Teacher Tip</p>
            <p className="text-xs text-amber-700 mt-1">
              Copy text directly from student's work. The AI will identify
              dyslexia-related patterns like letter reversals, phonetic
              confusions, and grammar variations.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LeftPanel;
