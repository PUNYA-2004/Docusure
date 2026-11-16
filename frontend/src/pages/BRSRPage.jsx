import React, { useState, useEffect } from "react";
import {
  FileText,
  Search,
  Filter,
  Download,
  UploadCloud,
  Globe,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  XCircle,
  ExternalLink,
  ChevronRight,
  Eye,
  RefreshCw,
  Edit3,
  Layers,
  Leaf,
  Users,
  ShieldAlert,
  ArrowRight,
  Database,
  BarChart2,
  FileSpreadsheet,
  Info
} from "lucide-react";
import {
  getBrsrReports,
  getBrsrReport,
  getBrsrObservations,
  getBrsrStats,
  processBrsrReport,
  uploadBrsrReport,
  importBrsrFromUrl,
  reviewBrsrObservation,
  getBrsrExportUrl,
  getBrsrPrinciplesSummary,
  getBrsrPagePreviewUrl
} from "../services/api";

export default function BRSRPage() {
  const [activeSubTab, setActiveSubTab] = useState("repository");
  const [reports, setReports] = useState([]);
  const [selectedReportId, setSelectedReportId] = useState("");
  const [selectedReport, setSelectedReport] = useState(null);
  const [observations, setObservations] = useState([]);
  const [principlesSummary, setPrinciplesSummary] = useState({});
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [processingId, setProcessingId] = useState(null);
  const [notification, setNotification] = useState(null);

  // Filters
  const [searchQuery, setSearchQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("ALL");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [companyFilter, setCompanyFilter] = useState("");

  // Modals & Panels
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showImportUrlModal, setShowImportUrlModal] = useState(false);
  const [reviewingObs, setReviewingObs] = useState(null);
  const [selectedPageNum, setSelectedPageNum] = useState(1);
  const [activeParserTab, setActiveParserTab] = useState("sections");

  // Form states
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadCompany, setUploadCompany] = useState("");
  const [uploadYear, setUploadYear] = useState("2023-24");
  const [uploadIndustry, setUploadIndustry] = useState("Diversified");
  const [importUrl, setImportUrl] = useState("");
  const [importCompany, setImportCompany] = useState("");
  const [importYear, setImportYear] = useState("2023-24");
  const [importIndustry, setImportIndustry] = useState("Diversified");

  // Edit form state
  const [editValue, setEditValue] = useState("");
  const [editNotes, setEditNotes] = useState("");
  const [reviewerName, setReviewerName] = useState("MCA Auditor");

  useEffect(() => {
    loadReports();
    loadStats();
    loadObservations();
    loadPrinciples();
  }, []);

  useEffect(() => {
    if (selectedReportId) {
      loadReportDetails(selectedReportId);
    }
  }, [selectedReportId]);

  const showToast = (message, type = "success") => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 4500);
  };

  const loadReports = async () => {
    try {
      setLoading(true);
      const data = await getBrsrReports();
      setReports(data);
      if (data.length > 0 && !selectedReportId) {
        setSelectedReportId(data[0].report_id);
      }
    } catch (err) {
      showToast(`Failed to load reports: ${err.message}`, "error");
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const data = await getBrsrStats();
      setStats(data);
    } catch (err) {
      console.error(err);
    }
  };

  const loadObservations = async () => {
    try {
      const data = await getBrsrObservations();
      setObservations(data);
    } catch (err) {
      console.error(err);
    }
  };

  const loadPrinciples = async () => {
    try {
      const data = await getBrsrPrinciplesSummary();
      setPrinciplesSummary(data);
    } catch (err) {
      console.error(err);
    }
  };

  const loadReportDetails = async (id) => {
    try {
      const data = await getBrsrReport(id);
      setSelectedReport(data);
      setSelectedPageNum(1);
    } catch (err) {
      showToast(`Failed to load report details: ${err.message}`, "error");
    }
  };

  const handleProcess = async (reportId) => {
    try {
      setProcessingId(reportId);
      const res = await processBrsrReport(reportId);
      showToast(`Parsed & Extracted ${res.total_indicators_extracted} ESG metrics in ${res.processing_time_ms}ms!`, "success");
      await loadReports();
      await loadStats();
      await loadObservations();
      await loadPrinciples();
      if (selectedReportId === reportId) {
        await loadReportDetails(reportId);
      }
    } catch (err) {
      showToast(`Processing failed: ${err.message}`, "error");
    } finally {
      setProcessingId(null);
    }
  };

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!uploadFile || !uploadCompany) {
      showToast("Please select a PDF file and specify company name.", "error");
      return;
    }
    try {
      setLoading(true);
      const res = await uploadBrsrReport(uploadFile, uploadCompany, uploadYear, uploadIndustry);
      showToast(res.message, res.is_duplicate ? "info" : "success");
      setShowUploadModal(false);
      setUploadFile(null);
      setUploadCompany("");
      await loadReports();
      await loadStats();
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      setLoading(false);
    }
  };

  const handleImportUrlSubmit = async (e) => {
    e.preventDefault();
    if (!importUrl || !importCompany) {
      showToast("Please enter a valid PDF URL and company name.", "error");
      return;
    }
    try {
      setLoading(true);
      const res = await importBrsrFromUrl(importUrl, importCompany, importYear, importIndustry);
      showToast(res.message, res.is_duplicate ? "info" : "success");
      setShowImportUrlModal(false);
      setImportUrl("");
      setImportCompany("");
      await loadReports();
      await loadStats();
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      setLoading(false);
    }
  };

  const handleReviewSubmit = async (e) => {
    e.preventDefault();
    if (!reviewingObs) return;
    try {
      setLoading(true);
      await reviewBrsrObservation(reviewingObs.observation_id, {
        observation_id: reviewingObs.observation_id,
        corrected_value: editValue,
        corrected_numeric_value: parseFloat(editValue) || null,
        reviewer_notes: editNotes || "Manually verified by MCA auditor",
        reviewer_name: reviewerName
      });
      showToast(`Observation '${reviewingObs.indicator_name}' updated successfully!`, "success");
      setReviewingObs(null);
      await loadObservations();
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      setLoading(false);
    }
  };

  // Filtered observations
  const filteredObservations = observations.filter((obs) => {
    const matchesSearch =
      !searchQuery ||
      obs.indicator_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      obs.indicator_code.toLowerCase().includes(searchQuery.toLowerCase()) ||
      obs.company_name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCat = categoryFilter === "ALL" || obs.esg_category === categoryFilter;
    const matchesStatus = statusFilter === "ALL" || obs.extraction_status === statusFilter;
    const matchesCompany = !companyFilter || obs.company_name === companyFilter;
    return matchesSearch && matchesCat && matchesStatus && matchesCompany;
  });

  return (
    <div className="space-y-6 pb-12">
      {/* Toast Notification */}
      {notification && (
        <div
          className={`fixed top-20 right-8 z-50 px-4 py-3 rounded-xl border shadow-xl flex items-center space-x-3 text-sm transition-all animate-bounce ${
            notification.type === "error"
              ? "bg-red-950/90 text-red-200 border-red-800"
              : notification.type === "info"
              ? "bg-cyan-950/90 text-cyan-200 border-cyan-800"
              : "bg-emerald-950/90 text-emerald-200 border-emerald-800"
          }`}
        >
          {notification.type === "error" ? (
            <XCircle className="w-5 h-5 text-red-400" />
          ) : (
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          )}
          <span>{notification.message}</span>
        </div>
      )}

      {/* Header Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-emerald-950/60 via-slate-900 to-blue-950/60 border border-emerald-800/30 p-6 sm:p-8 backdrop-blur-md shadow-2xl">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-3 mb-2">
              <span className="p-2 rounded-xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                <Leaf className="w-6 h-6" />
              </span>
              <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight bg-gradient-to-r from-white via-emerald-100 to-emerald-400 bg-clip-text text-transparent">
                BRSR & ESG Intelligence Platform
              </h1>
              <span className="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full font-bold bg-emerald-500/10 text-emerald-300 border border-emerald-500/30">
                Non-LLM Verified
              </span>
            </div>
            <p className="text-sm text-gray-400 max-w-3xl">
              Deterministic SEBI BRSR Report Ingestion, PDF Document Parsing, Rule-Based ESG Indicator Extraction, and NGRBC Principle Classification across top Indian listed entities.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={() => setShowUploadModal(true)}
              className="flex items-center space-x-2 px-3.5 py-2 rounded-xl text-xs sm:text-sm font-semibold bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/20 transition-all cursor-pointer"
            >
              <UploadCloud className="w-4 h-4" />
              <span>Upload PDF</span>
            </button>
            <button
              onClick={() => setShowImportUrlModal(true)}
              className="flex items-center space-x-2 px-3.5 py-2 rounded-xl text-xs sm:text-sm font-semibold bg-gray-800 hover:bg-gray-700 text-gray-200 border border-gray-700 transition-all cursor-pointer"
            >
              <Globe className="w-4 h-4" />
              <span>Import URL</span>
            </button>
            <a
              href={getBrsrExportUrl("csv")}
              download
              className="flex items-center space-x-2 px-3.5 py-2 rounded-xl text-xs sm:text-sm font-semibold bg-blue-600/20 hover:bg-blue-600/30 text-blue-300 border border-blue-500/30 transition-all"
            >
              <FileSpreadsheet className="w-4 h-4" />
              <span>Export CSV</span>
            </a>
          </div>
        </div>

        {/* Global Key Metrics Ribbon */}
        {stats && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6 pt-6 border-t border-gray-800/60">
            <div className="bg-gray-900/40 p-3 rounded-xl border border-gray-800/40">
              <span className="text-xs text-gray-400">Total Companies</span>
              <p className="text-xl font-bold text-white mt-0.5">{stats.total_companies} Entities</p>
            </div>
            <div className="bg-gray-900/40 p-3 rounded-xl border border-gray-800/40">
              <span className="text-xs text-gray-400">Collected Reports</span>
              <p className="text-xl font-bold text-emerald-400 mt-0.5">{stats.total_reports} Reports</p>
            </div>
            <div className="bg-gray-900/40 p-3 rounded-xl border border-gray-800/40">
              <span className="text-xs text-gray-400">Common ESG Dataset</span>
              <p className="text-xl font-bold text-cyan-400 mt-0.5">{stats.total_observations} Observations</p>
            </div>
            <div className="bg-gray-900/40 p-3 rounded-xl border border-gray-800/40">
              <span className="text-xs text-gray-400">Deterministic Engine</span>
              <p className="text-xl font-bold text-amber-400 mt-0.5">100% Non-LLM</p>
            </div>
          </div>
        )}
      </div>

      {/* Sub-Navigation Tabs */}
      <div className="flex border-b border-gray-800 overflow-x-auto space-x-1 sm:space-x-2 pb-1 scrollbar-none">
        {[
          { id: "repository", label: "1. Report Repository", icon: Database },
          { id: "parser", label: "2. Parser Results", icon: FileText },
          { id: "extraction", label: "3. ESG Extraction", icon: Leaf },
          { id: "classification", label: "4. Mapping & Classification", icon: Layers },
          { id: "quality", label: "5. Review & Data Quality", icon: AlertTriangle },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeSubTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveSubTab(tab.id)}
              className={`flex items-center space-x-2 px-4 py-2.5 rounded-t-xl text-xs sm:text-sm font-semibold transition-all whitespace-nowrap cursor-pointer ${
                isActive
                  ? "bg-gray-900 text-emerald-400 border-t-2 border-emerald-500 border-x border-gray-800 shadow-lg"
                  : "text-gray-400 hover:text-gray-200 hover:bg-gray-900/40"
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* VIEW 1: REPORT REPOSITORY */}
      {activeSubTab === "repository" && (
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <h2 className="text-lg font-bold text-white flex items-center space-x-2">
              <Database className="w-5 h-5 text-emerald-400" />
              <span>SEBI-Regulated BRSR Report Repository</span>
            </h2>
            <div className="flex items-center space-x-2">
              <button
                onClick={loadReports}
                className="p-2 rounded-lg bg-gray-900 hover:bg-gray-800 text-gray-300 border border-gray-800 cursor-pointer"
                title="Refresh"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
              </button>
            </div>
          </div>

          <div className="overflow-x-auto rounded-xl border border-gray-800 bg-gray-950/60 shadow-xl">
            <table className="min-w-full divide-y divide-gray-800/80 text-left text-xs sm:text-sm">
              <thead className="bg-gray-900/80 font-semibold text-gray-300">
                <tr>
                  <th className="py-3.5 px-4">Company Name</th>
                  <th className="py-3.5 px-4">Industry / Sector</th>
                  <th className="py-3.5 px-4">Financial Year</th>
                  <th className="py-3.5 px-4">Pages / Size</th>
                  <th className="py-3.5 px-4">Source Origin</th>
                  <th className="py-3.5 px-4">Status</th>
                  <th className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/40">
                {reports.map((rep) => {
                  const isProcessing = processingId === rep.report_id;
                  return (
                    <tr key={rep.report_id} className="hover:bg-gray-900/50 transition-colors">
                      <td className="py-3.5 px-4">
                        <div className="font-semibold text-white">{rep.company_name}</div>
                        <div className="font-mono text-[11px] text-gray-500">ID: {rep.report_id}</div>
                      </td>
                      <td className="py-3.5 px-4 text-gray-300">{rep.industry || "Diversified"}</td>
                      <td className="py-3.5 px-4 font-mono text-cyan-300">{rep.financial_year}</td>
                      <td className="py-3.5 px-4 font-mono text-gray-400">
                        {rep.page_count > 0 ? `${rep.page_count} pages` : "Pending"} •{" "}
                        {roundKb(rep.file_size_bytes)}
                      </td>
                      <td className="py-3.5 px-4">
                        {rep.source_url && rep.source_url.startsWith("http") ? (
                          <a
                            href={rep.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center space-x-1 text-emerald-400 hover:underline text-xs"
                          >
                            <span>Official BSE / Portal</span>
                            <ExternalLink className="w-3 h-3 ml-0.5" />
                          </a>
                        ) : (
                          <span className="text-gray-500 text-xs">Direct PDF Upload</span>
                        )}
                      </td>
                      <td className="py-3.5 px-4">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold ${
                            rep.processing_status === "COMPLETED"
                              ? "bg-emerald-950/60 text-emerald-400 border border-emerald-800/60"
                              : "bg-amber-950/60 text-amber-300 border border-amber-800/60"
                          }`}
                        >
                          {rep.processing_status === "COMPLETED" ? (
                            <CheckCircle2 className="w-3 h-3 mr-1" />
                          ) : (
                            <RefreshCw className="w-3 h-3 mr-1" />
                          )}
                          {rep.processing_status}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-right space-x-2 whitespace-nowrap">
                        <button
                          disabled={isProcessing}
                          onClick={() => handleProcess(rep.report_id)}
                          className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                            isProcessing
                              ? "bg-emerald-800/30 text-emerald-400 cursor-wait"
                              : "bg-emerald-600 hover:bg-emerald-500 text-white shadow-md shadow-emerald-700/20"
                          }`}
                        >
                          {isProcessing ? "Processing..." : "Parse & Extract"}
                        </button>
                        <button
                          onClick={() => {
                            setSelectedReportId(rep.report_id);
                            setActiveSubTab("parser");
                          }}
                          className="px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-gray-800 hover:bg-gray-700 text-gray-300 border border-gray-700 cursor-pointer"
                        >
                          Inspect
                        </button>
                        <button
                          onClick={() => {
                            setCompanyFilter(rep.company_name);
                            setActiveSubTab("extraction");
                          }}
                          className="px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-blue-600/20 hover:bg-blue-600/30 text-blue-300 border border-blue-500/30 cursor-pointer"
                        >
                          ESG Data
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* VIEW 2: PARSER RESULTS */}
      {activeSubTab === "parser" && (
        <div className="space-y-6">
          {/* Report Selector Banner */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-xl bg-gray-900 border border-gray-800">
            <div className="flex items-center space-x-3">
              <FileText className="w-6 h-6 text-emerald-400" />
              <div>
                <span className="text-xs text-gray-400 uppercase tracking-wider font-bold">Selected Report</span>
                <div className="text-base font-bold text-white">
                  {selectedReport ? selectedReport.company_name : "Select a report"}
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <select
                value={selectedReportId}
                onChange={(e) => setSelectedReportId(e.target.value)}
                className="bg-gray-950 border border-gray-700 rounded-lg px-3 py-1.5 text-xs sm:text-sm text-gray-200 focus:outline-none focus:border-emerald-500"
              >
                {reports.map((r) => (
                  <option key={r.report_id} value={r.report_id}>
                    {r.company_name} ({r.financial_year})
                  </option>
                ))}
              </select>

              <button
                disabled={processingId === selectedReportId}
                onClick={() => handleProcess(selectedReportId)}
                className="px-3.5 py-1.5 rounded-lg text-xs sm:text-sm font-semibold bg-emerald-600 hover:bg-emerald-500 text-white cursor-pointer"
              >
                {processingId === selectedReportId ? "Reprocessing..." : "Reprocess PDF"}
              </button>
            </div>
          </div>

          {selectedReport && selectedReport.parsed_data && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left Column: Structural Milestones & Classification */}
              <div className="space-y-6">
                {/* Document Type Classification Box */}
                <div className="p-5 rounded-xl bg-gray-950/80 border border-gray-800 shadow-lg space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold uppercase tracking-wider text-gray-400">Report Classification</span>
                    <span className="text-xs px-2 py-0.5 rounded font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                      {Math.round((selectedReport.parsed_data.classification_confidence || 0.96) * 100)}% Confidence
                    </span>
                  </div>
                  <h3 className="text-lg font-bold text-white">{selectedReport.document_type}</h3>
                  <div className="space-y-1.5 text-xs text-gray-400">
                    {selectedReport.parsed_data.type_reasons?.map((reason, idx) => (
                      <div key={idx} className="flex items-start space-x-2">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 mt-0.5 flex-shrink-0" />
                        <span>{reason}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Sections Breakdown */}
                <div className="p-5 rounded-xl bg-gray-950/80 border border-gray-800 shadow-lg space-y-4">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-gray-400">SEBI Statutory Sections</h4>
                  <div className="space-y-3">
                    {selectedReport.parsed_data.sections?.map((sec) => (
                      <div
                        key={sec.section_code}
                        onClick={() => setSelectedPageNum(sec.start_page)}
                        className="p-3 rounded-lg bg-gray-900 hover:bg-gray-850 border border-gray-800 hover:border-emerald-500/50 cursor-pointer transition-all"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-semibold text-white text-xs">{sec.section_name}</span>
                          <span className="font-mono text-emerald-400 text-xs">
                            p.{sec.start_page}–{sec.end_page}
                          </span>
                        </div>
                        <div className="text-[11px] text-gray-500 mt-1">
                          {sec.page_count} pages • Method: {sec.detection_method}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* 9 NGRBC Principles Quick Jump */}
                <div className="p-5 rounded-xl bg-gray-950/80 border border-gray-800 shadow-lg space-y-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-gray-400">NGRBC Principle Milestones</h4>
                  <div className="grid grid-cols-3 gap-2">
                    {Object.entries(selectedReport.parsed_data.principle_pages || {}).map(([pKey, pNum]) => (
                      <button
                        key={pKey}
                        onClick={() => setSelectedPageNum(pNum)}
                        className="p-2 rounded-lg bg-gray-900 hover:bg-emerald-950/50 border border-gray-800 hover:border-emerald-600/40 text-center cursor-pointer transition-all"
                      >
                        <span className="text-xs font-bold text-cyan-300 block">{pKey}</span>
                        <span className="text-[10px] text-gray-400 font-mono">Page {pNum}</span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Right Column: Visual Page Preview & Page Content */}
              <div className="lg:col-span-2 space-y-4">
                <div className="flex items-center justify-between p-3 rounded-xl bg-gray-900 border border-gray-800 text-xs sm:text-sm">
                  <div className="flex items-center space-x-2">
                    <span className="text-gray-400">Page Navigation:</span>
                    <button
                      disabled={selectedPageNum <= 1}
                      onClick={() => setSelectedPageNum((p) => Math.max(1, p - 1))}
                      className="px-2.5 py-1 rounded bg-gray-800 hover:bg-gray-700 disabled:opacity-40 text-white cursor-pointer"
                    >
                      Prev
                    </button>
                    <span className="font-mono font-bold text-white">
                      Page {selectedPageNum} of {selectedReport.page_count || 1}
                    </span>
                    <button
                      disabled={selectedPageNum >= (selectedReport.page_count || 1)}
                      onClick={() => setSelectedPageNum((p) => Math.min(selectedReport.page_count, p + 1))}
                      className="px-2.5 py-1 rounded bg-gray-800 hover:bg-gray-700 disabled:opacity-40 text-white cursor-pointer"
                    >
                      Next
                    </button>
                  </div>

                  <div className="flex items-center space-x-1">
                    <button
                      onClick={() => setActiveParserTab("preview")}
                      className={`px-3 py-1 rounded-lg text-xs font-semibold cursor-pointer ${
                        activeParserTab === "preview"
                          ? "bg-emerald-600 text-white"
                          : "text-gray-400 hover:bg-gray-800"
                      }`}
                    >
                      Visual Preview
                    </button>
                    <button
                      onClick={() => setActiveParserTab("tables")}
                      className={`px-3 py-1 rounded-lg text-xs font-semibold cursor-pointer ${
                        activeParserTab === "tables"
                          ? "bg-emerald-600 text-white"
                          : "text-gray-400 hover:bg-gray-800"
                      }`}
                    >
                      Parsed Tables ({selectedReport.parsed_data.tables_count || 0})
                    </button>
                  </div>
                </div>

                {/* Content Panel */}
                <div className="p-4 rounded-xl bg-gray-950 border border-gray-800 min-h-[500px]">
                  {activeParserTab === "preview" ? (
                    <div className="flex flex-col items-center justify-center space-y-3">
                      <div className="relative border border-gray-800 rounded-lg overflow-hidden bg-black max-w-full shadow-2xl">
                        <img
                          src={getBrsrPagePreviewUrl(selectedReport.report_id, selectedPageNum)}
                          alt={`Page ${selectedPageNum} Preview`}
                          className="max-h-[750px] w-auto object-contain"
                          onError={(e) => {
                            e.target.style.display = "none";
                            e.target.nextSibling.style.display = "flex";
                          }}
                        />
                        <div className="hidden flex-col items-center justify-center p-12 text-gray-500">
                          <AlertTriangle className="w-8 h-8 text-amber-500 mb-2" />
                          <span>Page {selectedPageNum} preview image generating on-demand...</span>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="flex items-center justify-between text-xs text-gray-400">
                        <span>Extracted Tables & Rows on Page {selectedPageNum}:</span>
                      </div>
                      <div className="text-xs text-gray-400 bg-gray-900/60 p-4 rounded-lg border border-gray-800">
                        <p className="font-semibold text-gray-300 mb-2">
                          Interactive Table Extractor (PyMuPDF Grid Aligner):
                        </p>
                        <p>
                          Tables on this page have been segmented into typed rows and columns. Navigate to the{" "}
                          <span className="text-emerald-400 font-semibold cursor-pointer" onClick={() => setActiveSubTab("extraction")}>
                            ESG Extraction tab
                          </span>{" "}
                          to see specific normalized metrics mapped to the Common Dataset.
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* VIEW 3: ESG EXTRACTION */}
      {activeSubTab === "extraction" && (
        <div className="space-y-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
            <div className="flex items-center space-x-2">
              <Leaf className="w-5 h-5 text-emerald-400" />
              <h2 className="text-lg font-bold text-white">Extracted ESG Indicators</h2>
              <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-gray-800 text-gray-300">
                {filteredObservations.length} items
              </span>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <div className="relative">
                <Search className="w-4 h-4 text-gray-400 absolute left-3 top-2.5" />
                <input
                  type="text"
                  placeholder="Search indicator or code..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="bg-gray-900 border border-gray-700 rounded-lg pl-9 pr-3 py-1.5 text-xs text-gray-200 w-48 sm:w-64 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <select
                value={companyFilter}
                onChange={(e) => setCompanyFilter(e.target.value)}
                className="bg-gray-900 border border-gray-700 rounded-lg px-2.5 py-1.5 text-xs text-gray-200 focus:outline-none"
              >
                <option value="">All Companies</option>
                {stats?.companies?.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>

              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="bg-gray-900 border border-gray-700 rounded-lg px-2.5 py-1.5 text-xs text-gray-200 focus:outline-none"
              >
                <option value="ALL">All Statuses</option>
                <option value="EXTRACTED">Extracted</option>
                <option value="REPORTED_ZERO">Reported Zero</option>
                <option value="NOT_DISCLOSED">Not Disclosed</option>
                <option value="NOT_FOUND">Not Found</option>
              </select>
            </div>
          </div>

          {/* Category Filter Pills */}
          <div className="flex items-center space-x-2">
            {["ALL", "Environmental", "Social", "Governance"].map((cat) => (
              <button
                key={cat}
                onClick={() => setCategoryFilter(cat)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                  categoryFilter === cat
                    ? "bg-emerald-600 text-white shadow-md shadow-emerald-700/20"
                    : "bg-gray-900 text-gray-400 hover:text-white border border-gray-800"
                }`}
              >
                {cat === "ALL" ? "All Categories" : cat}
              </button>
            ))}
          </div>

          {/* Observation Records Table */}
          <div className="overflow-x-auto rounded-xl border border-gray-800 bg-gray-950/60 shadow-xl">
            <table className="min-w-full divide-y divide-gray-800/80 text-left text-xs sm:text-sm">
              <thead className="bg-gray-900/80 font-semibold text-gray-300">
                <tr>
                  <th className="py-3.5 px-4">Indicator Name</th>
                  <th className="py-3.5 px-4">Company</th>
                  <th className="py-3.5 px-4">Reported Value & Unit</th>
                  <th className="py-3.5 px-4">Normalized Value</th>
                  <th className="py-3.5 px-4">Status</th>
                  <th className="py-3.5 px-4">Source Page</th>
                  <th className="py-3.5 px-4 text-right">Evidence & Audit</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/40">
                {filteredObservations.map((obs) => {
                  return (
                    <tr key={obs.observation_id} className="hover:bg-gray-900/50 transition-colors">
                      <td className="py-3.5 px-4">
                        <div className="font-semibold text-white">{obs.indicator_name}</div>
                        <div className="flex items-center space-x-2 mt-0.5">
                          <span className="font-mono text-[10px] text-gray-500">{obs.indicator_code}</span>
                          <span
                            className={`text-[10px] px-1.5 py-0.2 rounded font-semibold ${
                              obs.esg_category === "Environmental"
                                ? "bg-emerald-950 text-emerald-400 border border-emerald-800"
                                : obs.esg_category === "Social"
                                ? "bg-blue-950 text-blue-400 border border-blue-800"
                                : "bg-purple-950 text-purple-400 border border-purple-800"
                            }`}
                          >
                            {obs.esg_category}
                          </span>
                        </div>
                      </td>
                      <td className="py-3.5 px-4 text-gray-300 max-w-[140px] truncate">{obs.company_name}</td>
                      <td className="py-3.5 px-4">
                        <span className="font-mono font-semibold text-white">{obs.reported_value}</span>{" "}
                        <span className="text-gray-400 text-xs">{obs.unit || ""}</span>
                      </td>
                      <td className="py-3.5 px-4 font-mono text-emerald-400">
                        {obs.normalized_value !== null ? `${obs.normalized_value} ${obs.normalized_unit || ""}` : "—"}
                      </td>
                      <td className="py-3.5 px-4">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold ${
                            obs.extraction_status === "EXTRACTED"
                              ? "bg-emerald-950/60 text-emerald-400 border border-emerald-800/60"
                              : obs.extraction_status === "REPORTED_ZERO"
                              ? "bg-cyan-950/60 text-cyan-300 border border-cyan-800/60"
                              : obs.extraction_status === "NOT_DISCLOSED"
                              ? "bg-amber-950/60 text-amber-300 border border-amber-800/60"
                              : "bg-gray-900 text-gray-400 border border-gray-800"
                          }`}
                        >
                          {obs.extraction_status}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 font-mono text-cyan-400">Page {obs.source_page}</td>
                      <td className="py-3.5 px-4 text-right space-x-2 whitespace-nowrap">
                        <button
                          onClick={() => {
                            setReviewingObs(obs);
                            setEditValue(obs.reported_value === "NOT_FOUND" ? "" : obs.reported_value);
                          }}
                          className="p-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 border border-gray-700 cursor-pointer inline-flex items-center space-x-1"
                          title="Audit & Review"
                        >
                          <Edit3 className="w-3.5 h-3.5 text-amber-400" />
                          <span className="text-xs">Audit</span>
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* VIEW 4: MAPPING AND CLASSIFICATION */}
      {activeSubTab === "classification" && (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h2 className="text-lg font-bold text-white flex items-center space-x-2">
                <Layers className="w-5 h-5 text-emerald-400" />
                <span>Multi-Dimensional ESG & NGRBC Principle Mapping</span>
              </h2>
              <p className="text-xs text-gray-400 mt-0.5">
                Each observation is verified and mapped across ESG Dimensions, SEBI Statutory Sections, and the 9 NGRBC Principles.
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <a
                href={getBrsrExportUrl("json")}
                download
                className="flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-semibold bg-gray-800 hover:bg-gray-700 text-gray-200 border border-gray-700"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Export Canonical JSON</span>
              </a>
            </div>
          </div>

          {/* 9 NGRBC Principles Interactive Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              { id: "P1", name: "Ethics, Transparency & Accountability", cat: "Governance", desc: "Anti-corruption, anti-bribery, board oversight, regulatory fines" },
              { id: "P2", name: "Sustainable Products & Services", cat: "Environmental", desc: "Life cycle assessments, sustainable sourcing, recyclable packaging" },
              { id: "P3", name: "Employee Well-Being", cat: "Social", desc: "Workforce composition, LTIFR safety, training person-hours, health insurance" },
              { id: "P4", name: "Stakeholder Responsiveness", cat: "Social", desc: "Vulnerable stakeholder consultation, grievance redressal mechanisms" },
              { id: "P5", name: "Human Rights", cat: "Social", desc: "POSH sexual harassment complaints, child labor, forced labor" },
              { id: "P6", name: "Environmental Protection & Restoration", cat: "Environmental", desc: "Total energy, Scope 1 & 2 GHG footprint, water consumption, waste circularity" },
              { id: "P7", name: "Responsible Public Policy Advocacy", cat: "Governance", desc: "Trade associations, lobbying transparency, policy submissions" },
              { id: "P8", name: "Inclusive Growth & Equitable Development", cat: "Social", desc: "Corporate Social Responsibility (CSR) projects, local community development" },
              { id: "P9", name: "Responsible Consumer Engagement", cat: "Social", desc: "Customer complaints, data privacy breaches, cybersecurity safeguards" },
            ].map((p) => {
              const summaryData = principlesSummary[p.id] || { count: 0, indicators: [] };
              return (
                <div
                  key={p.id}
                  className="p-4 rounded-xl bg-gray-950 border border-gray-800/80 hover:border-emerald-500/40 transition-all shadow-lg space-y-2.5"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-extrabold text-sm text-cyan-400 font-mono">{p.id}</span>
                    <span
                      className={`text-[10px] px-2 py-0.5 rounded font-semibold ${
                        p.cat === "Environmental"
                          ? "bg-emerald-950 text-emerald-400 border border-emerald-800"
                          : p.cat === "Social"
                          ? "bg-blue-950 text-blue-400 border border-blue-800"
                          : "bg-purple-950 text-purple-400 border border-purple-800"
                      }`}
                    >
                      {p.cat}
                    </span>
                  </div>
                  <h4 className="font-bold text-white text-sm">{p.name}</h4>
                  <p className="text-xs text-gray-400 line-clamp-2">{p.desc}</p>
                  <div className="pt-2 border-t border-gray-800/60 flex items-center justify-between text-xs">
                    <span className="text-gray-500 font-mono">{summaryData.count} Disclosures Mapped</span>
                    <button
                      onClick={() => {
                        setSearchQuery(p.id);
                        setActiveSubTab("extraction");
                      }}
                      className="text-emerald-400 hover:underline flex items-center space-x-1 cursor-pointer"
                    >
                      <span>View</span>
                      <ArrowRight className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* VIEW 5: REVIEW AND DATA QUALITY */}
      {activeSubTab === "quality" && (
        <div className="space-y-6">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center space-x-2">
              <AlertTriangle className="w-5 h-5 text-amber-400" />
              <span>Evidence Attribution & Data Quality Review Gate</span>
            </h2>
            <p className="text-xs text-gray-400 mt-0.5">
              Review uncertain extractions, cross-referenced disclosures, or missing metrics. Human auditors can modify values with immutable audit tracking.
            </p>
          </div>

          {/* Quality Summary Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-gray-950 border border-gray-800 shadow-lg">
              <span className="text-xs text-gray-400">Total Flagged Disclosures</span>
              <p className="text-2xl font-bold text-amber-400 mt-1">
                {observations.filter((o) => o.review_status === "REQUIRES_REVIEW").length}
              </p>
              <span className="text-[11px] text-gray-500">Not Disclosed or Ambiguous</span>
            </div>
            <div className="p-4 rounded-xl bg-gray-950 border border-gray-800 shadow-lg">
              <span className="text-xs text-gray-400">Auto-Verified by Rules</span>
              <p className="text-2xl font-bold text-emerald-400 mt-1">
                {observations.filter((o) => o.review_status === "AUTO_VERIFIED").length}
              </p>
              <span className="text-[11px] text-gray-500">Supported by Table Evidence</span>
            </div>
            <div className="p-4 rounded-xl bg-gray-950 border border-gray-800 shadow-lg">
              <span className="text-xs text-gray-400">Auditor Overrides</span>
              <p className="text-2xl font-bold text-blue-400 mt-1">
                {observations.filter((o) => o.review_status === "MANUALLY_EDITED").length}
              </p>
              <span className="text-[11px] text-gray-500">Human-in-the-Loop Edits</span>
            </div>
          </div>

          {/* Flagged Observations for Review */}
          <div className="space-y-3">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Disclosures Requiring Auditor Verification
            </h3>
            <div className="divide-y divide-gray-800 rounded-xl border border-gray-800 bg-gray-950/60 overflow-hidden">
              {observations
                .filter((o) => o.review_status === "REQUIRES_REVIEW" || o.review_status === "MANUALLY_EDITED")
                .map((obs) => (
                  <div key={obs.observation_id} className="p-4 hover:bg-gray-900/40 transition-colors flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-white text-sm">{obs.indicator_name}</span>
                        <span className="text-xs text-cyan-400 font-mono">({obs.company_name})</span>
                        <span className="text-xs px-2 py-0.5 rounded font-bold bg-amber-500/10 text-amber-300 border border-amber-500/30">
                          {obs.extraction_status}
                        </span>
                      </div>
                      <p className="text-xs text-gray-400 italic">
                        Evidence snippet: &ldquo;{obs.source_text}&rdquo; (Page {obs.source_page})
                      </p>
                      {obs.manual_correction_notes && (
                        <div className="text-xs text-blue-300 font-mono mt-1">
                          Auditor Log: {obs.manual_correction_notes}
                        </div>
                      )}
                    </div>

                    <div className="flex items-center space-x-2 flex-shrink-0">
                      <button
                        onClick={() => {
                          setReviewingObs(obs);
                          setEditValue(obs.reported_value === "NOT_FOUND" ? "" : obs.reported_value);
                        }}
                        className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-amber-600/20 hover:bg-amber-600/30 text-amber-300 border border-amber-500/30 cursor-pointer"
                      >
                        <Edit3 className="w-3.5 h-3.5" />
                        <span>Override Value</span>
                      </button>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </div>
      )}

      {/* Review & Manual Edit Modal */}
      {reviewingObs && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-gray-950 border border-gray-800 rounded-2xl p-6 max-w-lg w-full space-y-4 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-gray-800">
              <h3 className="text-base font-bold text-white flex items-center space-x-2">
                <Edit3 className="w-5 h-5 text-amber-400" />
                <span>Auditor Value Correction</span>
              </h3>
              <button onClick={() => setReviewingObs(null)} className="text-gray-400 hover:text-white cursor-pointer">
                ✕
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <span className="text-gray-400">Indicator:</span>
                <p className="font-bold text-white text-sm">{reviewingObs.indicator_name}</p>
              </div>
              <div>
                <span className="text-gray-400">Company & Period:</span>
                <p className="text-gray-200">
                  {reviewingObs.company_name} ({reviewingObs.financial_year})
                </p>
              </div>
              <div className="p-2.5 rounded bg-gray-900 border border-gray-800 text-gray-300">
                <span className="font-semibold text-gray-400 block mb-1">Source Evidence Snippet (Page {reviewingObs.source_page}):</span>
                &ldquo;{reviewingObs.source_text}&rdquo;
              </div>

              <div>
                <label className="block text-gray-400 mb-1">Corrected Value (e.g. 12500, Disclosed, Nil):</label>
                <input
                  type="text"
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg p-2 text-white focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-gray-400 mb-1">Reviewer Name:</label>
                <input
                  type="text"
                  value={reviewerName}
                  onChange={(e) => setReviewerName(e.target.value)}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg p-2 text-white focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-gray-400 mb-1">Audit Justification Notes:</label>
                <textarea
                  rows={2}
                  value={editNotes}
                  onChange={(e) => setEditNotes(e.target.value)}
                  placeholder="Reason for manual adjustment..."
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg p-2 text-white focus:outline-none"
                />
              </div>
            </div>

            <div className="flex items-center justify-end space-x-2 pt-3 border-t border-gray-800">
              <button
                onClick={() => setReviewingObs(null)}
                className="px-4 py-2 rounded-lg text-xs font-semibold bg-gray-800 hover:bg-gray-700 text-gray-300 cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handleReviewSubmit}
                className="px-4 py-2 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white cursor-pointer shadow-lg shadow-emerald-700/20"
              >
                Commit Audit Override
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <form
            onSubmit={handleUploadSubmit}
            className="bg-gray-950 border border-gray-800 rounded-2xl p-6 max-w-md w-full space-y-4 shadow-2xl"
          >
            <div className="flex items-center justify-between pb-3 border-b border-gray-800">
              <h3 className="text-base font-bold text-white flex items-center space-x-2">
                <UploadCloud className="w-5 h-5 text-emerald-400" />
                <span>Upload Official BRSR PDF</span>
              </h3>
              <button onClick={() => setShowUploadModal(false)} type="button" className="text-gray-400 hover:text-white cursor-pointer">
                ✕
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-gray-400 mb-1">Select PDF File:</label>
                <input
                  type="file"
                  accept=".pdf"
                  onChange={(e) => setUploadFile(e.target.files[0])}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg p-2 text-gray-300"
                />
              </div>

              <div>
                <label className="block text-gray-400 mb-1">Company Name:</label>
                <input
                  type="text"
                  placeholder="e.g. Infosys Limited"
                  value={uploadCompany}
                  onChange={(e) => setUploadCompany(e.target.value)}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg p-2 text-white focus:outline-none"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-gray-400 mb-1">Financial Year:</label>
                  <select
                    value={uploadYear}
                    onChange={(e) => setUploadYear(e.target.value)}
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg p-2 text-white"
                  >
                    <option value="2023-24">2023-24</option>
                    <option value="2022-23">2022-23</option>
                    <option value="2024-25">2024-25</option>
                  </select>
                </div>
                <div>
                  <label className="block text-gray-400 mb-1">Industry:</label>
                  <input
                    type="text"
                    placeholder="e.g. Technology"
                    value={uploadIndustry}
                    onChange={(e) => setUploadIndustry(e.target.value)}
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg p-2 text-white"
                  />
                </div>
              </div>
            </div>

            <div className="flex items-center justify-end space-x-2 pt-3 border-t border-gray-800">
              <button
                type="button"
                onClick={() => setShowUploadModal(false)}
                className="px-4 py-2 rounded-lg text-xs font-semibold bg-gray-800 hover:bg-gray-700 text-gray-300 cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white cursor-pointer shadow-lg shadow-emerald-700/20"
              >
                {loading ? "Uploading..." : "Register Report"}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Import URL Modal */}
      {showImportUrlModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <form
            onSubmit={handleImportUrlSubmit}
            className="bg-gray-950 border border-gray-800 rounded-2xl p-6 max-w-md w-full space-y-4 shadow-2xl"
          >
            <div className="flex items-center justify-between pb-3 border-b border-gray-800">
              <h3 className="text-base font-bold text-white flex items-center space-x-2">
                <Globe className="w-5 h-5 text-emerald-400" />
                <span>Import from Public PDF URL</span>
              </h3>
              <button onClick={() => setShowImportUrlModal(false)} type="button" className="text-gray-400 hover:text-white cursor-pointer">
                ✕
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-gray-400 mb-1">Public BRSR PDF URL:</label>
                <input
                  type="url"
                  placeholder="https://www.bseindia.com/XBRLFILES/..."
                  value={importUrl}
                  onChange={(e) => setImportUrl(e.target.value)}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg p-2 text-white font-mono text-[11px]"
                  required
                />
              </div>

              <div>
                <label className="block text-gray-400 mb-1">Company Name:</label>
                <input
                  type="text"
                  placeholder="e.g. Tata Motors Limited"
                  value={importCompany}
                  onChange={(e) => setImportCompany(e.target.value)}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg p-2 text-white"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-gray-400 mb-1">Financial Year:</label>
                  <select
                    value={importYear}
                    onChange={(e) => setImportYear(e.target.value)}
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg p-2 text-white"
                  >
                    <option value="2023-24">2023-24</option>
                    <option value="2022-23">2022-23</option>
                    <option value="2024-25">2024-25</option>
                  </select>
                </div>
                <div>
                  <label className="block text-gray-400 mb-1">Industry:</label>
                  <input
                    type="text"
                    placeholder="e.g. Automotive"
                    value={importIndustry}
                    onChange={(e) => setImportIndustry(e.target.value)}
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg p-2 text-white"
                  />
                </div>
              </div>
            </div>

            <div className="flex items-center justify-end space-x-2 pt-3 border-t border-gray-800">
              <button
                type="button"
                onClick={() => setShowImportUrlModal(false)}
                className="px-4 py-2 rounded-lg text-xs font-semibold bg-gray-800 hover:bg-gray-700 text-gray-300 cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white cursor-pointer shadow-lg shadow-emerald-700/20"
              >
                {loading ? "Importing..." : "Download & Ingest"}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}

function roundKb(bytes) {
  if (!bytes) return "0 KB";
  return `${(bytes / 1024).toFixed(1)} KB`;
}
