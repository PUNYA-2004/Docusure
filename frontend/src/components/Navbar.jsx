import React from "react";
import { ShieldCheck, FileText, Activity, Sliders, History, UploadCloud, Cpu, Leaf } from "lucide-react";

export default function Navbar({ activeTab, setActiveTab, currentDoc }) {
  const tabs = [
    { id: "dashboard", label: "Dashboard", icon: Activity },
    { id: "brsr", label: "BRSR & ESG Intelligence", icon: Leaf },
    { id: "upload", label: "Ingest & Extract", icon: UploadCloud },
    { id: "inspector", label: "Document Inspector", icon: FileText, disabled: !currentDoc },
    { id: "calibration", label: "Calibration & Research", icon: Sliders },
    { id: "robustness", label: "Robustness Lab", icon: Cpu, disabled: !currentDoc },
    { id: "audit", label: "Audit Trail", icon: History },
  ];

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-gray-800 bg-gray-950/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab("dashboard")}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-cyan-400 flex items-center justify-center shadow-lg shadow-blue-500/20">
              <ShieldCheck className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-blue-100 to-blue-400 bg-clip-text text-transparent">
                  DOCUSURE
                </span>
                <span className="text-[10px] font-semibold tracking-wider uppercase px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                  AI DOC INTEL
                </span>
              </div>
              <p className="text-xs text-gray-400 font-mono hidden sm:block">
                Evidence-Grounded Verification Engine
              </p>
            </div>
          </div>

          {/* Nav Tabs */}
          <nav className="flex items-center space-x-1 sm:space-x-2">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  disabled={tab.disabled}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-all ${
                    isActive
                      ? "bg-blue-600/20 text-blue-400 border border-blue-500/30 shadow-sm shadow-blue-500/10"
                      : tab.disabled
                      ? "text-gray-600 cursor-not-allowed opacity-50"
                      : "text-gray-300 hover:text-white hover:bg-gray-800/60"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="hidden md:inline">{tab.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Live Engine Indicator */}
          <div className="flex items-center space-x-3">
            {currentDoc && (
              <div className="hidden lg:flex items-center space-x-2 text-xs text-gray-400 bg-gray-900 px-2.5 py-1 rounded-md border border-gray-800">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                <span className="font-mono text-gray-300 truncate max-w-[140px]">{currentDoc.filename}</span>
              </div>
            )}
            <div className="flex items-center space-x-1.5 text-xs text-emerald-400 bg-emerald-950/40 border border-emerald-800/40 px-2.5 py-1 rounded-full">
              <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
              <span className="font-medium hidden sm:inline">Engine Active</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
