import os
from pathlib import Path
import fitz  # PyMuPDF

def generate_sample_documents(output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Clean Invoice (INV-10245) - Matching user spec example
    doc1 = fitz.open()
    page1 = doc1.new_page(width=595, height=842)  # A4

    page1.insert_text((50, 60), "TAX INVOICE", fontsize=20, fontname="helv", color=(0.1, 0.2, 0.5))
    page1.insert_text((50, 90), "ABC Technologies Pvt Ltd", fontsize=14, fontname="helv", color=(0, 0, 0))
    page1.insert_text((50, 105), "42 Cyber Park, Outer Ring Road, Bangalore - 560103", fontsize=10, fontname="helv", color=(0.3, 0.3, 0.3))
    page1.insert_text((50, 120), "GSTIN: 29ABCDE1234F1Z5 | Email: billing@abctech.com", fontsize=10, fontname="helv", color=(0.3, 0.3, 0.3))

    page1.insert_text((380, 90), "Invoice Number: INV-10245", fontsize=11, fontname="helv", color=(0, 0, 0))
    page1.insert_text((380, 105), "Invoice Date: 12/09/2026", fontsize=11, fontname="helv", color=(0, 0, 0))
    page1.insert_text((380, 120), "Due Date: 28/09/2026", fontsize=11, fontname="helv", color=(0, 0, 0))

    page1.draw_line((50, 140), (545, 140), color=(0.8, 0.8, 0.8), width=1)

    page1.insert_text((50, 165), "Bill To:", fontsize=11, fontname="helv", color=(0.1, 0.2, 0.5))
    page1.insert_text((50, 180), "Nexus Enterprise Solutions", fontsize=11, fontname="helv", color=(0, 0, 0))
    page1.insert_text((50, 195), "18 Tech Zone, Whitefield, Bangalore", fontsize=10, fontname="helv", color=(0.3, 0.3, 0.3))

    # Table Header
    page1.draw_rect(fitz.Rect(50, 230, 545, 255), color=(0.93, 0.95, 0.98), fill=(0.93, 0.95, 0.98))
    page1.insert_text((60, 247), "Item Description", fontsize=10, fontname="helv", color=(0.1, 0.2, 0.5))
    page1.insert_text((310, 247), "Qty", fontsize=10, fontname="helv", color=(0.1, 0.2, 0.5))
    page1.insert_text((380, 247), "Unit Price", fontsize=10, fontname="helv", color=(0.1, 0.2, 0.5))
    page1.insert_text((470, 247), "Line Total", fontsize=10, fontname="helv", color=(0.1, 0.2, 0.5))

    # Table Rows
    # Item 1: Cloud Server Instance | 2 | 20,000 | 40,000
    page1.insert_text((60, 280), "Cloud Server Instance 8-Core", fontsize=10, fontname="helv")
    page1.insert_text((315, 280), "2", fontsize=10, fontname="helv")
    page1.insert_text((380, 280), "20,000.00", fontsize=10, fontname="helv")
    page1.insert_text((470, 280), "40,000.00", fontsize=10, fontname="helv")

    # Item 2: Secure SSL Certificate | 5 | 1,000 | 5,000
    page1.insert_text((60, 310), "Secure SSL Wildcard Certificate", fontsize=10, fontname="helv")
    page1.insert_text((315, 310), "5", fontsize=10, fontname="helv")
    page1.insert_text((380, 310), "1,000.00", fontsize=10, fontname="helv")
    page1.insert_text((470, 310), "5,000.00", fontsize=10, fontname="helv")

    page1.draw_line((50, 340), (545, 340), color=(0.8, 0.8, 0.8), width=1)

    # Totals
    page1.insert_text((350, 370), "Subtotal Amount: INR 45,000.00", fontsize=10, fontname="helv")
    page1.insert_text((350, 390), "Tax Amount (GST 18%): INR 800.00", fontsize=10, fontname="helv")
    page1.draw_rect(fitz.Rect(340, 410, 545, 440), color=(0.9, 0.94, 1.0), fill=(0.9, 0.94, 1.0))
    page1.insert_text((350, 430), "Total Amount: INR 45,800.00", fontsize=12, fontname="helv", color=(0.1, 0.2, 0.6))

    page1.insert_text((50, 500), "Payment Terms: Net 30 Days", fontsize=9, fontname="helv", color=(0.4, 0.4, 0.4))
    page1.insert_text((50, 515), "Authorized Signatory: Dr. Rajesh Kumar, CFO", fontsize=9, fontname="helv", color=(0.4, 0.4, 0.4))

    doc1.save(str(output_dir / "clean_invoice_10245.pdf"))
    doc1.close()

    # 2. Anomalous Invoice (Math Mismatch: Total ₹58,500 vs items ₹45,800 + Missing GST)
    doc2 = fitz.open()
    page2 = doc2.new_page(width=595, height=842)
    page2.insert_text((50, 60), "TAX INVOICE", fontsize=20, fontname="helv", color=(0.6, 0.1, 0.1))
    page2.insert_text((50, 90), "Apex Global Hardware Systems", fontsize=14, fontname="helv")
    page2.insert_text((380, 90), "Invoice Number: INV-99201", fontsize=11, fontname="helv")
    page2.insert_text((380, 105), "Invoice Date: 15/10/2026", fontsize=11, fontname="helv")
    page2.insert_text((380, 120), "Due Date: 01/10/2026", fontsize=11, fontname="helv") # Chronology inversion!

    page2.draw_line((50, 140), (545, 140), color=(0.8, 0.8, 0.8), width=1)
    page2.insert_text((50, 165), "Bill To: Horizon Analytics Ltd", fontsize=11, fontname="helv")

    # Table
    page2.draw_rect(fitz.Rect(50, 200, 545, 225), color=(0.95, 0.95, 0.95), fill=(0.95, 0.95, 0.95))
    page2.insert_text((60, 217), "Item Description", fontsize=10, fontname="helv")
    page2.insert_text((310, 217), "Qty", fontsize=10, fontname="helv")
    page2.insert_text((380, 217), "Unit Price", fontsize=10, fontname="helv")
    page2.insert_text((470, 217), "Line Total", fontsize=10, fontname="helv")

    # Item: Laptop 2 * 20000 = 40000
    page2.insert_text((60, 245), "Development Laptop Pro", fontsize=10, fontname="helv")
    page2.insert_text((315, 245), "2", fontsize=10, fontname="helv")
    page2.insert_text((380, 245), "20,000.00", fontsize=10, fontname="helv")
    page2.insert_text((470, 245), "40,000.00", fontsize=10, fontname="helv")

    # Item: Optical Mouse 5 * 500 = 2500 (but printed as 3500 line item error)
    page2.insert_text((60, 275), "Optical Mouse Ergonomic", fontsize=10, fontname="helv")
    page2.insert_text((315, 275), "5", fontsize=10, fontname="helv")
    page2.insert_text((380, 275), "500.00", fontsize=10, fontname="helv")
    page2.insert_text((470, 275), "3,500.00", fontsize=10, fontname="helv") # 5 * 500 != 3500!

    page2.draw_line((50, 305), (545, 305), color=(0.8, 0.8, 0.8), width=1)
    page2.insert_text((350, 335), "Subtotal Amount: INR 43,500.00", fontsize=10, fontname="helv")
    page2.insert_text((350, 355), "Tax Amount: INR 2,300.00", fontsize=10, fontname="helv")
    # Fabricated / inconsistent grand total:
    page2.insert_text((350, 385), "Total Amount: INR 58,500.00", fontsize=12, fontname="helv", color=(0.7, 0.1, 0.1))

    doc2.save(str(output_dir / "anomalous_invoice_math_error.pdf"))
    doc2.close()

    # 3. Academic Certificate
    doc3 = fitz.open()
    page3 = doc3.new_page(width=842, height=595)  # Landscape A4
    page3.draw_rect(fitz.Rect(30, 30, 812, 565), color=(0.6, 0.45, 0.1), width=3)
    page3.draw_rect(fitz.Rect(36, 36, 806, 559), color=(0.8, 0.7, 0.3), width=1)

    page3.insert_text((220, 100), "NATIONAL INSTITUTE OF TECHNOLOGY", fontsize=20, fontname="times-bold", color=(0.1, 0.15, 0.3))
    page3.insert_text((320, 130), "PROVISIONAL DEGREE CERTIFICATE", fontsize=14, fontname="times-bold", color=(0.5, 0.35, 0.1))

    page3.insert_text((150, 200), "This is to certify that", fontsize=13, fontname="times-roman")
    page3.insert_text((320, 200), "PUNYASHREE S", fontsize=17, fontname="times-bold", color=(0.0, 0.1, 0.4))
    
    page3.insert_text((150, 240), "has successfully completed the curriculum and conferred the degree of", fontsize=13, fontname="times-roman")
    page3.insert_text((230, 275), "MASTER OF COMPUTER APPLICATIONS (MCA)", fontsize=16, fontname="times-bold", color=(0.1, 0.2, 0.5))

    page3.insert_text((150, 330), "Certificate Number: NIT-MCA-2026-884", fontsize=12, fontname="times-bold")
    page3.insert_text((520, 330), "Date of Issue: 18/08/2026", fontsize=12, fontname="times-bold")
    page3.insert_text((150, 370), "Grade: First Class with Distinction (CGPA 9.42)", fontsize=12, fontname="times-bold")

    page3.insert_text((150, 480), "Authorized Signatory: Prof. K. R. Sharma", fontsize=11, fontname="times-italic")
    page3.insert_text((550, 480), "Dean (Academic Affairs): Dr. V. Sen", fontsize=11, fontname="times-italic")

    doc3.save(str(output_dir / "sample_certificate.pdf"))
    doc3.close()

    # 4. Application Form
    doc4 = fitz.open()
    page4 = doc4.new_page(width=595, height=842)
    page4.insert_text((160, 60), "ADMISSION APPLICATION FORM", fontsize=16, fontname="helv", color=(0.1, 0.2, 0.5))
    page4.insert_text((190, 85), "Academic Year 2026 - 2027", fontsize=12, fontname="helv", color=(0.3, 0.3, 0.3))

    page4.draw_rect(fitz.Rect(50, 110, 545, 140), color=(0.9, 0.92, 0.96), fill=(0.9, 0.92, 0.96))
    page4.insert_text((60, 130), "Personal & Academic Credentials", fontsize=11, fontname="helv", color=(0.1, 0.2, 0.5))

    page4.insert_text((60, 175), "Applicant Name: Punyashree S", fontsize=11, fontname="helv")
    page4.insert_text((340, 175), "Application ID: APP-2026-9481", fontsize=11, fontname="helv")

    page4.insert_text((60, 215), "Date of Birth: 14/05/2003", fontsize=11, fontname="helv")
    page4.insert_text((340, 215), "Submission Date: 05/06/2026", fontsize=11, fontname="helv")

    page4.insert_text((60, 255), "Email Address: punyashree.s@domain.edu", fontsize=11, fontname="helv")
    page4.insert_text((340, 255), "Phone Number: +91-9876543210", fontsize=11, fontname="helv")

    page4.insert_text((60, 295), "Applied Position: Master of Computer Applications (MCA)", fontsize=11, fontname="helv")
    page4.insert_text((60, 335), "Eligibility Status: Eligible for Direct Merit Round", fontsize=11, fontname="helv")

    page4.draw_line((50, 370), (545, 370), color=(0.8, 0.8, 0.8), width=1)
    page4.insert_text((60, 400), "Declaration: I hereby declare that all information furnished is true and verifiable.", fontsize=9, fontname="helv", color=(0.4, 0.4, 0.4))
    page4.insert_text((60, 440), "Signature of Applicant: Punyashree S", fontsize=10, fontname="helv")

    doc4.save(str(output_dir / "sample_application_form.pdf"))
    doc4.close()

    print("Sample test documents successfully generated in:", output_dir)

if __name__ == "__main__":
    current_dir = Path(__file__).resolve().parent
    generate_sample_documents(current_dir)
