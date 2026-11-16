import React, { useEffect, useState } from "react";
import {
  FileText, ShieldCheck, AlertTriangle, AlertOctagon,
  ArrowRight, Upload, Play, CheckCircle2, Clock
} from "lucide-react";
import MetricCard from "../components/MetricCard";
import { getRecentDocuments, getSampleDocs, processSampleDoc, getDocument } from "../services/api";

export default function DashboardPage({ onSelectDoc, onNavigateUpload }) {
  const [recentDocs, setRecentDocs] = useState([]);
  const [samples, setSamples] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [processingSample, setProcessingSample] = useState(null);

  const loadData = async () => {
    try {
      const [docs, sampleList] = await Promise.all([
        getRecentDocuments().catch(() => []),
        getSampleDocs().catch(() => []),
      ]);
      setRecentDocs(docs);
      setSamples(sampleList);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleProcessSample = async (filename) => {
    setProcessingSample(filename);
    try {
      const result = await processSampleDoc(filename);
      await loadData();
      onSelectDoc(result);
    } catch (err) {
      alert("Error processing sample: " + err.message);
    } finally {
      setProcessingSample(null);
    }
  };

  const handleViewDoc = async (docId) => {
    try {
      const doc = await getDocument(docId);
      onSelectDoc(doc.processed_data);
    } catch (err) {
      alert("Failed to load document: " + err.message);
    }
  };

  // Compute aggregate statistics
  const totalDocs = recentDocs.length;
  const autoAcceptCount = recentDocs.filter((d) => d.overall_decision === "AUTO-ACCEPT").length;
  const reviewCount = recentDocs.filter((d) => d.overall_decision === "REVIEW REQUIRED").length;
  const rejectCount = recentDocs.filter((d) => d.overall_decision === "REJECT / INVESTIGATE").length;
  const avgConf = totalDocs > 0
    ? Math.round((recentDocs.reduce((acc, d) => acc + (d.average_confidence || 0), 0) / totalDocs) * 100)
    : 94;

  return (
    <div className="space-y-8 animate-in fade-in">
      {/* Hero Welcome Banner */}
      <div className="glass-panel p-6 sm:p-8 rounded-2xl border border-blue-500/20 bg-gradient-to-r from-blue-950/40 via-gray-900 to-indigo-950/40 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-500/10 text-blue-400 text-xs font-semibold border border-blue-500/20 mb-3">
            <span className="w-2 h-2 rounded-full bg-blue-400 animate-pulse"></span>
            <span>MCA Final-Year Research Project</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            DOCUSURE Intelligent Document Processing
          </h1>
          <p className="text-sm text-gray-300 mt-2 max-w-2xl leading-relaxed">
            Evidence-grounded information extraction, verification engine, confidence calibration, and explainable anomaly detection for invoices, certificates, and forms.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={onNavigateUpload}
            className="px-5 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs sm:text-sm flex items-center space-x-2 shadow-lg shadow-blue-500/25 transition"
          >
            <Upload className="w-4 h-4" />
            <span>Upload Document</span>
          </button>
        </div>
      </div>

      {/* KPI Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Documents"
          value={totalDocs}
          subtitle="Processed in pipeline"
          icon={FileText}
          color="blue"
        />
        <MetricCard
          title="Auto-Accepted"
          value={autoAcceptCount}
          subtitle="Grounded & High Conf"
          icon={ShieldCheck}
          color="emerald"
          badge={`${totalDocs > 0 ? Math.round((autoAcceptCount / totalDocs) * 100) : 0}%`}
        />
        <MetricCard
          title="Review Required"
          value={reviewCount}
          subtitle="Medium Conf or Warnings"
          icon={AlertTriangle}
          color="amber"
        />
        <MetricCard
          title="Suspicious / Flagged"
          value={rejectCount}
          subtitle="Contradictions / Anomalies"
          icon={AlertOctagon}
          color="rose"
        />
      </div>

      {/* 1-Click Interactive Evaluation Documents */}
      <div className="glass-panel p-5 rounded-2xl border border-gray-800">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-sm font-bold text-white tracking-wide uppercase">
              1-Click Benchmark Evaluation Documents
            </h2>
            <p className="text-xs text-gray-400 mt-0.5">
              Launch pre-curated test cases to instantly observe evidence attribution, math anomaly alerts, and verification.
            </p>
          </div>
          <span className="text-[11px] font-mono text-gray-400 bg-gray-900 px-2 py-1 rounded border border-gray-800">
            {samples.length} Benchmark Files
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {samples.map((s) => (
            <div
              key={s.filename}
              className="p-4 rounded-xl border border-gray-800 bg-gray-900/50 hover:border-blue-500/40 hover:bg-gray-900 transition flex flex-col justify-between"
            >
              <div>
                <span className="text-[10px] font-mono uppercase text-blue-400 bg-blue-950/60 px-2 py-0.5 rounded border border-blue-900/50">
                  {s.filename.includes("invoice") ? "INVOICE" : s.filename.includes("cert") ? "CERTIFICATE" : "FORM"}
                </span>
                <h3 className="text-xs font-bold text-white mt-2 truncate" title={s.display_name}>
                  {s.display_name}
                </h3>
                <p className="text-[11px] text-gray-400 mt-1">{s.size_kb} KB • Ready for extraction</p>
              </div>

              <button
                onClick={() => handleProcessSample(s.filename)}
                disabled={processingSample === s.filename}
                className="mt-4 w-full py-2 px-3 rounded-lg bg-gray-800 hover:bg-blue-600 text-gray-200 hover:text-white font-medium text-xs flex items-center justify-center space-x-1.5 transition disabled:opacity-50"
              >
                {processingSample === s.filename ? (
                  <span>Processing...</span>
                ) : (
                  <>
                    <Play className="w-3.5 h-3.5" />
                    <span>Run Pipeline</span>
                  </>
                )}
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Processed Documents Table */}
      <div className="glass-panel rounded-2xl border border-gray-800 overflow-hidden">
        <div className="p-4 border-b border-gray-800 bg-gray-900/60 flex items-center justify-between">
          <h3 className="text-sm font-bold text-white tracking-wide uppercase">
            Recent Processed Documents
          </h3>
          <span className="text-xs text-gray-400">Showing last {recentDocs.length} items</span>
        </div>

        {recentDocs.length === 0 ? (
          <div className="text-center py-12 text-gray-500 text-xs">
            No documents processed yet. Click "Upload Document" or run a benchmark sample above.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-gray-900 text-gray-400 uppercase tracking-wider text-[11px] border-b border-gray-800">
                <tr>
                  <th className="py-3 px-4">Document File</th>
                  <th className="py-3 px-4">Document Type</th>
                  <th className="py-3 px-4">Pages</th>
                  <th className="py-3 px-4">Avg Confidence</th>
                  <th className="py-3 px-4">Decision Status</th>
                  <th className="py-3 px-4">Audited</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60 font-mono">
                {recentDocs.map((doc) => {
                  let badgeStyle = "bg-emerald-950/60 text-emerald-400 border-emerald-800/50";
                  if (doc.overall_decision === "REVIEW REQUIRED") {
                    badgeStyle = "bg-amber-950/60 text-amber-400 border-amber-800/50";
                  } else if (doc.overall_decision === "REJECT / INVESTIGATE") {
                    badgeStyle = "bg-rose-950/60 text-rose-400 border-rose-800/50";
                  }

                  return (
                    <tr
                      key={doc.id}
                      onClick={() => handleViewDoc(doc.id)}
                      className="hover:bg-gray-800/40 cursor-pointer transition"
                    >
                      <td className="py-3 px-4 font-sans font-medium text-white flex items-center space-x-2">
                        <FileText className="w-4 h-4 text-blue-400 flex-shrink-0" />
                        <span className="truncate max-w-[220px]">{doc.filename}</span>
                      </td>

                      <td className="py-3 px-4 text-blue-300 font-semibold">{doc.doc_type}</td>

                      <td className="py-3 px-4 text-gray-400">{doc.page_count}</td>

                      <td className="py-3 px-4 text-gray-200">
                        {Math.round((doc.average_confidence || 0) * 100)}%
                      </td>

                      <td className="py-3 px-4">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${badgeStyle}`}>
                          {doc.overall_decision}
                        </span>
                      </td>

                      <td className="py-3 px-4 font-sans">
                        {doc.is_reviewed ? (
                          <span className="text-emerald-400 flex items-center space-x-1">
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            <span>{doc.reviewer_name || "Reviewed"}</span>
                          </span>
                        ) : (
                          <span className="text-gray-500">Pending</span>
                        )}
                      </td>

                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleViewDoc(doc.id);
                          }}
                          className="px-3 py-1 rounded bg-gray-800 hover:bg-blue-600 text-gray-300 hover:text-white transition font-sans text-xs flex items-center space-x-1 ml-auto"
                        >
                          <span>Inspect</span>
                          <ArrowRight className="w-3 h-3" />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
