import React, { useState } from "react";
import Navbar from "./components/Navbar";
import DashboardPage from "./pages/DashboardPage";
import UploadProcessPage from "./pages/UploadProcessPage";
import DocumentDetailPage from "./pages/DocumentDetailPage";
import CalibrationPage from "./components/CalibrationPage";
import RobustnessLab from "./components/RobustnessLab";
import AuditPage from "./pages/AuditPage";
import BRSRPage from "./pages/BRSRPage";

export default function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [currentDoc, setCurrentDoc] = useState(null);

  const handleSelectDoc = (doc) => {
    setCurrentDoc(doc);
    setActiveTab("inspector");
  };

  const handleUploadSuccess = (doc) => {
    setCurrentDoc(doc);
    setActiveTab("inspector");
  };

  return (
    <div className="min-h-screen bg-[#0b0f19] text-gray-100 flex flex-col selection:bg-blue-600 selection:text-white">
      {/* Navigation */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        currentDoc={currentDoc}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === "dashboard" && (
          <DashboardPage
            onSelectDoc={handleSelectDoc}
            onNavigateUpload={() => setActiveTab("upload")}
          />
        )}

        {activeTab === "brsr" && <BRSRPage />}

        {activeTab === "upload" && (
          <UploadProcessPage onUploadSuccess={handleUploadSuccess} />
        )}

        {activeTab === "inspector" && (
          <DocumentDetailPage
            document={currentDoc}
            onBack={() => setActiveTab("dashboard")}
            onUpdateDoc={(updated) => setCurrentDoc(updated)}
          />
        )}

        {activeTab === "calibration" && <CalibrationPage />}

        {activeTab === "robustness" && <RobustnessLab document={currentDoc} />}

        {activeTab === "audit" && <AuditPage currentDoc={currentDoc} />}
      </main>

      {/* Enterprise Footer */}
      <footer className="border-t border-gray-900 bg-gray-950/80 py-6 text-center text-xs text-gray-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-2">
          <p>
            <span className="font-bold text-gray-400">DOCUSURE</span> — MCA Final-Year Major Project (Document AI + Evidence Verification)
          </p>
          <p className="font-mono text-[11px] text-gray-600">
            Powered by PyMuPDF • EasyOCR • FastAPI • React • RapidFuzz • OpenCV
          </p>
        </div>
      </footer>
    </div>
  );
}
