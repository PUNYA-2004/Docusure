import React from "react";
import AuditTrail from "../components/AuditTrail";

export default function AuditPage({ currentDoc }) {
  return (
    <div className="space-y-6 animate-in fade-in">
      <div className="glass-panel p-5 rounded-xl border border-gray-800">
        <h2 className="text-base font-bold text-white tracking-wide">
          Enterprise Security & Audit Trail
        </h2>
        <p className="text-xs text-gray-400 mt-1">
          Review tamper-evident transaction logs capturing document processing events, automated anomaly detections, and human operator edits.
        </p>
      </div>

      <AuditTrail documentId={currentDoc?.document_id || null} />
    </div>
  );
}
