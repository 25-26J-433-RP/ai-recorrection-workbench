/**
 * Akura AI - Left Panel Component (Input Module)
 *
 * Child-friendly text input with playful styling and encouraging messages
 */

import React, { useState, useRef } from "react";
import {
  Send,
  AlertCircle,
  Lightbulb,
  PenTool,
  Upload,
  Camera,
  X,
  Image as ImageIcon,
  Loader2,
  Sparkles,
  Star,
} from "lucide-react";
import { useAnalysis } from "../context/AnalysisContext";
import { Button, Card, CardHeader, CardTitle, CardContent, Textarea } from "./ui";
import ocrService from "../services/ocr";

// Sample texts for quick testing - with fun descriptions
const SAMPLE_TEXTS = [
  {
    title: "🎯 නියැදිය 1",
    text: "මම ගෙරද යනව",
    description: "Can you spot the mixed-up letters?",
  },
  {
    title: "🎯 නියැදිය 2",
    text: "මං පාලස යනව",
    description: "Find the spelling mistakes!",
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

    const validation = ocrService.validateImage(file);
    if (!validation.valid) {
      setOcrError(validation.error);
      return;
    }

    setOcrError(null);
    setUploadedImage(file);

    const reader = new FileReader();
    reader.onload = (e) => {
      setImagePreview(e.target.result);
    };
    reader.readAsDataURL(file);

    setIsUploading(true);
    try {
      const result = await ocrService.extractTextFromImage(file);
      if (result.success) {
        setInputText(result.text);
      } else {
        setOcrError(result.error || "Oops! Couldn't read the image 😅");
      }
    } catch (error) {
      setOcrError(error.message || "Something went wrong 😢");
    } finally {
      setIsUploading(false);
    }
  };

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
      <CardHeader className="border-b-2 border-primary-100 bg-gradient-to-r from-primary-50 to-white">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <div className="p-2 bg-primary-100 rounded-xl">
                <PenTool className="w-5 h-5 text-primary-600" />
              </div>
              <span className="sinhala-text">✍️ ආදාන පෙළ</span>
            </CardTitle>
            <p className="text-sm text-primary-500 mt-2 font-medium">
              Type or upload your writing - I'll help find mistakes! 🔍
            </p>
          </div>

          {/* Character/Word Count - Fun display */}
          <div className="text-right">
            <div className="text-2xl font-bold text-primary-600">{wordCount}</div>
            <div className="text-xs text-primary-400">words ✏️</div>
          </div>
        </div>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col gap-4 p-4 sm:p-6 overflow-hidden">
        {/* Text Input */}
        <form onSubmit={handleSubmit} className="flex-1 flex flex-col gap-4">
          <Textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="📝 ඔබේ රචනය මෙහි ඇතුලත් කරන්න... (Type your essay here)"
            className="flex-1 min-h-[150px] sm:min-h-[180px] text-lg sinhala-text border-2 border-primary-200 focus:border-primary-400 rounded-2xl"
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
                className="w-full flex items-center justify-center gap-3 py-4 px-4 border-2 border-dashed border-primary-300 rounded-2xl text-primary-500 hover:border-primary-400 hover:text-primary-600 hover:bg-primary-50 transition-all duration-300 group"
              >
                {isUploading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>🔍 Reading your handwriting...</span>
                  </>
                ) : (
                  <>
                    <Camera className="w-6 h-6 group-hover:scale-110 transition-transform" />
                    <div className="text-left">
                      <span className="block font-bold">
                        📷 Upload a Photo!
                      </span>
                      <span className="text-xs text-primary-400">
                        Take a pic of your handwriting
                      </span>
                    </div>
                  </>
                )}
              </button>
            ) : (
              <div className="relative rounded-2xl overflow-hidden border-2 border-primary-200">
                <img
                  src={imagePreview}
                  alt="Uploaded essay"
                  className="w-full h-24 sm:h-32 object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-primary-900/50 to-transparent" />
                <button
                  type="button"
                  onClick={clearImage}
                  className="absolute top-2 right-2 p-2 bg-white rounded-full hover:bg-primary-100 shadow-lg"
                >
                  <X className="w-4 h-4 text-primary-600" />
                </button>
                <div className="absolute bottom-2 left-2 text-white text-sm font-bold">
                  ✅ Got your writing!
                </div>
              </div>
            )}

            {ocrError && (
              <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 px-4 py-3 rounded-2xl border-2 border-red-200">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{ocrError}</span>
              </div>
            )}
          </div>

          {/* Analyze Button - Big and Fun! */}
          <Button
            type="submit"
            size="lg"
            className="w-full text-lg"
            disabled={!inputText.trim() || isAnalyzing}
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="w-6 h-6 animate-spin" />
                <span>🔎 Checking...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-6 h-6" />
                <span className="sinhala-text">🚀 Let's Check It!</span>
              </>
            )}
          </Button>
        </form>

        {/* Tips and Sample Texts */}
        <div className="space-y-3 pt-3 border-t-2 border-primary-100">
          {/* Sample Texts */}
          <div>
            <p className="text-sm text-primary-500 mb-2 flex items-center gap-1 font-bold">
              <Lightbulb className="w-4 h-4 text-accent-yellow" />
              Try these examples:
            </p>
            <div className="flex flex-wrap gap-2">
              {SAMPLE_TEXTS.map((sample, idx) => (
                <button
                  key={idx}
                  onClick={() => loadSample(sample.text)}
                  className="text-sm px-4 py-2 bg-primary-100 hover:bg-primary-200 text-primary-700 rounded-full transition-all duration-200 font-bold hover:scale-105 sinhala-text"
                  title={sample.description}
                >
                  {sample.title}
                </button>
              ))}
            </div>
          </div>

          {/* Encouraging Message */}
          <div className="text-sm text-primary-500 bg-primary-50 px-4 py-3 rounded-2xl border-2 border-primary-100">
            <p className="flex items-start gap-2">
              <Star className="w-4 h-4 mt-0.5 shrink-0 text-accent-yellow animate-pulse" />
              <span>
                <strong>💡 Did you know?</strong> Making mistakes helps us learn! 
                This AI will find any mixed-up letters and help you fix them. 🌟
              </span>
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default LeftPanel;
