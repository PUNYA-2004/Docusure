import React, { useState } from "react";
import { Cpu, Play, RefreshCw, CheckCircle2, TrendingUp, Sliders } from "lucide-react";
import { runRobustnessTest } from "../services/api";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from "recharts";

export default function RobustnessLab({ document }) {
  const [degradationType, setDegradationType] = useState("BLUR");
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState(null);

  const degradationOptions = [
    { id: "BLUR", name: "Defocus / Motion Blur", desc: "Simulates unsteady camera capture or lens defocus" },
    { id: "NOISE", name: "Gaussian Sensor Noise", desc: "Simulates low-light sensor grain and thermal noise" },
    { id: "ROTATION", name: "Camera Skew (8.5°)", desc: "Simulates misaligned or hand-held smartphone scan" },
    { id: "JPEG_COMPRESSION", name: "Heavy JPEG Compression (Q=15)", desc: "Simulates high artifacting from messaging apps" },
    { id: "LOW_RESOLUTION", name: "Downsampling (35% Scale)", desc: "Simulates low-DPI thumbnail or faxed document" },
    { id: "CONTRAST_FADED", name: "Faded Thermal Ink / Low Contrast", desc: "Simulates aging receipt paper or weak toner" },
  ];

  const handleRunTest = async () => {
    if (!document) return;
    setIsRunning(true);
    try {
      const data = await runRobustnessTest(document.document_id, degradationType);
      setResults(data);
    } catch (err) {
      alert("Robustness test error: " + err.message);
    } finally {
      setIsRunning(false);
    }
  };

  const chartData = results
    ? [
        {
          metric: "Extraction F1 (%)",
          Clean: Math.round(results.clean_metrics.extraction_f1 * 100),
          Degraded: Math.round(results.degraded_metrics.extraction_f1 * 100),
          Restored: Math.round(results.preprocessed_metrics.extraction_f1 * 100),
        },
        {
          metric: "Verification Acc (%)",
          Clean: Math.round(results.clean_metrics.verification_accuracy * 100),
          Degraded: Math.round(results.degraded_metrics.verification_accuracy * 100),
          Restored: Math.round(results.preprocessed_metrics.verification_accuracy * 100),
        },
        {
          metric: "Avg Confidence (%)",
          Clean: Math.round(results.clean_metrics.average_confidence * 100),
          Degraded: Math.round(results.degraded_metrics.average_confidence * 100),
          Restored: Math.round(results.preprocessed_metrics.average_confidence * 100),
        },
      ]
    : [];

  return (
    <div className="space-y-6">
      {/* Title Banner */}
      <div className="glass-panel p-5 rounded-xl border border-gray-800 flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-2">
            <Cpu className="w-5 h-5 text-indigo-400" />
            <h2 className="text-base font-bold text-white tracking-wide">
              PRATYAKSH-Inspired Document Robustness & Restoration Lab
            </h2>
          </div>
          <p className="text-xs text-gray-400 mt-1">
            Evaluate performance degradation under real-world document corruptions and verify OpenCV restoration gains.
          </p>
        </div>

        <button
          onClick={handleRunTest}
          disabled={isRunning || !document}
          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-xs flex items-center space-x-2 shadow-lg shadow-indigo-500/20 disabled:opacity-50 transition"
        >
          {isRunning ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
          <span>{isRunning ? "Simulating Degradation..." : "Execute 3-Stage Robustness Test"}</span>
        </button>
      </div>

      {/* Degradation Model Selector Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {degradationOptions.map((opt) => (
          <div
            key={opt.id}
            onClick={() => setDegradationType(opt.id)}
            className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
              degradationType === opt.id
                ? "bg-indigo-950/30 border-indigo-500 ring-1 ring-indigo-500/50"
                : "glass-panel border-gray-800 hover:border-gray-700"
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-white">{opt.name}</span>
              {degradationType === opt.id && (
                <span className="w-2 h-2 rounded-full bg-indigo-400"></span>
              )}
            </div>
            <p className="text-[11px] text-gray-400 mt-1">{opt.desc}</p>
          </div>
        ))}
      </div>

      {/* Results View */}
      {results && (
        <div className="space-y-6 animate-in fade-in">
          {/* Recovery Highlight Banner */}
          <div className="glass-panel p-5 rounded-xl border border-indigo-500/30 bg-gradient-to-r from-indigo-950/40 via-blue-950/20 to-purple-950/40 flex items-center justify-between">
            <div>
              <span className="text-[11px] font-semibold text-indigo-400 uppercase tracking-wider">
                Restoration Benchmark Result ({results.degradation_type})
              </span>
              <h3 className="text-2xl font-bold text-white mt-0.5 font-mono">
                {results.recovery_percentage}% Performance Recovery
              </h3>
              <p className="text-xs text-gray-300 mt-1">
                Deskewing, bilateral denoising, and CLAHE contrast equalization recovered {results.recovery_percentage}% of the extraction F1 lost due to corruption.
              </p>
            </div>
            <div className="text-right">
              <span className="text-xs text-gray-400">Character Error Rate (CER)</span>
              <div className="flex items-center space-x-2 mt-1">
                <span className="text-xs font-mono text-rose-400 line-through">
                  {(results.degraded_metrics.char_error_rate * 100).toFixed(1)}%
                </span>
                <span className="text-sm font-mono text-emerald-400 font-bold">
                  {(results.preprocessed_metrics.char_error_rate * 100).toFixed(1)}%
                </span>
              </div>
            </div>
          </div>

          {/* Side-by-Side 3-Phase Metrics Table */}
          <div className="glass-panel rounded-xl border border-gray-800 overflow-hidden">
            <table className="w-full text-left text-xs">
              <thead className="bg-gray-900 text-gray-400 uppercase tracking-wider text-[11px] border-b border-gray-800">
                <tr>
                  <th className="py-3 px-4">Evaluation Phase</th>
                  <th className="py-3 px-4">CER</th>
                  <th className="py-3 px-4">WER</th>
                  <th className="py-3 px-4">Precision</th>
                  <th className="py-3 px-4">Recall</th>
                  <th className="py-3 px-4">Extraction F1</th>
                  <th className="py-3 px-4">Verification Acc</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60 font-mono">
                <tr className="bg-gray-900/30">
                  <td className="py-3 px-4 font-sans font-semibold text-blue-400">
                    Phase 1: Clean Baseline
                  </td>
                  <td className="py-3 px-4">{(results.clean_metrics.char_error_rate * 100).toFixed(1)}%</td>
                  <td className="py-3 px-4">{(results.clean_metrics.word_error_rate * 100).toFixed(1)}%</td>
                  <td className="py-3 px-4">{(results.clean_metrics.extraction_precision * 100).toFixed(1)}%</td>
                  <td className="py-3 px-4">{(results.clean_metrics.extraction_recall * 100).toFixed(1)}%</td>
                  <td className="py-3 px-4 text-emerald-400 font-bold">{(results.clean_metrics.extraction_f1 * 100).toFixed(1)}%</td>
                  <td className="py-3 px-4">{(results.clean_metrics.verification_accuracy * 100).toFixed(1)}%</td>
                </tr>

                <tr className="bg-rose-950/10">
                  <td className="py-3 px-4 font-sans font-semibold text-rose-400">
                    Phase 2: Degraded Document
                  </td>
                  <td className="py-3 px-4 text-rose-400">{(results.degraded_metrics.char_error_rate * 100).toFixed(1)}%</td>
                  <td className="py-3 px-4 text-rose-400">{(results.degraded_metrics.word_error_rate * 100).toFixed(1)}%</td>
                  <td className="py-3 px-4">{(results.degraded_metrics.extraction_precision * 100).toFixed(1)}%</td>
                  <td className="py-3 px-4">{(results.degraded_metrics.extraction_recall * 100).toFixed(1)}%</td>
                  <td className="py-3 px-4 text-rose-400 font-bold">{(results.degraded_metrics.extraction_f1 * 100).toFixed(1)}%</td>
                  <td className="py-3 px-4">{(results.degraded_metrics.verification_accuracy * 100).toFixed(1)}%</td>
                </tr>

                <tr className="bg-emerald-950/10">
                  <td className="py-3 px-4 font-sans font-semibold text-emerald-400">
                    Phase 3: Restored (Preprocessing)
                  </td>
                  <td className="py-3 px-4 text-emerald-400">{(results.preprocessed_metrics.char_error_rate * 100).toFixed(1)}%</td>
                  <td className="py-3 px-4 text-emerald-400">{(results.preprocessed_metrics.word_error_rate * 100).toFixed(1)}%</td>
                  <td className="py-3 px-4">{(results.preprocessed_metrics.extraction_precision * 100).toFixed(1)}%</td>
                  <td className="py-3 px-4">{(results.preprocessed_metrics.extraction_recall * 100).toFixed(1)}%</td>
                  <td className="py-3 px-4 text-emerald-400 font-bold">{(results.preprocessed_metrics.extraction_f1 * 100).toFixed(1)}%</td>
                  <td className="py-3 px-4">{(results.preprocessed_metrics.verification_accuracy * 100).toFixed(1)}%</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Recharts Bar Chart Visualizing Performance Recovery */}
          <div className="glass-panel p-5 rounded-xl border border-gray-800">
            <h4 className="text-xs font-bold text-gray-300 uppercase tracking-wider mb-4">
              Degradation Impact vs Preprocessing Recovery Comparison
            </h4>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                  <XAxis dataKey="metric" stroke="#6b7280" fontSize={11} />
                  <YAxis domain={[0, 100]} stroke="#6b7280" fontSize={11} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#111827", borderColor: "#374151", fontSize: "12px", borderRadius: "8px" }}
                  />
                  <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "10px" }} />
                  <Bar dataKey="Clean" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Clean Baseline" />
                  <Bar dataKey="Degraded" fill="#ef4444" radius={[4, 4, 0, 0]} name="Corrupted Input" />
                  <Bar dataKey="Restored" fill="#10b981" radius={[4, 4, 0, 0]} name="Restored (DOCUSURE)" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
