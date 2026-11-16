import React from "react";
import { AlertOctagon, AlertTriangle, Info, CheckCircle2 } from "lucide-react";

export default function AnomalyAlerts({ anomalies, onSelectField }) {
  if (!anomalies || anomalies.length === 0) {
    return (
      <div className="glass-panel p-4 rounded-xl border border-emerald-500/20 bg-emerald-950/20 flex items-center space-x-3">
        <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0" />
        <div>
          <h4 className="text-xs font-semibold text-emerald-300">Document Consistency Verified</h4>
          <p className="text-xs text-gray-400 mt-0.5">
            No arithmetic discrepancies, missing mandatory schemas, or temporal contradictions detected.
          </p>
        </div>
      </div>
    );
  }

  const getSeverityStyle = (sev) => {
    switch (sev) {
      case "CRITICAL":
        return {
          border: "border-rose-500/30",
          bg: "bg-rose-950/20",
          badge: "bg-rose-500/20 text-rose-400 border-rose-500/30",
          icon: AlertOctagon,
          iconColor: "text-rose-400",
        };
      case "WARNING":
        return {
          border: "border-amber-500/30",
          bg: "bg-amber-950/20",
          badge: "bg-amber-500/20 text-amber-400 border-amber-500/30",
          icon: AlertTriangle,
          iconColor: "text-amber-400",
        };
      default:
        return {
          border: "border-blue-500/30",
          bg: "bg-blue-950/20",
          badge: "bg-blue-500/20 text-blue-400 border-blue-500/30",
          icon: Info,
          iconColor: "text-blue-400",
        };
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-bold uppercase tracking-wider text-gray-300 flex items-center space-x-2">
          <span>Detected Document Anomalies</span>
          <span className="bg-rose-500/20 text-rose-400 border border-rose-500/30 px-1.5 py-0.2 rounded font-mono text-[11px]">
            {anomalies.length}
          </span>
        </h3>
        <span className="text-[11px] text-gray-500 font-mono">SENTINEL-XAI Engine</span>
      </div>

      <div className="space-y-2.5">
        {anomalies.map((ano) => {
          const style = getSeverityStyle(ano.severity);
          const Icon = style.icon;

          return (
            <div
              key={ano.anomaly_id}
              className={`p-3.5 rounded-xl border ${style.border} ${style.bg} transition-all`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-2.5">
                  <Icon className={`w-4 h-4 mt-0.5 ${style.iconColor} flex-shrink-0`} />
                  <div>
                    <div className="flex items-center space-x-2">
                      <h4 className="text-xs font-semibold text-white">{ano.title}</h4>
                      <span className={`text-[10px] font-bold px-1.5 py-0.2 rounded border font-mono ${style.badge}`}>
                        {ano.severity}
                      </span>
                    </div>

                    {/* Plain language explanation */}
                    <p className="text-xs text-gray-300 mt-1 leading-relaxed">
                      {ano.reason}
                    </p>

                    {/* Discrepancy comparison pills */}
                    {(ano.extracted_value || ano.calculated_or_expected) && (
                      <div className="flex items-center space-x-3 mt-2 text-[11px]">
                        {ano.extracted_value && (
                          <div className="bg-gray-900 px-2 py-0.5 rounded border border-gray-800">
                            <span className="text-gray-500">Extracted: </span>
                            <span className="font-mono text-rose-400 font-semibold">{ano.extracted_value}</span>
                          </div>
                        )}
                        {ano.calculated_or_expected && (
                          <div className="bg-gray-900 px-2 py-0.5 rounded border border-gray-800">
                            <span className="text-gray-500">Expected: </span>
                            <span className="font-mono text-emerald-400 font-semibold">{ano.calculated_or_expected}</span>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Recommended action */}
                    <div className="mt-2 text-[11px] text-amber-300/80 font-medium flex items-center space-x-1">
                      <span>Action: </span>
                      <span>{ano.recommended_action}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
