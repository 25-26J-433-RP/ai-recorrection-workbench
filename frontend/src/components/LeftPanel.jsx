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
import { Button, Card, CardHeader, CardTitle, CardContent, Textarea } from "./ui";
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

  return (
    <Card className="flex flex-col h-full min-h-[500px] lg:h-[calc(100vh-200px)]">
      <CardHeader className="border-b border-slate-100">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-indigo-500" />
              <span className="sinhala-text">ආදාන පෙළ</span>
            </CardTitle>
            <p className="text-sm text-slate-500 mt-1">
              Enter or upload student's essay for analysis
            </p>
          </div>

          {/* Character/Word Count */}
          <div className="text-xs text-slate-400 text-right">
            <span className="block">{characterCount} characters</span>
            <span className="block">{wordCount} words</span>
          </div>
        </div>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col gap-4 p-4 sm:p-6 overflow-hidden">
        {/* Text Input */}
        <form onSubmit={handleSubmit} className="flex-1 flex flex-col gap-4">
          <Textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="සිසුන්ගේ රචනය මෙහි ඇතුලත් කරන්න..."
            className="flex-1 min-h-[150px] sm:min-h-[200px] text-lg sinhala-text"
            disabled={isAnalyzing}
          />

          {/* Image Upload Section */}
          <div className="space-y-2">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleImageSelect}
              className="hidden"
            />

            {!imagePreview ? (
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={isUploading}
                className="w-full flex items-center justify-center gap-3 py-4 px-4 border-2 border-dashed border-slate-200 rounded-xl text-slate-500 hover:border-indigo-300 hover:text-indigo-600 hover:bg-indigo-50/50 transition-all duration-200 group"
              >
                {isUploading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Extracting text from image...</span>
                  </>
                ) : (
                  <>
                    <Camera className="w-5 h-5 group-hover:scale-110 transition-transform" />
                    <div className="text-left">
                      <span className="block font-medium">
                        Upload Handwritten Essay
                      </span>
                      <span className="text-xs text-slate-400">
                        Supports JPG, PNG (max 10MB)
                      </span>
                    </div>
                  </>
                )}
              </button>
            ) : (
              <div className="relative rounded-xl overflow-hidden border border-slate-200">
                <img
                  src={imagePreview}
                  alt="Uploaded essay"
                  className="w-full h-24 sm:h-32 object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent" />
                <button
                  type="button"
                  onClick={clearImage}
                  className="absolute top-2 right-2 p-1.5 bg-white/90 rounded-full hover:bg-white shadow-sm"
                >
                  <X className="w-4 h-4 text-slate-600" />
                </button>
                <div className="absolute bottom-2 left-2 text-white text-xs">
                  ✓ Text extracted from image
                </div>
              </div>
            )}

            {ocrError && (
              <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{ocrError}</span>
              </div>
            )}
          </div>

          {/* Analyze Button */}
          <Button
            type="submit"
            size="lg"
            className="w-full"
            disabled={!inputText.trim() || isAnalyzing}
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                <span className="sinhala-text">විශ්ලේෂණය කරන්න</span>
              </>
            )}
          </Button>
        </form>

        {/* Tips and Sample Texts */}
        <div className="space-y-3 pt-2 border-t border-slate-100">
          {/* Sample Texts */}
          <div>
            <p className="text-xs text-slate-400 mb-2 flex items-center gap-1">
              <Lightbulb className="w-3 h-3" />
              Quick test samples:
            </p>
            <div className="flex flex-wrap gap-2">
              {SAMPLE_TEXTS.map((sample, idx) => (
                <button
                  key={idx}
                  onClick={() => loadSample(sample.text)}
                  className="text-xs px-3 py-1.5 bg-slate-100 hover:bg-indigo-100 text-slate-600 hover:text-indigo-700 rounded-full transition-colors sinhala-text"
                  title={sample.description}
                >
                  {sample.title}
                </button>
              ))}
            </div>
          </div>

          {/* Tips */}
          <div className="text-xs text-slate-400 space-y-1">
            <p className="flex items-start gap-1.5">
              <AlertCircle className="w-3 h-3 mt-0.5 shrink-0 text-indigo-400" />
              <span>
                This AI is trained on Sinhala dyslexia patterns. Click on
                highlighted words in the output to accept or modify corrections.
              </span>
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default LeftPanel;
