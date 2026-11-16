import React, { useState } from "react";
import { X, Check, AlertOctagon, Edit3, ShieldAlert } from "lucide-react";
import { submitReview } from "../services/api";

export default function HumanReviewModal({ isOpen, onClose, document, onReviewSuccess }) {
  if (!isOpen || !document) return null;

  const [reviewerName, setReviewerName] = useState("Lead Quality Auditor");
  const [notes, setNotes] = useState("");
  const [decision, setDecision] = useState(
    document.overall_decision === "AUTO-ACCEPT" ? "ACCEPTED" : "MODIFIED"
  );
  const [corrections, setCorrections] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleFieldChange = (fieldName, newVal) => {
    setCorrections((prev) => ({
      ...prev,
      [fieldName]: newVal,
    }));
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      await submitReview(document.document_id, {
        document_id: document.document_id,
        decision: decision,
        reviewer_name: reviewerName,
        notes: notes,
        field_corrections: corrections,
      });
      onReviewSuccess();
      onClose();
    } catch (err) {
      alert("Failed to submit review: " + err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-950/80 backdrop-blur-md">
      <div className="glass-panel w-full max-w-2xl rounded-2xl border border-gray-700 bg-gray-900 shadow-2xl flex flex-col max-h-[90vh] overflow-hidden animate-in fade-in zoom-in-95">
        {/* Header */}
        <div className="p-4 border-b border-gray-800 flex items-center justify-between bg-gray-950/60">
          <div className="flex items-center space-x-2">
            <Edit3 className="w-5 h-5 text-blue-400" />
            <h3 className="text-base font-bold text-white">Human-in-the-Loop Quality Review</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 transition"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-5 overflow-y-auto space-y-4 text-xs">
          {/* Metadata banner */}
          <div className="flex items-center justify-between p-3 rounded-lg bg-gray-950 border border-gray-800">
            <div>
              <span className="text-gray-400">Document: </span>
              <span className="font-mono text-white font-semibold">{document.filename}</span>
            </div>
            <div>
              <span className="text-gray-400">Current Decision: </span>
              <span className="font-mono text-amber-400 font-bold">{document.overall_decision}</span>
            </div>
          </div>

          {/* Reviewer Name */}
          <div>
            <label className="block text-gray-400 font-medium mb-1">Reviewer Name / ID</label>
            <input
              type="text"
              value={reviewerName}
              onChange={(e) => setReviewerName(e.target.value)}
              className="w-full bg-gray-950 border border-gray-800 rounded-lg px-3 py-2 text-white font-mono outline-none focus:border-blue-500"
            />
          </div>

          {/* Decision Selection */}
          <div>
            <label className="block text-gray-400 font-medium mb-1.5">Audit Decision</label>
            <div className="grid grid-cols-3 gap-3">
              <button
                type="button"
                onClick={() => setDecision("ACCEPTED")}
                className={`py-2 px-3 rounded-xl border flex items-center justify-center space-x-2 font-medium transition ${
                  decision === "ACCEPTED"
                    ? "bg-emerald-600/20 border-emerald-500 text-emerald-400"
                    : "bg-gray-950 border-gray-800 text-gray-400 hover:border-gray-700"
                }`}
              >
                <Check className="w-4 h-4" />
                <span>ACCEPT</span>
              </button>

              <button
                type="button"
                onClick={() => setDecision("MODIFIED")}
                className={`py-2 px-3 rounded-xl border flex items-center justify-center space-x-2 font-medium transition ${
                  decision === "MODIFIED"
                    ? "bg-amber-600/20 border-amber-500 text-amber-400"
                    : "bg-gray-950 border-gray-800 text-gray-400 hover:border-gray-700"
                }`}
              >
                <Edit3 className="w-4 h-4" />
                <span>CORRECT & SAVE</span>
              </button>

              <button
                type="button"
                onClick={() => setDecision("REJECTED")}
                className={`py-2 px-3 rounded-xl border flex items-center justify-center space-x-2 font-medium transition ${
                  decision === "REJECTED"
                    ? "bg-rose-600/20 border-rose-500 text-rose-400"
                    : "bg-gray-950 border-gray-800 text-gray-400 hover:border-gray-700"
                }`}
              >
                <AlertOctagon className="w-4 h-4" />
                <span>REJECT</span>
              </button>
            </div>
          </div>

          {/* Editable Fields Table */}
          <div>
            <label className="block text-gray-400 font-medium mb-1.5">
              Extracted Fields & Manual Overrides
            </label>
            <div className="space-y-2 max-h-[220px] overflow-y-auto pr-1">
              {document.fields.map((f) => {
                const currentVal = corrections[f.field_name] !== undefined ? corrections[f.field_name] : f.value;
                const isModified = corrections[f.field_name] !== undefined && corrections[f.field_name] !== f.value;

                return (
                  <div
                    key={f.field_name}
                    className="flex items-center justify-between p-2 rounded-lg bg-gray-950 border border-gray-800"
                  >
                    <div className="w-1/3">
                      <p className="font-medium text-gray-300">{f.display_name}</p>
                      <p className="text-[10px] text-gray-500 font-mono">
                        {Math.round(f.confidence * 100)}% conf • {f.status}
                      </p>
                    </div>

                    <div className="w-2/3 flex items-center space-x-2">
                      <input
                        type="text"
                        value={currentVal}
                        onChange={(e) => handleFieldChange(f.field_name, e.target.value)}
                        className={`w-full bg-gray-900 border rounded px-2.5 py-1 text-white font-mono outline-none text-xs ${
                          isModified ? "border-amber-500 bg-amber-950/20" : "border-gray-800"
                        }`}
                      />
                      {isModified && (
                        <span className="text-[10px] text-amber-400 font-semibold uppercase">Edited</span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Audit Notes */}
          <div>
            <label className="block text-gray-400 font-medium mb-1">Auditor Notes & Justification</label>
            <textarea
              rows={2}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="e.g. Verified vendor registration on official state portal; corrected OCR smudge on tax code."
              className="w-full bg-gray-950 border border-gray-800 rounded-lg p-2.5 text-white outline-none focus:border-blue-500 resize-none font-mono text-xs"
            />
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-800 bg-gray-950/60 flex items-center justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-gray-800 text-gray-300 hover:text-white transition text-xs font-medium"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={isSubmitting}
            className="px-5 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold transition text-xs shadow-lg shadow-blue-500/20 disabled:opacity-50"
          >
            {isSubmitting ? "Committing Audit Log..." : "Commit Review Decision"}
          </button>
        </div>
      </div>
    </div>
  );
}
