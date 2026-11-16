import React from "react";
import { CheckCircle2, XCircle, AlertTriangle, HelpCircle, Eye, Calculator } from "lucide-react";

export default function ExtractionTable({ document, activeField, onSelectField, onOpenReview }) {
  if (!document || !document.fields) {
    return <div className="text-gray-500 text-sm">No extraction data available.</div>;
  }

  const getStatusBadge = (status) => {
    switch (status) {
      case "SUPPORTED":
        return (
          <span className="badge-supported inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold">
            <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
            SUPPORTED
          </span>
        );
      case "CONTRADICTED":
        return (
          <span className="badge-contradicted inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold">
            <XCircle className="w-3.5 h-3.5 mr-1" />
            CONTRADICTED
          </span>
        );
      case "UNSUPPORTED":
        return (
          <span className="badge-unsupported inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold">
            <XCircle className="w-3.5 h-3.5 mr-1" />
            UNSUPPORTED
          </span>
        );
      case "UNCERTAIN":
      default:
        return (
          <span className="badge-uncertain inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold">
            <AlertTriangle className="w-3.5 h-3.5 mr-1" />
            UNCERTAIN
          </span>
        );
    }
  };

  const getConfidenceBar = (conf) => {
    const pct = Math.round(conf * 100);
    let colorClass = "bg-emerald-500";
    if (pct < 70) colorClass = "bg-rose-500";
    else if (pct < 90) colorClass = "bg-amber-500";

    return (
      <div className="flex items-center space-x-2">
        <div className="w-16 bg-gray-800 h-2 rounded-full overflow-hidden">
          <div className={`${colorClass} h-full transition-all`} style={{ width: `${pct}%` }}></div>
        </div>
        <span className="text-xs font-mono text-gray-300">{pct}%</span>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Extracted Fields Card */}
      <div className="glass-panel rounded-xl border border-gray-800 overflow-hidden">
        <div className="p-4 border-b border-gray-800 bg-gray-900/60 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-white tracking-wide">
              Schema Information Extraction & Evidence Attribution
            </h3>
            <p className="text-xs text-gray-400 mt-0.5">
              Click any field row to localize physical evidence in the document viewer
            </p>
          </div>
          <button
            onClick={onOpenReview}
            className="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium transition shadow-sm shadow-blue-500/20"
          >
            Human Review / Edit
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-gray-900/90 text-gray-400 uppercase tracking-wider text-[11px] border-b border-gray-800">
              <tr>
                <th className="py-3 px-4">Field Name</th>
                <th className="py-3 px-4">Extracted Value</th>
                <th className="py-3 px-4">Confidence</th>
                <th className="py-3 px-4">Verification Status</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60">
              {document.fields.map((field) => {
                const isSelected = activeField?.field_name === field.field_name;
                return (
                  <tr
                    key={field.field_name}
                    onClick={() => onSelectField(field)}
                    className={`cursor-pointer transition-colors ${
                      isSelected
                        ? "bg-blue-600/15 border-l-4 border-blue-500"
                        : "hover:bg-gray-800/40"
                    }`}
                  >
                    <td className="py-3 px-4 font-medium text-gray-200">
                      <div>{field.display_name}</div>
                      {field.is_edited && (
                        <span className="text-[10px] text-amber-400 font-mono">(Edited by reviewer)</span>
                      )}
                    </td>

                    <td className="py-3 px-4 font-mono font-medium">
                      <span
                        className={
                          field.value === "NOT_FOUND"
                            ? "text-gray-500 italic"
                            : "text-white bg-gray-900 px-2 py-0.5 rounded border border-gray-800"
                        }
                      >
                        {field.value}
                      </span>
                    </td>

                    <td className="py-3 px-4">{getConfidenceBar(field.confidence)}</td>

                    <td className="py-3 px-4">
                      <div>{getStatusBadge(field.status)}</div>
                      <div className="text-[10px] text-gray-400 mt-1 max-w-[240px] truncate" title={field.verification_reason}>
                        {field.verification_reason}
                      </div>
                    </td>

                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectField(field);
                        }}
                        className={`px-2.5 py-1 rounded text-xs font-medium flex items-center space-x-1 ml-auto transition ${
                          isSelected
                            ? "bg-cyan-500 text-gray-950 font-bold"
                            : "bg-gray-800 text-gray-300 hover:text-white hover:bg-gray-700"
                        }`}
                      >
                        <Eye className="w-3 h-3" />
                        <span>Evidence</span>
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Table Line Items (for Invoices) */}
      {document.line_items && document.line_items.length > 0 && (
        <div className="glass-panel rounded-xl border border-gray-800 overflow-hidden">
          <div className="p-4 border-b border-gray-800 bg-gray-900/60 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Calculator className="w-4 h-4 text-indigo-400" />
              <h3 className="text-sm font-bold text-white tracking-wide">
                Table Line-Items & Arithmetic Verification
              </h3>
            </div>
            <span className="text-xs text-gray-400">
              Formula: Quantity × Unit Price = Computed Total
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-gray-900/90 text-gray-400 uppercase tracking-wider text-[11px] border-b border-gray-800">
                <tr>
                  <th className="py-3 px-4">#</th>
                  <th className="py-3 px-4">Description</th>
                  <th className="py-3 px-4 text-center">Qty</th>
                  <th className="py-3 px-4 text-right">Unit Price</th>
                  <th className="py-3 px-4 text-right">Extracted Total</th>
                  <th className="py-3 px-4 text-right">Computed Total</th>
                  <th className="py-3 px-4 text-center">Math Match</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60">
                {document.line_items.map((item) => (
                  <tr key={item.item_id} className="hover:bg-gray-800/30">
                    <td className="py-2.5 px-4 font-mono text-gray-500">{item.item_id}</td>
                    <td className="py-2.5 px-4 font-medium text-gray-200">{item.description}</td>
                    <td className="py-2.5 px-4 text-center font-mono text-gray-300">{item.quantity}</td>
                    <td className="py-2.5 px-4 text-right font-mono text-gray-300">
                      ₹{item.unit_price.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                    </td>
                    <td className="py-2.5 px-4 text-right font-mono font-semibold text-white">
                      ₹{item.line_total.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                    </td>
                    <td className="py-2.5 px-4 text-right font-mono text-blue-400">
                      ₹{item.computed_total.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                    </td>
                    <td className="py-2.5 px-4 text-center">
                      {item.is_match ? (
                        <span className="inline-flex items-center text-emerald-400 font-semibold text-xs">
                          <CheckCircle2 className="w-4 h-4 mr-1" />
                          VERIFIED
                        </span>
                      ) : (
                        <span className="inline-flex items-center text-rose-400 font-semibold text-xs" title={`Discrepancy: ₹${item.discrepancy}`}>
                          <XCircle className="w-4 h-4 mr-1" />
                          ERROR (₹{item.discrepancy})
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
