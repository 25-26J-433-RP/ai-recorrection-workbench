/**
 * Akura AI - Left Panel Component
 *
 * Clean, minimal text input with OCR upload
 */

import React, { useState, useRef } from "react";
import {
  Send,
  AlertCircle,
  Upload,
  X,
  Loader2,
} from "lucide-react";
import { useAnalysis } from "../context/AnalysisContext";
import { Button, Card, CardHeader, CardTitle, CardContent, Textarea } from "./ui";
import ocrService from "../services/ocr";

const SAMPLE_TEXTS = [
  { title: "Sample 1", text: "මම ගෙරද යනව" },
  { title: "Sample 2", text: "මං පාලස යනව" },
];

function LeftPanel() {
  const {
    inputText,
    setInputText,
    analyzeText,
    isAnalyzing,
  } = useAnalysis();

  const [isUploading, setIsUploading] = useState(false);
  const [imagePreview, setImagePreview] = useState(null);
  const [ocrError, setOcrError] = useState(null);
  const fileInputRef = useRef(null);

  const wordCount = inputText.trim() ? inputText.trim().split(/\s+/).length : 0;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputText.trim() && !isAnalyzing) {
      analyzeText();
    }
  };

  const handleImageSelect = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const validation = ocrService.validateImage(file);
    if (!validation.valid) {
      setOcrError(validation.error);
      return;
    }

    setOcrError(null);
    const reader = new FileReader();
    reader.onload = (e) => setImagePreview(e.target.result);
    reader.readAsDataURL(file);

    setIsUploading(true);
    try {
      const result = await ocrService.extractTextFromImage(file);
      if (result.success) {
        setInputText(result.text);
      } else {
        setOcrError(result.error || "Failed to extract text");
      }
    } catch (error) {
      setOcrError(error.message || "OCR failed");
    } finally {
      setIsUploading(false);
    }
  };

  const clearImage = () => {
    setImagePreview(null);
    setOcrError(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  return (
    <Card className="flex flex-col h-full min-h-[500px] lg:min-h-0">
      <CardHeader className="border-b border-neutral-100">
        <div className="flex items-center justify-between">
          <CardTitle>Input Text</CardTitle>
          <span className="text-xs text-neutral-400">{wordCount} words</span>
        </div>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col gap-4 p-5">
        <form onSubmit={handleSubmit} className="flex-1 flex flex-col gap-4">
          <Textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Enter or paste text to analyze..."
            className="flex-1 min-h-[180px] sinhala-text"
            disabled={isAnalyzing}
          />

          {/* Image upload */}
          <div>
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
                className="w-full flex items-center justify-center gap-2 py-3 border border-dashed border-neutral-300 rounded-md text-neutral-500 hover:border-neutral-400 hover:text-neutral-600 transition-colors text-sm"
              >
                {isUploading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Extracting text...
                  </>
                ) : (
                  <>
                    <Upload className="w-4 h-4" />
                    Upload image for OCR
                  </>
                )}
              </button>
            ) : (
              <div className="relative rounded-md overflow-hidden border border-neutral-200">
                <img
                  src={imagePreview}
                  alt="Upload"
                  className="w-full h-20 object-cover"
                />
                <button
                  type="button"
                  onClick={clearImage}
                  className="absolute top-1 right-1 p-1 bg-white rounded-full shadow-sm hover:bg-neutral-50"
                >
                  <X className="w-3 h-3 text-neutral-600" />
                </button>
              </div>
            )}

            {ocrError && (
              <div className="flex items-center gap-2 text-sm text-red-600 mt-2">
                <AlertCircle className="w-4 h-4" />
                {ocrError}
              </div>
            )}
          </div>

          <Button
            type="submit"
            disabled={!inputText.trim() || isAnalyzing}
            className="w-full"
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                Analyze
              </>
            )}
          </Button>
        </form>

        {/* Quick samples */}
        <div className="pt-3 border-t border-neutral-100">
          <p className="text-xs text-neutral-400 mb-2">Quick samples:</p>
          <div className="flex gap-2">
            {SAMPLE_TEXTS.map((sample, idx) => (
              <button
                key={idx}
                onClick={() => setInputText(sample.text)}
                className="text-xs px-3 py-1.5 bg-neutral-100 hover:bg-neutral-200 text-neutral-600 rounded-md transition-colors"
              >
                {sample.title}
              </button>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default LeftPanel;
