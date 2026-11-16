import os
import uuid
import shutil
from pathlib import Path
from typing import List, Dict, Any, Tuple
import fitz  # PyMuPDF
from PIL import Image
from app.config import UPLOAD_DIR

class DocumentIngestionService:
    """Handles ingestion of PDF documents and scanned images, generating page previews."""

    @staticmethod
    def process_upload(file_bytes: bytes, filename: str) -> Dict[str, Any]:
        doc_id = f"doc_{uuid.uuid4().hex[:12]}"
        doc_dir = UPLOAD_DIR / doc_id
        previews_dir = doc_dir / "previews"
        doc_dir.mkdir(parents=True, exist_ok=True)
        previews_dir.mkdir(parents=True, exist_ok=True)

        original_ext = Path(filename).suffix.lower()
        if not original_ext:
            original_ext = ".pdf"
        saved_filename = f"original{original_ext}"
        saved_path = doc_dir / saved_filename

        with open(saved_path, "wb") as f:
            f.write(file_bytes)

        pages_info: List[Dict[str, Any]] = []
        is_pdf = original_ext == ".pdf"

        if is_pdf:
            doc = fitz.open(str(saved_path))
            page_count = len(doc)
            for page_idx in range(page_count):
                page = doc[page_idx]
                rect = page.rect
                # Render to high-resolution PNG preview (150 DPI for crisp visual inspection)
                pix = page.get_pixmap(dpi=150)
                preview_filename = f"page_{page_idx + 1}.png"
                preview_path = previews_dir / preview_filename
                pix.save(str(preview_path))

                pages_info.append({
                    "page_number": page_idx + 1,
                    "width": rect.width,
                    "height": rect.height,
                    "preview_width": pix.width,
                    "preview_height": pix.height,
                    "preview_path": str(preview_path),
                    "preview_url": f"/api/documents/{doc_id}/pages/{page_idx + 1}/preview"
                })
            doc.close()
        else:
            # Single image file (JPG, PNG, TIFF)
            img = Image.open(str(saved_path))
            page_count = 1
            preview_filename = "page_1.png"
            preview_path = previews_dir / preview_filename
            img.save(str(preview_path), format="PNG")
            
            pages_info.append({
                "page_number": 1,
                "width": img.width,
                "height": img.height,
                "preview_width": img.width,
                "preview_height": img.height,
                "preview_path": str(preview_path),
                "preview_url": f"/api/documents/{doc_id}/pages/1/preview"
            })

        return {
            "document_id": doc_id,
            "filename": filename,
            "file_path": str(saved_path),
            "doc_dir": str(doc_dir),
            "is_pdf": is_pdf,
            "page_count": page_count,
            "pages": pages_info
        }
