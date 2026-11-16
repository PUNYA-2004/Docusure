import React, { useState } from "react";
import {
  ShieldCheck, AlertTriangle, AlertOctagon, CheckCircle2,
  FileText, Clock, Edit3, ArrowLeft, RefreshCw
} from "lucide-react";
import DocumentViewer from "../components/DocumentViewer";
import ExtractionTable from "../components/ExtractionTable";
import AnomalyAlerts from "../components/AnomalyAlerts";
import HumanReviewModal from "../components/HumanReviewModal";
import { getDocument } from "../services/api";

export default function DocumentDetailPage({ document, onBack, onUpdateDoc }) {
  const [activeField, setActiveField] = useState(
    document?.fields && document.fields.length > 0 ? document.fields[0] : null
  );
  const [isReviewOpen, setIsReviewOpen] = useState(false);

  if (!document) {
    return <div className="text-gray-500 text-sm">No document selected.</div>;
  }

  const handleReviewSuccess = async () => {
    try {
      const refreshed = await getDocument(document.document_id);
      onUpdateDoc(refreshed.processed_data);
    } catch (err) {
      console.error(err);
    }
  };

  const getDecisionBadge = (decision) => {
    switch (decision) {
      case "AUTO-ACCEPT":
        return {
          bg: "bg-emerald-950/40 text-emerald-400 border-emerald-500/40",
          icon: ShieldCheck,
          text: "AUTO-ACCEPT (High Grounded Confidence)",
        };
      case "REJECT / INVESTIGATE":
        return {
          bg: "bg-rose-950/40 text-rose-400 border-rose-500/40",
          icon: AlertOctagon,
          text: "REJECT / INVESTIGATE (Critical Inconsistency Detected)",
        };
      case "REVIEW REQUIRED":
      default:
        return {
          bg: "bg-amber-950/40 text-amber-400 border-amber-500/40",
          icon: AlertTriangle,
          text: "REVIEW REQUIRED (Human Inspection Recommended)",
        };
    }
  };

  const decBadge = getDecisionBadge(document.overall_decision);
  const DecIcon = decBadge.icon;

  return (
    <div className="space-y-6 animate-in fade-in">
      {/* Top Document Summary Header Bar */}
      <div className="glass-panel p-5 rounded-2xl border border-gray-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <button
            onClick={onBack}
            className="p-2 rounded-lg bg-gray-900 text-gray-400 hover:text-white hover:bg-gray-800 border border-gray-800 transition"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-lg font-bold text-white tracking-wide truncate max-w-[320px]">
                {document.filename}
              </h1>
              <span className="text-xs font-mono px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800">
                {document.document_type}
              </span>
            </div>
            <p className="text-xs text-gray-400 font-mono mt-0.5">
              Doc ID: {document.document_id} • Latency: {document.processing_time_ms} ms • {document.page_count} Page(s)
            </p>
          </div>
        </div>

        {/* Decision Banner & Action */}
        <div className="flex items-center space-x-3 w-full md:w-auto justify-between md:justify-end">
          <div className={`px-3 py-1.5 rounded-xl border flex items-center space-x-2 font-bold text-xs ${decBadge.bg}`}>
            <DecIcon className="w-4 h-4" />
            <span>{decBadge.text}</span>
          </div>

          <button
            onClick={() => setIsReviewOpen(true)}
            className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs flex items-center space-x-1.5 shadow-lg shadow-blue-500/20 transition"
          >
            <Edit3 className="w-3.5 h-3.5" />
            <span>Audit / Review</span>
          </button>
        </div>
      </div>

      {/* Main Split View: Left Document Preview & Right Extraction Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Side: Original Document Viewer & Evidence Highlighting (5 Cols) */}
        <div className="lg:col-span-5 sticky top-20">
          <DocumentViewer document={document} activeField={activeField} />
        </div>

        {/* Right Side: Extraction Table + Anomaly Alerts (7 Cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Anomaly Alerts Section */}
          <AnomalyAlerts
            anomalies={document.anomalies}
            onSelectField={(f) => {
              const matched = document.fields.find((field) => field.field_name === f);
              if (matched) setActiveField(matched);
            }}
          />

          {/* Fields Extraction Table */}
          <ExtractionTable
            document={document}
            activeField={activeField}
            onSelectField={(f) => setActiveField(f)}
            onOpenReview={() => setIsReviewOpen(true)}
          />
        </div>
      </div>

      {/* Human Review Modal */}
      <HumanReviewModal
        isOpen={isReviewOpen}
        onClose={() => setIsReviewOpen(false)}
        document={document}
        onReviewSuccess={handleReviewSuccess}
      />
    </div>
  );
}
