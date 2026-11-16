import React, { useState, useRef } from "react";
import { UploadCloud, FileText, CheckCircle2, Loader2, ArrowRight, ShieldCheck } from "lucide-react";
import { uploadDocument } from "../services/api";

export default function UploadProcessPage({ onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [docType, setDocType] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const pipelineSteps = [
    { title: "Document Ingestion", desc: "Parsing PDF binary stream & generating high-res page previews" },
    { title: "Computer Vision & OCR", desc: "Extracting word tokens, character spans, and spatial bounding boxes" },
    { title: "Document Classification", desc: "Determining document category & matching Pydantic schema rules" },
    { title: "Structured Information Extraction", desc: "Extracting key-value fields and tabular line items" },
    { title: "VERITAS Evidence Attribution", desc: "Grounding extracted fields to exact page coordinates" },
    { title: "Extraction Verification", desc: "Checking support, contradiction, and hallucination prevention" },
    { title: "SENTINEL Anomaly Detection", desc: "Running arithmetic consistency, date logic, and missing field checks" },
  ];

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") setDragActive(true);
    else if (e.type === "dragleave") setDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setIsProcessing(true);
    setCurrentStep(0);

    // Progressive step animation
    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev < pipelineSteps.length - 1 ? prev + 1 : prev));
    }, 450);

    try {
      const result = await uploadDocument(file, docType || null);
      clearInterval(interval);
      setCurrentStep(pipelineSteps.length);
      setTimeout(() => {
        onUploadSuccess(result);
      }, 500);
    } catch (err) {
      clearInterval(interval);
      alert("Error: " + err.message);
      setIsProcessing(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in">
      <div className="text-center space-y-2">
        <h1 className="text-2xl font-extrabold text-white tracking-tight">
          Upload & Ingest Document
        </h1>
        <p className="text-xs text-gray-400 max-w-lg mx-auto">
          Upload any PDF, invoice scan, degree certificate, or application form to initiate evidence attribution and verification.
        </p>
      </div>

      {!isProcessing ? (
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Drag & Drop Area */}
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all ${
              dragActive
                ? "border-blue-500 bg-blue-950/20"
                : file
                ? "border-emerald-500/60 bg-emerald-950/10"
                : "border-gray-800 hover:border-gray-700 bg-gray-950/50"
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.png,.jpg,.jpeg,.tiff"
              onChange={handleFileChange}
              className="hidden"
            />

            <div className="flex flex-col items-center justify-center space-y-3">
              <div className="w-14 h-14 rounded-2xl bg-blue-600/10 border border-blue-500/20 flex items-center justify-center text-blue-400 shadow-lg shadow-blue-500/10">
                <UploadCloud className="w-7 h-7" />
              </div>

              {file ? (
                <div>
                  <p className="text-sm font-bold text-white font-mono">{file.name}</p>
                  <p className="text-xs text-emerald-400 mt-1">
                    Ready to process • {(file.size / 1024).toFixed(1)} KB
                  </p>
                </div>
              ) : (
                <div>
                  <p className="text-sm font-semibold text-white">
                    Drop your document here, or <span className="text-blue-400">browse files</span>
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    Supports PDF, PNG, JPG, JPEG, TIFF (scanned or native digital)
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Optional Document Type Pre-Selection */}
          <div className="glass-panel p-5 rounded-xl border border-gray-800 space-y-3">
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-300">
              Document Type Schema (Optional)
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              {[
                { id: "", label: "Auto-Detect (AI Classification)" },
                { id: "INVOICE", label: "Commercial Invoice" },
                { id: "CERTIFICATE", label: "Academic Certificate" },
                { id: "APPLICATION_FORM", label: "Application Form" },
              ].map((opt) => (
                <button
                  type="button"
                  key={opt.id}
                  onClick={() => setDocType(opt.id)}
                  className={`py-2 px-3 rounded-lg border text-left font-medium transition ${
                    docType === opt.id
                      ? "bg-blue-600/20 border-blue-500 text-blue-300 shadow-sm"
                      : "bg-gray-950 border-gray-800 text-gray-400 hover:border-gray-700"
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={!file}
            className="w-full py-3.5 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white font-bold text-sm shadow-xl shadow-blue-500/25 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            <span>Run DOCUSURE Processing Pipeline</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>
      ) : (
        /* Real-Time Processing Animation */
        <div className="glass-panel p-8 rounded-2xl border border-gray-800 space-y-6">
          <div className="text-center space-y-1">
            <h2 className="text-base font-bold text-white tracking-wide">
              Document Processing Pipeline in Execution
            </h2>
            <p className="text-xs text-gray-400 font-mono">Document: {file?.name}</p>
          </div>

          <div className="space-y-3">
            {pipelineSteps.map((step, idx) => {
              const isDone = currentStep > idx;
              const isActive = currentStep === idx;

              return (
                <div
                  key={idx}
                  className={`p-3.5 rounded-xl border flex items-center justify-between transition-all ${
                    isActive
                      ? "bg-blue-950/30 border-blue-500 text-white ring-1 ring-blue-500/40"
                      : isDone
                      ? "bg-emerald-950/15 border-emerald-800/40 text-gray-300"
                      : "bg-gray-950/50 border-gray-800/40 text-gray-600"
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <div className="flex-shrink-0">
                      {isDone ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      ) : isActive ? (
                        <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
                      ) : (
                        <span className="w-4 h-4 rounded-full border border-gray-700 flex items-center justify-center text-[10px] font-mono text-gray-500">
                          {idx + 1}
                        </span>
                      )}
                    </div>
                    <div>
                      <p className="text-xs font-semibold">{step.title}</p>
                      <p className="text-[11px] text-gray-400 mt-0.5">{step.desc}</p>
                    </div>
                  </div>
                  {isDone && <span className="text-[10px] font-mono text-emerald-400 font-bold uppercase">Done</span>}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
