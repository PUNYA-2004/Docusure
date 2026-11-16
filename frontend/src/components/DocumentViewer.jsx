import React, { useState, useRef } from "react";
import { ZoomIn, ZoomOut, RotateCw, Maximize2, ShieldCheck, AlertCircle, Eye } from "lucide-react";
import { getPagePreviewUrl } from "../services/api";

export default function DocumentViewer({ document, activeField }) {
  const [currentPage, setCurrentPage] = useState(1);
  const [zoomLevel, setZoomLevel] = useState(1.0);
  const containerRef = useRef(null);

  if (!document) {
    return (
      <div className="glass-panel rounded-xl p-8 flex flex-col items-center justify-center min-h-[500px] text-gray-500">
        <Eye className="w-12 h-12 mb-3 text-gray-600" />
        <p className="text-sm font-medium">Select or upload a document to view original source evidence</p>
      </div>
    );
  }

  const pageCount = document.page_count || 1;
  const previewUrl = getPagePreviewUrl(document.document_id, currentPage);

  // Evidence bounding box
  const hasEvidence = activeField?.evidence && activeField.evidence.bbox;
  const evidencePage = activeField?.evidence?.page || 1;
  const isEvidenceOnCurrentPage = hasEvidence && evidencePage === currentPage;
  const bbox = activeField?.evidence?.bbox || [0, 0, 0, 0]; // [ymin, xmin, ymax, xmax]

  const topPct = bbox[0] * 100;
  const leftPct = bbox[1] * 100;
  const heightPct = Math.max(2.5, (bbox[2] - bbox[0]) * 100);
  const widthPct = Math.max(4.0, (bbox[3] - bbox[1]) * 100);

  const handleZoom = (delta) => {
    setZoomLevel((prev) => Math.min(2.5, Math.max(0.6, prev + delta)));
  };

  return (
    <div className="glass-panel rounded-xl overflow-hidden border border-gray-800 flex flex-col h-full bg-gray-950">
      {/* Top Controls Bar */}
      <div className="px-4 py-3 border-b border-gray-800 bg-gray-900/60 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <span className="text-xs font-semibold text-gray-300 uppercase tracking-wider">
            Original Document Preview
          </span>
          <span className="text-xs text-blue-400 bg-blue-950/60 border border-blue-800/50 px-2 py-0.5 rounded font-mono">
            {document.document_type}
          </span>
        </div>

        {/* Page Selector & Zoom */}
        <div className="flex items-center space-x-2">
          {pageCount > 1 && (
            <div className="flex items-center space-x-1 bg-gray-800 px-2 py-1 rounded text-xs text-gray-300 mr-2">
              <span>Page</span>
              <select
                value={currentPage}
                onChange={(e) => setCurrentPage(Number(e.target.value))}
                className="bg-transparent text-white font-mono outline-none"
              >
                {Array.from({ length: pageCount }, (_, i) => (
                  <option key={i + 1} value={i + 1} className="bg-gray-900 text-white">
                    {i + 1}
                  </option>
                ))}
              </select>
              <span>of {pageCount}</span>
            </div>
          )}

          <div className="flex items-center space-x-1 bg-gray-800/80 rounded-lg p-0.5 border border-gray-700">
            <button
              onClick={() => handleZoom(-0.15)}
              className="p-1.5 text-gray-400 hover:text-white rounded hover:bg-gray-700 transition"
              title="Zoom Out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <span className="text-[11px] font-mono text-gray-300 px-1.5">{Math.round(zoomLevel * 100)}%</span>
            <button
              onClick={() => handleZoom(0.15)}
              className="p-1.5 text-gray-400 hover:text-white rounded hover:bg-gray-700 transition"
              title="Zoom In"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setZoomLevel(1.0)}
              className="p-1.5 text-gray-400 hover:text-white rounded hover:bg-gray-700 transition text-[11px]"
              title="Reset Zoom"
            >
              1:1
            </button>
          </div>
        </div>
      </div>

      {/* Active Field Attribution Callout Banner */}
      {activeField && (
        <div className="bg-blue-950/40 border-b border-blue-900/40 px-4 py-2 flex items-center justify-between text-xs">
          <div className="flex items-center space-x-2">
            <span className="font-semibold text-blue-400">{activeField.display_name}:</span>
            <span className="font-mono text-white bg-blue-900/40 px-2 py-0.5 rounded border border-blue-700/50">
              {activeField.value}
            </span>
          </div>
          <div className="flex items-center space-x-3 text-gray-400">
            {hasEvidence ? (
              <span className="flex items-center text-emerald-400">
                <ShieldCheck className="w-3.5 h-3.5 mr-1" />
                Evidence Grounded on Page {evidencePage} ({Math.round((activeField.evidence.matched_score || 1) * 100)}% Alignment)
              </span>
            ) : (
              <span className="flex items-center text-amber-400">
                <AlertCircle className="w-3.5 h-3.5 mr-1" />
                No physical evidence grounded (Hallucination Prevented)
              </span>
            )}
          </div>
        </div>
      )}

      {/* Image & Canvas Display Area */}
      <div
        ref={containerRef}
        className="flex-1 overflow-auto p-4 flex items-center justify-center bg-gray-900/40 relative min-h-[550px]"
      >
        <div
          className="relative inline-block transition-transform duration-150 origin-top shadow-2xl border border-gray-700/60 rounded"
          style={{ transform: `scale(${zoomLevel})` }}
        >
          {/* Base Document Image */}
          <img
            src={previewUrl}
            alt={`Document Page ${currentPage}`}
            className="max-w-[720px] w-full h-auto block rounded select-none pointer-events-none"
            onError={(e) => {
              e.target.onerror = null;
              e.target.src = "https://placehold.co/600x800/1e293b/94a3b8?text=Document+Preview+Rendering";
            }}
          />

          {/* VERITAS Evidence Attribution Bounding Box Overlay */}
          {isEvidenceOnCurrentPage && (
            <div
              className="absolute pointer-events-none transition-all duration-300 animate-pulse"
              style={{
                top: `${topPct}%`,
                left: `${leftPct}%`,
                width: `${widthPct}%`,
                height: `${heightPct}%`,
                border: "2px solid #06b6d4",
                backgroundColor: "rgba(6, 182, 212, 0.22)",
                boxShadow: "0 0 25px rgba(6, 182, 212, 0.6)",
                borderRadius: "4px",
              }}
            >
              {/* Evidence Tag */}
              <div className="absolute -top-7 left-0 bg-cyan-500 text-gray-950 font-bold text-[10px] px-2 py-0.5 rounded shadow-lg flex items-center space-x-1 whitespace-nowrap">
                <span>EVIDENCE: {activeField.display_name}</span>
                <span className="bg-gray-950 text-cyan-400 px-1 rounded text-[9px] font-mono">
                  {Math.round(activeField.confidence * 100)}%
                </span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Evidence Source Snippet Footer */}
      {activeField?.evidence?.source_text && (
        <div className="p-3 bg-gray-900 border-t border-gray-800 text-xs">
          <span className="text-gray-400 font-medium">Source Text Snippet: </span>
          <span className="font-mono text-cyan-300 bg-gray-950 px-2 py-0.5 rounded border border-gray-800">
            "{activeField.evidence.source_text}"
          </span>
        </div>
      )}
    </div>
  );
}
