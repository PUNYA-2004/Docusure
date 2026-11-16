const API_BASE = "http://localhost:8000/api";

export async function uploadDocument(file, docType = null) {
  const formData = new FormData();
  formData.append("file", file);
  if (docType) {
    formData.append("doc_type", docType);
  }

  const res = await fetch(`${API_BASE}/documents/process`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(err.detail || "Document processing failed");
  }
  return res.json();
}

export async function getRecentDocuments() {
  const res = await fetch(`${API_BASE}/documents`);
  if (!res.ok) throw new Error("Failed to fetch documents");
  return res.json();
}

export async function getDocument(docId) {
  const res = await fetch(`${API_BASE}/documents/${docId}`);
  if (!res.ok) throw new Error("Document not found");
  return res.json();
}

export function getPagePreviewUrl(docId, pageNum = 1) {
  return `${API_BASE}/documents/${docId}/pages/${pageNum}/preview`;
}

export async function submitReview(docId, reviewPayload) {
  const res = await fetch(`${API_BASE}/documents/${docId}/review`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(reviewPayload),
  });
  if (!res.ok) throw new Error("Review submission failed");
  return res.json();
}

export async function runRobustnessTest(docId, degradationType) {
  const res = await fetch(`${API_BASE}/documents/${docId}/robustness?degradation_type=${degradationType}`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Robustness test failed");
  return res.json();
}

export async function getCalibrationReport() {
  const res = await fetch(`${API_BASE}/calibration/report`);
  if (!res.ok) throw new Error("Failed to load calibration report");
  return res.json();
}

export async function getAuditLogs(docId = null) {
  const url = docId ? `${API_BASE}/audit/logs?doc_id=${docId}` : `${API_BASE}/audit/logs`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to load audit logs");
  return res.json();
}

export async function getSampleDocs() {
  const res = await fetch(`${API_BASE}/sample-docs`);
  if (!res.ok) throw new Error("Failed to load sample documents");
  return res.json();
}

export async function processSampleDoc(sampleName) {
  const res = await fetch(`${API_BASE}/sample-docs/${sampleName}/process`, {
    method: "POST",
  });
  if (!res.ok) throw new Error(`Processing sample doc ${sampleName} failed`);
  return res.json();
}

// =============================================================================
// BRSR & ESG Intelligence API Client Functions
// =============================================================================

export async function getBrsrReports(company = "", year = "") {
  let url = `${API_BASE}/brsr/reports`;
  const params = new URLSearchParams();
  if (company) params.append("company", company);
  if (year) params.append("year", year);
  if (params.toString()) url += `?${params.toString()}`;
  
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to load BRSR reports");
  return res.json();
}

export async function getBrsrReport(reportId) {
  const res = await fetch(`${API_BASE}/brsr/reports/${reportId}`);
  if (!res.ok) throw new Error("Failed to load BRSR report details");
  return res.json();
}

export async function uploadBrsrReport(file, companyName, financialYear = "2023-24", industry = "Diversified") {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("company_name", companyName);
  formData.append("financial_year", financialYear);
  formData.append("industry", industry);

  const res = await fetch(`${API_BASE}/brsr/reports/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(err.detail || "BRSR upload failed");
  }
  return res.json();
}

export async function importBrsrFromUrl(sourceUrl, companyName, financialYear = "2023-24", industry = "Diversified") {
  const formData = new FormData();
  formData.append("source_url", sourceUrl);
  formData.append("company_name", companyName);
  formData.append("financial_year", financialYear);
  formData.append("industry", industry);

  const res = await fetch(`${API_BASE}/brsr/reports/import-url`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Import failed" }));
    throw new Error(err.detail || "BRSR URL import failed");
  }
  return res.json();
}

export async function processBrsrReport(reportId) {
  const res = await fetch(`${API_BASE}/brsr/reports/${reportId}/process`, {
    method: "POST",
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Processing failed" }));
    throw new Error(err.detail || "BRSR processing failed");
  }
  return res.json();
}

export function getBrsrPagePreviewUrl(reportId, pageNum = 1) {
  return `${API_BASE}/brsr/reports/${reportId}/pages/${pageNum}/preview`;
}

export async function getBrsrObservations(filters = {}) {
  const params = new URLSearchParams();
  if (filters.reportId) params.append("report_id", filters.reportId);
  if (filters.company) params.append("company", filters.company);
  if (filters.category) params.append("category", filters.category);
  if (filters.indicator) params.append("indicator", filters.indicator);
  if (filters.principle) params.append("principle", filters.principle);
  if (filters.reviewStatus) params.append("review_status", filters.reviewStatus);

  const qs = params.toString() ? `?${params.toString()}` : "";
  const res = await fetch(`${API_BASE}/brsr/observations${qs}`);
  if (!res.ok) throw new Error("Failed to load ESG observations");
  return res.json();
}

export async function reviewBrsrObservation(observationId, reviewPayload) {
  const res = await fetch(`${API_BASE}/brsr/observations/${observationId}/review`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(reviewPayload),
  });
  if (!res.ok) throw new Error("Failed to update observation review");
  return res.json();
}

export async function getBrsrPrinciplesSummary(reportId = null) {
  const url = reportId ? `${API_BASE}/brsr/principles/summary?report_id=${reportId}` : `${API_BASE}/brsr/principles/summary`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to load principles summary");
  return res.json();
}

export async function getBrsrStats() {
  const res = await fetch(`${API_BASE}/brsr/stats`);
  if (!res.ok) throw new Error("Failed to load BRSR stats");
  return res.json();
}

export function getBrsrExportUrl(format = "csv", company = "", year = "", category = "") {
  const params = new URLSearchParams({ format });
  if (company) params.append("company", company);
  if (year) params.append("year", year);
  if (category) params.append("category", category);
  return `${API_BASE}/brsr/export?${params.toString()}`;
}

