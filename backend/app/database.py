import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.config import DB_PATH

def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Documents table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        doc_type TEXT NOT NULL,
        page_count INTEGER NOT NULL,
        upload_time TEXT NOT NULL,
        overall_decision TEXT NOT NULL,
        average_confidence REAL NOT NULL,
        raw_ocr_text TEXT,
        is_reviewed INTEGER DEFAULT 0,
        reviewer_name TEXT,
        review_notes TEXT,
        processed_data_json TEXT NOT NULL
    )
    """)
    
    # Audit Logs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id TEXT PRIMARY KEY,
        document_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        action TEXT NOT NULL,
        actor TEXT NOT NULL,
        details_json TEXT NOT NULL,
        FOREIGN KEY (document_id) REFERENCES documents (id)
    )
    """)
    
    # Robustness Experiments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS robustness_experiments (
        id TEXT PRIMARY KEY,
        document_id TEXT NOT NULL,
        degradation_type TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        results_json TEXT NOT NULL
    )
    """)

    # BRSR Reports Repository table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS brsr_reports (
        report_id TEXT PRIMARY KEY,
        company_name TEXT NOT NULL,
        industry TEXT,
        financial_year TEXT NOT NULL,
        report_title TEXT NOT NULL,
        report_category TEXT NOT NULL,
        source_url TEXT,
        local_file_path TEXT NOT NULL,
        file_hash_sha256 TEXT NOT NULL UNIQUE,
        file_size_bytes INTEGER DEFAULT 0,
        page_count INTEGER DEFAULT 0,
        upload_status TEXT NOT NULL,
        processing_status TEXT NOT NULL,
        error_message TEXT,
        document_type TEXT NOT NULL,
        created_at TEXT NOT NULL,
        parsed_data_json TEXT
    )
    """)

    # BRSR Canonical Observations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS brsr_observations (
        observation_id TEXT PRIMARY KEY,
        report_id TEXT NOT NULL,
        company_name TEXT NOT NULL,
        industry TEXT,
        financial_year TEXT NOT NULL,
        report_type TEXT,
        section_name TEXT,
        esg_category TEXT NOT NULL,
        indicator_code TEXT NOT NULL,
        indicator_name TEXT NOT NULL,
        reported_value TEXT NOT NULL,
        numeric_value REAL,
        unit TEXT,
        normalized_value REAL,
        normalized_unit TEXT,
        reporting_period TEXT,
        reporting_boundary TEXT,
        brsr_principle TEXT,
        brsr_core_indicator TEXT,
        source_page INTEGER,
        source_text TEXT,
        extraction_method TEXT,
        classification_status TEXT,
        extraction_status TEXT,
        confidence_score REAL,
        review_status TEXT,
        manual_correction_notes TEXT,
        FOREIGN KEY (report_id) REFERENCES brsr_reports (report_id)
    )
    """)
    
    conn.commit()
    conn.close()

def save_document(doc_data: Dict[str, Any]):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO documents (
            id, filename, file_path, doc_type, page_count, upload_time,
            overall_decision, average_confidence, raw_ocr_text,
            is_reviewed, reviewer_name, review_notes, processed_data_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        doc_data["id"],
        doc_data["filename"],
        doc_data["file_path"],
        doc_data["doc_type"],
        doc_data["page_count"],
        doc_data.get("upload_time", datetime.utcnow().isoformat()),
        doc_data["overall_decision"],
        doc_data["average_confidence"],
        doc_data.get("raw_ocr_text", ""),
        doc_data.get("is_reviewed", 0),
        doc_data.get("reviewer_name", None),
        doc_data.get("review_notes", None),
        json.dumps(doc_data["processed_data"])
    ))
    conn.commit()
    conn.close()

def get_document_by_id(doc_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["processed_data"] = json.loads(d["processed_data_json"])
    del d["processed_data_json"]
    return d

def list_documents(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, filename, doc_type, page_count, upload_time, overall_decision, average_confidence, is_reviewed, reviewer_name FROM documents ORDER BY upload_time DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_audit_log(doc_id: str, action: str, actor: str, details: Dict[str, Any]):
    import uuid
    conn = get_db_connection()
    cursor = conn.cursor()
    log_id = f"log_{uuid.uuid4().hex[:10]}"
    cursor.execute("""
        INSERT INTO audit_logs (id, document_id, timestamp, action, actor, details_json)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        log_id,
        doc_id,
        datetime.utcnow().isoformat(),
        action,
        actor,
        json.dumps(details)
    ))
    conn.commit()
    conn.close()

def get_audit_logs(doc_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    if doc_id:
        cursor.execute("SELECT * FROM audit_logs WHERE document_id = ? ORDER BY timestamp DESC LIMIT ?", (doc_id, limit))
    else:
        cursor.execute("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["details"] = json.loads(d["details_json"])
        del d["details_json"]
        result.append(d)
    return result

def update_document_review(doc_id: str, reviewer: str, decision: str, notes: str, updated_processed_data: Dict[str, Any]):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE documents
        SET is_reviewed = 1,
            reviewer_name = ?,
            overall_decision = ?,
            review_notes = ?,
            processed_data_json = ?
        WHERE id = ?
    """, (
        reviewer,
        decision,
        notes,
        json.dumps(updated_processed_data),
        doc_id
    ))
    conn.commit()
    conn.close()

# =============================================================================
# BRSR Reports & Observations Database Operations
# =============================================================================

def save_brsr_report(r: Dict[str, Any]):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO brsr_reports (
            report_id, company_name, industry, financial_year, report_title,
            report_category, source_url, local_file_path, file_hash_sha256,
            file_size_bytes, page_count, upload_status, processing_status,
            error_message, document_type, created_at, parsed_data_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        r["report_id"],
        r["company_name"],
        r.get("industry", "Diversified"),
        r["financial_year"],
        r.get("report_title", "BRSR Report"),
        r.get("report_category", "BRSR Report"),
        r.get("source_url", ""),
        r["local_file_path"],
        r["file_hash_sha256"],
        r.get("file_size_bytes", 0),
        r.get("page_count", 0),
        r.get("upload_status", "COMPLETED"),
        r.get("processing_status", "READY_FOR_PARSING"),
        r.get("error_message", None),
        r.get("document_type", "BRSR Report"),
        r.get("created_at", datetime.utcnow().isoformat()),
        json.dumps(r.get("parsed_data", {})) if "parsed_data" in r else r.get("parsed_data_json", "{}")
    ))
    conn.commit()
    conn.close()

def get_brsr_report(report_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM brsr_reports WHERE report_id = ?", (report_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    if d.get("parsed_data_json"):
        try:
            d["parsed_data"] = json.loads(d["parsed_data_json"])
        except Exception:
            d["parsed_data"] = {}
    return d

def get_brsr_report_by_hash(file_hash: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM brsr_reports WHERE file_hash_sha256 = ?", (file_hash,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    if d.get("parsed_data_json"):
        try:
            d["parsed_data"] = json.loads(d["parsed_data_json"])
        except Exception:
            d["parsed_data"] = {}
    return d

def list_brsr_reports(company_filter: Optional[str] = None, year_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM brsr_reports WHERE 1=1"
    params = []
    if company_filter:
        query += " AND company_name LIKE ?"
        params.append(f"%{company_filter}%")
    if year_filter:
        query += " AND financial_year = ?"
        params.append(year_filter)
    query += " ORDER BY company_name ASC, financial_year DESC"
    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()
    results = []
    for r in rows:
        d = dict(r)
        if d.get("parsed_data_json"):
            try:
                d["parsed_data"] = json.loads(d["parsed_data_json"])
            except Exception:
                d["parsed_data"] = {}
        results.append(d)
    return results

def save_brsr_observations(observations: List[Dict[str, Any]]):
    conn = get_db_connection()
    cursor = conn.cursor()
    if observations:
        rep_id = observations[0].get("report_id")
        if rep_id:
            cursor.execute("DELETE FROM brsr_observations WHERE report_id = ?", (rep_id,))
    for obs in observations:
        cursor.execute("""
            INSERT OR REPLACE INTO brsr_observations (
                observation_id, report_id, company_name, industry, financial_year,
                report_type, section_name, esg_category, indicator_code, indicator_name,
                reported_value, numeric_value, unit, normalized_value, normalized_unit,
                reporting_period, reporting_boundary, brsr_principle, brsr_core_indicator,
                source_page, source_text, extraction_method, classification_status,
                extraction_status, confidence_score, review_status, manual_correction_notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            obs["observation_id"],
            obs["report_id"],
            obs["company_name"],
            obs.get("industry"),
            obs["financial_year"],
            obs.get("report_type", "BRSR Report"),
            obs.get("section_name", ""),
            obs["esg_category"],
            obs["indicator_code"],
            obs["indicator_name"],
            str(obs["reported_value"]),
            obs.get("numeric_value"),
            obs.get("unit"),
            obs.get("normalized_value"),
            obs.get("normalized_unit"),
            obs.get("reporting_period"),
            obs.get("reporting_boundary", "Standalone"),
            obs.get("brsr_principle"),
            obs.get("brsr_core_indicator"),
            obs.get("source_page", 1),
            obs.get("source_text", ""),
            obs.get("extraction_method", "TABLE_PARSING"),
            obs.get("classification_status", "High-confidence rule match"),
            obs.get("extraction_status", "EXTRACTED"),
            obs.get("confidence_score", 0.90),
            obs.get("review_status", "AUTO_VERIFIED"),
            obs.get("manual_correction_notes")
        ))
    conn.commit()
    conn.close()

def get_brsr_observations(
    report_id: Optional[str] = None,
    company_name: Optional[str] = None,
    esg_category: Optional[str] = None,
    indicator_code: Optional[str] = None,
    principle: Optional[str] = None,
    review_status: Optional[str] = None
) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM brsr_observations WHERE 1=1"
    params = []
    if report_id:
        query += " AND report_id = ?"
        params.append(report_id)
    if company_name:
        query += " AND company_name LIKE ?"
        params.append(f"%{company_name}%")
    if esg_category:
        query += " AND esg_category = ?"
        params.append(esg_category)
    if indicator_code:
        query += " AND indicator_code = ?"
        params.append(indicator_code)
    if principle:
        query += " AND brsr_principle LIKE ?"
        params.append(f"%{principle}%")
    if review_status:
        query += " AND review_status = ?"
        params.append(review_status)
    query += " ORDER BY esg_category ASC, indicator_code ASC"
    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_brsr_observation(observation_id: str, updates: Dict[str, Any]):
    conn = get_db_connection()
    cursor = conn.cursor()
    set_clauses = []
    params = []
    for k, v in updates.items():
        set_clauses.append(f"{k} = ?")
        params.append(v)
    params.append(observation_id)
    cursor.execute(f"UPDATE brsr_observations SET {', '.join(set_clauses)} WHERE observation_id = ?", tuple(params))
    conn.commit()
    conn.close()

