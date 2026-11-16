import os
from typing import List, Dict, Any, Optional
import fitz  # PyMuPDF
from PIL import Image

class OCREngine:
    """
    Hybrid OCR & Document Text Extraction Engine:
    - Primary: PyMuPDF high-fidelity text extraction with exact word & block bounding boxes.
    - Secondary: EasyOCR / Tesseract for image-based or rasterized scans.
    """

    def __init__(self):
        self._easyocr_reader = None

    def _get_easyocr_reader(self):
        if self._easyocr_reader is None:
            try:
                import easyocr
                # Use CPU mode for compatibility
                self._easyocr_reader = easyocr.Reader(['en'], gpu=False)
            except Exception as e:
                print(f"[OCR] EasyOCR init skipped/failed: {e}")
                self._easyocr_reader = False
        return self._easyocr_reader if self._easyocr_reader is not False else None

    def extract_document_tokens(self, file_path: str, pages_info: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extracts all words, lines, bounding boxes and confidence scores across all pages.
        Returns:
            {
                "full_text": str,
                "pages": [
                    {
                        "page_number": int,
                        "text": str,
                        "words": [
                            {
                                "text": str,
                                "bbox": [ymin, xmin, ymax, xmax],  # normalized 0-1
                                "pixel_bbox": [x0, y0, x1, y1],
                                "confidence": float
                            }
                        ],
                        "lines": [
                            {
                                "text": str,
                                "bbox": [ymin, xmin, ymax, xmax],
                                "pixel_bbox": [x0, y0, x1, y1]
                            }
                        ]
                    }
                ]
            }
        """
        is_pdf = file_path.lower().endswith(".pdf")
        doc_tokens = {"full_text": "", "pages": []}
        full_text_parts = []

        if is_pdf:
            doc = fitz.open(file_path)
            for page_idx, page in enumerate(doc):
                page_num = page_idx + 1
                page_rect = page.rect
                page_w = page_rect.width
                page_h = page_rect.height

                # Extract words: (x0, y0, x1, y1, word, block_no, line_no, word_no)
                raw_words = page.get_text("words")
                
                # If digital text exists:
                if len(raw_words) > 5:
                    page_words = []
                    for w in raw_words:
                        x0, y0, x1, y1, word_text = w[0], w[1], w[2], w[3], w[4]
                        norm_bbox = [
                            max(0.0, min(1.0, y0 / page_h)),
                            max(0.0, min(1.0, x0 / page_w)),
                            max(0.0, min(1.0, y1 / page_h)),
                            max(0.0, min(1.0, x1 / page_w))
                        ]
                        page_words.append({
                            "text": word_text,
                            "bbox": norm_bbox,
                            "pixel_bbox": [int(x0), int(y0), int(x1), int(y1)],
                            "confidence": 0.98,
                            "block_no": w[5],
                            "line_no": w[6]
                        })

                    # Extract blocks/lines
                    blocks = page.get_text("blocks")
                    page_lines = []
                    for b in blocks:
                        bx0, by0, bx1, by1, btext = b[0], b[1], b[2], b[3], b[4]
                        norm_b_bbox = [
                            max(0.0, min(1.0, by0 / page_h)),
                            max(0.0, min(1.0, bx0 / page_w)),
                            max(0.0, min(1.0, by1 / page_h)),
                            max(0.0, min(1.0, bx1 / page_w))
                        ]
                        page_lines.append({
                            "text": btext.strip(),
                            "bbox": norm_b_bbox,
                            "pixel_bbox": [int(bx0), int(by0), int(bx1), int(by1)]
                        })

                    raw_page_text = page.get_text("text")
                    full_text_parts.append(raw_page_text)
                    doc_tokens["pages"].append({
                        "page_number": page_num,
                        "text": raw_page_text,
                        "words": page_words,
                        "lines": page_lines
                    })
                else:
                    # Scanned PDF page: run OCR on rendered preview image
                    preview_path = pages_info[page_idx]["preview_path"]
                    ocr_res = self._ocr_image(preview_path, page_num)
                    doc_tokens["pages"].append(ocr_res)
                    full_text_parts.append(ocr_res["text"])

            doc.close()
        else:
            # Single image file
            preview_path = pages_info[0]["preview_path"]
            ocr_res = self._ocr_image(preview_path, 1)
            doc_tokens["pages"].append(ocr_res)
            full_text_parts.append(ocr_res["text"])

        doc_tokens["full_text"] = "\n\n--- PAGE BREAK ---\n\n".join(full_text_parts)
        return doc_tokens

    def _ocr_image(self, image_path: str, page_num: int) -> Dict[str, Any]:
        """Runs OCR on an image file using EasyOCR, pytesseract, or fallback."""
        img = Image.open(image_path)
        img_w, img_h = img.width, img.height
        words = []
        lines = []
        collected_text = []

        reader = self._get_easyocr_reader()
        if reader is not None:
            try:
                # easyocr output: [([ [x0,y0],[x1,y1],[x2,y2],[x3,y3] ], text, conf), ...]
                results = reader.readtext(image_path)
                for bbox_poly, text_val, conf in results:
                    x_coords = [p[0] for p in bbox_poly]
                    y_coords = [p[1] for p in bbox_poly]
                    x0, x1 = min(x_coords), max(x_coords)
                    y0, y1 = min(y_coords), max(y_coords)

                    norm_bbox = [
                        max(0.0, min(1.0, y0 / img_h)),
                        max(0.0, min(1.0, x0 / img_w)),
                        max(0.0, min(1.0, y1 / img_h)),
                        max(0.0, min(1.0, x1 / img_w))
                    ]
                    words.append({
                        "text": text_val,
                        "bbox": norm_bbox,
                        "pixel_bbox": [int(x0), int(y0), int(x1), int(y1)],
                        "confidence": float(conf)
                    })
                    collected_text.append(text_val)

                return {
                    "page_number": page_num,
                    "text": "\n".join(collected_text),
                    "words": words,
                    "lines": [{"text": t, "bbox": [0,0,1,1], "pixel_bbox": [0,0,img_w,img_h]} for t in collected_text]
                }
            except Exception as e:
                print(f"[OCR] EasyOCR image processing failed: {e}")

        # Fallback to pytesseract if installed
        try:
            import pytesseract
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            n_boxes = len(data['text'])
            for i in range(n_boxes):
                text_word = data['text'][i].strip()
                if not text_word:
                    continue
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                conf = float(data['conf'][i]) / 100.0 if float(data['conf'][i]) > 0 else 0.5
                norm_bbox = [
                    max(0.0, min(1.0, y / img_h)),
                    max(0.0, min(1.0, x / img_w)),
                    max(0.0, min(1.0, (y + h) / img_h)),
                    max(0.0, min(1.0, (x + w) / img_w))
                ]
                words.append({
                    "text": text_word,
                    "bbox": norm_bbox,
                    "pixel_bbox": [int(x), int(y), int(x + w), int(y + h)],
                    "confidence": conf
                })
                collected_text.append(text_word)

            return {
                "page_number": page_num,
                "text": " ".join(collected_text),
                "words": words,
                "lines": []
            }
        except Exception:
            pass

        return {
            "page_number": page_num,
            "text": " ".join(collected_text),
            "words": words,
            "lines": []
        }
