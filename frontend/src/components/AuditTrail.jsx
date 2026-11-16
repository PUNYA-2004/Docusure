import React, { useEffect, useState } from "react";
import { History, Shield, User, Clock, Terminal } from "lucide-react";
import { getAuditLogs } from "../services/api";

export default function AuditTrail({ documentId }) {
  const [logs, setLogs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    getAuditLogs(documentId)
      .then((data) => setLogs(data))
      .catch((err) => console.error(err))
      .finally(() => setIsLoading(false));
  }, [documentId]);

  return (
    <div className="glass-panel rounded-xl border border-gray-800 overflow-hidden">
      <div className="p-4 border-b border-gray-800 bg-gray-900/60 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <History className="w-5 h-5 text-indigo-400" />
          <div>
            <h3 className="text-sm font-bold text-white tracking-wide">
              Immutable Document Processing Audit Trail
            </h3>
            <p className="text-xs text-gray-400 mt-0.5">
              Chronological ledger tracking pipeline steps, anomaly alerts, and human operator interventions
            </p>
          </div>
        </div>
        <span className="text-xs font-mono text-gray-400 bg-gray-950 px-2 py-1 rounded border border-gray-800">
          {logs.length} Logged Events
        </span>
      </div>

      <div className="p-4">
        {logs.length === 0 ? (
          <div className="text-center py-8 text-gray-500 text-xs">No audit events recorded yet.</div>
        ) : (
          <div className="relative pl-6 space-y-4 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-gray-800">
            {logs.map((log) => {
              const dateStr = new Date(log.timestamp).toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit",
              });

              let dotColor = "bg-blue-500";
              if (log.action === "ANOMALY_FLAGGED") dotColor = "bg-rose-500";
              else if (log.action === "HUMAN_REVIEW") dotColor = "bg-amber-500";
              else if (log.action === "PIPELINE_COMPLETE") dotColor = "bg-emerald-500";

              return (
                <div key={log.id} className="relative group text-xs">
                  <div
                    className={`absolute -left-6 top-1 w-3 h-3 rounded-full ${dotColor} ring-4 ring-gray-950 transition-transform group-hover:scale-125`}
                  ></div>

                  <div className="glass-panel p-3 rounded-xl border border-gray-800/80 bg-gray-900/40">
                    <div className="flex items-center justify-between text-gray-400 text-[11px] mb-1">
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-white uppercase font-mono tracking-wider">
                          {log.action}
                        </span>
                        <span className="text-gray-600">•</span>
                        <span className="flex items-center text-gray-300">
                          <User className="w-3 h-3 mr-1 text-gray-500" />
                          {log.actor}
                        </span>
                      </div>
                      <span className="font-mono text-gray-500">{dateStr}</span>
                    </div>

                    <pre className="text-[11px] font-mono text-gray-300 bg-gray-950/80 p-2 rounded overflow-x-auto border border-gray-800/60 mt-1.5">
                      {JSON.stringify(log.details, null, 2)}
                    </pre>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
