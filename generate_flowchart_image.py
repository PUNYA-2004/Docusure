import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

def draw_flowchart(output_png: Path, output_pdf: Path):
    # Set high DPI and large canvas for crisp presentation quality
    fig, ax = plt.subplots(figsize=(14, 28), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Color Palette
    BG_COLOR = "#0B0F19"
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    COLOR_START_END = "#1E3A8A"        # Deep Royal Blue
    BORDER_START_END = "#60A5FA"       # Light Blue Accent
    COLOR_PROCESS = "#111827"          # Dark Slate
    BORDER_PROCESS = "#374151"         # Slate Border
    COLOR_DECISION = "#312E81"         # Indigo
    BORDER_DECISION = "#818CF8"        # Light Indigo
    COLOR_BRANCH = "#064E3B"           # Emerald
    BORDER_BRANCH = "#34D399"          # Emerald Border
    COLOR_TEXT = "#F9FAFB"             # Off-white
    COLOR_ARROW = "#94A3B8"            # Slate Gray Arrow
    COLOR_LABEL_YES = "#34D399"        # Green
    COLOR_LABEL_NO = "#F87171"         # Red

    # Header Title
    ax.text(50, 98.2, "DOCUSURE — SYSTEM EXECUTION FLOWCHART", 
            ha='center', va='center', color='#FFFFFF', fontsize=20, fontweight='bold', fontfamily='sans-serif')
    ax.text(50, 96.8, "Intelligent Document Processing, Information Extraction and Verification Using Generative AI", 
            ha='center', va='center', color='#93C5FD', fontsize=11, fontfamily='sans-serif')

    # Helper function to draw rounded process rectangle
    def draw_box(x, y, w, h, text, subtext="", bg=COLOR_PROCESS, border=BORDER_PROCESS, text_color=COLOR_TEXT):
        box = patches.FancyBboxPatch(
            (x - w/2, y - h/2), w, h,
            boxstyle="round,pad=0.5,rounding_size=1.0",
            facecolor=bg, edgecolor=border, linewidth=2.0, zorder=3
        )
        ax.add_patch(box)
        if subtext:
            ax.text(x, y + 0.35, text, ha='center', va='center', color=text_color, fontsize=11, fontweight='bold', zorder=4)
            ax.text(x, y - 0.55, subtext, ha='center', va='center', color='#94A3B8', fontsize=9, zorder=4)
        else:
            ax.text(x, y, text, ha='center', va='center', color=text_color, fontsize=11, fontweight='bold', zorder=4)

    # Helper function to draw terminal oval (Start/End)
    def draw_terminal(x, y, w, h, text):
        box = patches.FancyBboxPatch(
            (x - w/2, y - h/2), w, h,
            boxstyle="round,pad=0.8,rounding_size=1.6",
            facecolor=COLOR_START_END, edgecolor=BORDER_START_END, linewidth=2.5, zorder=3
        )
        ax.add_patch(box)
        ax.text(x, y, text, ha='center', va='center', color='#FFFFFF', fontsize=13, fontweight='bold', zorder=4)

    # Helper function to draw diamond decision node
    def draw_diamond(x, y, w, h, text, subtext=""):
        poly = patches.Polygon([
            (x, y + h/2),
            (x + w/2, y),
            (x, y - h/2),
            (x - w/2, y)
        ], closed=True, facecolor=COLOR_DECISION, edgecolor=BORDER_DECISION, linewidth=2.2, zorder=3)
        ax.add_patch(poly)
        if subtext:
            ax.text(x, y + 0.35, text, ha='center', va='center', color='#FFFFFF', fontsize=10.5, fontweight='bold', zorder=4)
            ax.text(x, y - 0.45, subtext, ha='center', va='center', color='#C7D2FE', fontsize=9, zorder=4)
        else:
            ax.text(x, y, text, ha='center', va='center', color='#FFFFFF', fontsize=10.5, fontweight='bold', zorder=4)

    # Helper function to draw clean arrow
    def draw_arrow(x1, y1, x2, y2, label="", label_color="#CBD5E1", label_pos="right", offset=1.2):
        ax.annotate(
            "", xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(arrowstyle="-|>", color=COLOR_ARROW, lw=2.0, mutation_scale=15),
            zorder=2
        )
        if label:
            mx = (x1 + x2) / 2
            my = (y1 + y2) / 2
            lx = mx + offset if label_pos == "right" else mx - offset
            ax.text(lx, my, label, ha='center', va='center', color=label_color, fontsize=10, fontweight='bold', zorder=5)

    # Coordinates layout (Centering x = 40 for main trunk to leave room for restoration branch on right)
    TRUNK_X = 40.0
    BRANCH_X = 76.0

    # Vertical coordinates for each node
    y_start         = 94.0
    y_upload        = 89.5
    y_input         = 85.0
    y_ingest        = 80.5
    y_render        = 76.0
    y_preproc       = 71.5
    y_ocr           = 67.0
    y_spatial       = 62.5
    y_classify      = 58.0
    y_extract       = 53.5
    y_parse         = 49.0
    y_evidence      = 44.5
    y_verify        = 40.0
    y_confidence    = 35.5
    y_anomaly       = 31.0
    y_quality       = 26.5   # Diamond 1

    # Restoration Branch
    y_restore       = 26.5
    y_reprocess     = 21.5

    y_verified_ext  = 21.5   # Merged node
    y_summary       = 17.0
    y_review        = 12.5   # Diamond 2: Human Review

    # Human Review Actions
    y_actions       = 8.0
    x_accept        = 28.0
    x_edit          = 52.0

    y_audit         = 4.5
    y_final         = 1.5    # Bottom box
    y_end           = -1.5   # We will fit within 0 to 100 by scaling coordinates

    # Let's adjust vertical coordinates smoothly from 94.0 down to 3.0:
    nodes_y = [
        94.0,  # 0: Start
        90.0,  # 1: Upload Document
        86.0,  # 2: PDF / Image Input
        82.0,  # 3: Document Ingestion
        78.0,  # 4: Page Rendering / Loading
        74.0,  # 5: Image Preprocessing
        70.0,  # 6: OCR
        66.0,  # 7: Text + Spatial Information
        62.0,  # 8: Document Type Classification
        58.0,  # 9: Structured Information Extraction
        54.0,  # 10: Table / Field Parsing
        50.0,  # 11: Evidence Attribution
        46.0,  # 12: Verification
        42.0,  # 13: Confidence Estimation
        38.0,  # 14: Anomaly Detection
        33.5,  # 15: Quality Check (Diamond)
        28.0,  # 16: Verified Extraction (Main)
        23.5,  # 17: Human-Readable Summary
        18.5,  # 18: Human Review (Diamond)
        13.5,  # 19: Accept / Edit Actions
        9.0,   # 20: Audit Trail
        5.2,   # 21: Final Results
        2.0    # 22: END
    ]

    BOX_W = 32.0
    BOX_H = 2.4

    # 0. START
    draw_terminal(TRUNK_X, nodes_y[0], 16.0, 2.2, "START")
    draw_arrow(TRUNK_X, nodes_y[0] - 1.1, TRUNK_X, nodes_y[1] + 1.2)

    # 1. Upload Document
    draw_box(TRUNK_X, nodes_y[1], BOX_W, BOX_H, "Upload Document", "Multi-page PDF or Raster Image upload")
    draw_arrow(TRUNK_X, nodes_y[1] - 1.2, TRUNK_X, nodes_y[2] + 1.2)

    # 2. PDF / Image Input
    draw_box(TRUNK_X, nodes_y[2], BOX_W, BOX_H, "PDF / Image Input", "Binary file stream ingestion & validation")
    draw_arrow(TRUNK_X, nodes_y[2] - 1.2, TRUNK_X, nodes_y[3] + 1.2)

    # 3. Document Ingestion
    draw_box(TRUNK_X, nodes_y[3], BOX_W, BOX_H, "Document Ingestion", "Document ID assignment & path isolation")
    draw_arrow(TRUNK_X, nodes_y[3] - 1.2, TRUNK_X, nodes_y[4] + 1.2)

    # 4. Page Rendering / Loading
    draw_box(TRUNK_X, nodes_y[4], BOX_W, BOX_H, "Page Rendering / Loading", "150 DPI high-res page image generation")
    draw_arrow(TRUNK_X, nodes_y[4] - 1.2, TRUNK_X, nodes_y[5] + 1.2)

    # 5. Image Preprocessing
    draw_box(TRUNK_X, nodes_y[5], BOX_W, BOX_H, "Image Preprocessing", "Deskewing • Denoising • CLAHE Enhancement")
    draw_arrow(TRUNK_X, nodes_y[5] - 1.2, TRUNK_X, nodes_y[6] + 1.2)

    # 6. OCR
    draw_box(TRUNK_X, nodes_y[6], BOX_W, BOX_H, "OCR Extraction", "Character & token recognition engine")
    draw_arrow(TRUNK_X, nodes_y[6] - 1.2, TRUNK_X, nodes_y[7] + 1.2)

    # 7. Text + Spatial Information
    draw_box(TRUNK_X, nodes_y[7], BOX_W, BOX_H, "Text + Spatial Information", "Character spans, word coordinates, bounding boxes")
    draw_arrow(TRUNK_X, nodes_y[7] - 1.2, TRUNK_X, nodes_y[8] + 1.2)

    # 8. Document Type Classification
    draw_box(TRUNK_X, nodes_y[8], BOX_W, BOX_H, "Document Type Classification", "Invoices • Certificates • Forms • Receipts")
    draw_arrow(TRUNK_X, nodes_y[8] - 1.2, TRUNK_X, nodes_y[9] + 1.2)

    # 9. Structured Information Extraction
    draw_box(TRUNK_X, nodes_y[9], BOX_W, BOX_H, "Structured Information Extraction", "Schema mapping & hallucination prevention")
    draw_arrow(TRUNK_X, nodes_y[9] - 1.2, TRUNK_X, nodes_y[10] + 1.2)

    # 10. Table / Field Parsing
    draw_box(TRUNK_X, nodes_y[10], BOX_W, BOX_H, "Table / Field Parsing", "Line-item row extraction & key-value pairs")
    draw_arrow(TRUNK_X, nodes_y[10] - 1.2, TRUNK_X, nodes_y[11] + 1.2)

    # 11. Evidence Attribution
    draw_box(TRUNK_X, nodes_y[11], BOX_W, BOX_H, "Evidence Attribution", "Source page, text snippet & [ymin, xmin, ymax, xmax]")
    draw_arrow(TRUNK_X, nodes_y[11] - 1.2, TRUNK_X, nodes_y[12] + 1.2)

    # 12. Verification
    draw_box(TRUNK_X, nodes_y[12], BOX_W, BOX_H, "Verification Engine", "SUPPORTED • CONTRADICTED • UNSUPPORTED • UNCERTAIN")
    draw_arrow(TRUNK_X, nodes_y[12] - 1.2, TRUNK_X, nodes_y[13] + 1.2)

    # 13. Confidence Estimation
    draw_box(TRUNK_X, nodes_y[13], BOX_W, BOX_H, "Confidence Estimation", "Multi-signal calibration & reliability binning")
    draw_arrow(TRUNK_X, nodes_y[13] - 1.2, TRUNK_X, nodes_y[14] + 1.2)

    # 14. Anomaly Detection
    draw_box(TRUNK_X, nodes_y[14], BOX_W, BOX_H, "Anomaly Detection", "Math consistency • Date logic • Explainable warnings")
    draw_arrow(TRUNK_X, nodes_y[14] - 1.2, TRUNK_X, nodes_y[15] + 2.0)

    # 15. Decision Diamond: Is Document Quality Sufficient?
    draw_diamond(TRUNK_X, nodes_y[15], 26.0, 4.0, "Is Document Quality", "Sufficient?")

    # Branch 1: YES -> down to Verified Extraction
    draw_arrow(TRUNK_X, nodes_y[15] - 2.0, TRUNK_X, nodes_y[16] + 1.2, label="YES", label_color=COLOR_LABEL_YES, offset=2.5)

    # Branch 2: NO -> right to Restoration / Preprocessing
    ax.annotate(
        "", xy=(BRANCH_X - 14.0, nodes_y[15]), xytext=(TRUNK_X + 13.0, nodes_y[15]),
        arrowprops=dict(arrowstyle="-|>", color=COLOR_ARROW, lw=2.0, mutation_scale=15),
        zorder=2
    )
    ax.text((TRUNK_X + 13.0 + BRANCH_X - 14.0) / 2, nodes_y[15] + 1.0, "NO", ha='center', va='center', color=COLOR_LABEL_NO, fontsize=10, fontweight='bold')

    draw_box(BRANCH_X, nodes_y[15], 24.0, BOX_H, "Restoration / Preprocessing", "Adaptive Denoise + CLAHE + Deskew", bg="#1E293B", border="#64748B")

    # Down from Restoration to Reprocessing
    draw_arrow(BRANCH_X, nodes_y[15] - 1.2, BRANCH_X, nodes_y[16] + 1.2)
    draw_box(BRANCH_X, nodes_y[16], 24.0, BOX_H, "Reprocessing", "Re-OCR & entity re-extraction", bg="#1E293B", border="#64748B")

    # Arrow from Reprocessing back to Verified Extraction
    ax.annotate(
        "", xy=(TRUNK_X + 16.0, nodes_y[16]), xytext=(BRANCH_X - 12.0, nodes_y[16]),
        arrowprops=dict(arrowstyle="-|>", color=COLOR_ARROW, lw=2.0, mutation_scale=15),
        zorder=2
    )

    # 16. Verified Extraction (Merged)
    draw_box(TRUNK_X, nodes_y[16], BOX_W, BOX_H, "Verified Extraction", "Validated fields & verified tables", bg="#064E3B", border="#059669")
    draw_arrow(TRUNK_X, nodes_y[16] - 1.2, TRUNK_X, nodes_y[17] + 1.2)

    # 17. Human-Readable Summary (4–5 lines)
    draw_box(TRUNK_X, nodes_y[17], BOX_W, BOX_H, "Human-Readable Summary", "Concise 4–5 line plain-language explanation", bg="#1E3A8A", border="#3B82F6")
    draw_arrow(TRUNK_X, nodes_y[17] - 1.2, TRUNK_X, nodes_y[18] + 2.0)

    # 18. Decision Diamond: Human Review
    draw_diamond(TRUNK_X, nodes_y[18], 26.0, 4.0, "Human Review Gate", "Inspection & Decision")

    # Branches from Human Review: Left to Accept, Right to Edit/Review
    x_accept = 24.0
    x_edit = 56.0
    y_actions = nodes_y[19]

    # Arrow to Accept (Left)
    ax.annotate(
        "", xy=(x_accept, y_actions + 1.2), xytext=(TRUNK_X - 13.0, nodes_y[18]),
        arrowprops=dict(arrowstyle="-|>", color=COLOR_ARROW, lw=2.0, mutation_scale=15, connectionstyle="angle,angleA=0,angleB=90,rad=3"),
        zorder=2
    )
    ax.text(x_accept + 1.0, nodes_y[18] + 1.0, "Auto-Accept / Approved", ha='center', va='center', color=COLOR_LABEL_YES, fontsize=9.5, fontweight='bold')
    draw_box(x_accept, y_actions, 18.0, 2.2, "Accept", "High-confidence pass", bg="#064E3B", border="#10B981")

    # Arrow to Edit / Review (Right)
    ax.annotate(
        "", xy=(x_edit, y_actions + 1.2), xytext=(TRUNK_X + 13.0, nodes_y[18]),
        arrowprops=dict(arrowstyle="-|>", color=COLOR_ARROW, lw=2.0, mutation_scale=15, connectionstyle="angle,angleA=0,angleB=90,rad=3"),
        zorder=2
    )
    ax.text(x_edit + 1.0, nodes_y[18] + 1.0, "Manual Review / Edit", ha='center', va='center', color="#FBBF24", fontsize=9.5, fontweight='bold')
    draw_box(x_edit, y_actions, 18.0, 2.2, "Edit / Review", "Operator corrections", bg="#78350F", border="#F59E0B")

    # Merging Accept and Edit into Audit Trail
    y_audit = nodes_y[20]
    ax.annotate(
        "", xy=(TRUNK_X - 5.0, y_audit + 1.2), xytext=(x_accept, y_actions - 1.1),
        arrowprops=dict(arrowstyle="-|>", color=COLOR_ARROW, lw=2.0, mutation_scale=15, connectionstyle="angle,angleA=-90,angleB=180,rad=3"),
        zorder=2
    )
    ax.annotate(
        "", xy=(TRUNK_X + 5.0, y_audit + 1.2), xytext=(x_edit, y_actions - 1.1),
        arrowprops=dict(arrowstyle="-|>", color=COLOR_ARROW, lw=2.0, mutation_scale=15, connectionstyle="angle,angleA=-90,angleB=0,rad=3"),
        zorder=2
    )

    # 20. Audit Trail
    draw_box(TRUNK_X, y_audit, BOX_W, BOX_H, "Audit Trail Logging", "Immutable SQLite transaction ledger")
    draw_arrow(TRUNK_X, y_audit - 1.2, TRUNK_X, nodes_y[21] + 1.2)

    # 21. Final Results
    draw_box(TRUNK_X, nodes_y[21], BOX_W, BOX_H, "Final Verified Results", "Interactive UI • Bounding Boxes • XAI Reports", bg="#1E3A8A", border="#60A5FA")
    draw_arrow(TRUNK_X, nodes_y[21] - 1.2, TRUNK_X, nodes_y[22] + 1.1)

    # 22. END
    draw_terminal(TRUNK_X, nodes_y[22], 16.0, 2.2, "END")

    # Legend at bottom right
    LEGEND_X = 80.0
    LEGEND_Y = 8.0
    legend_box = patches.FancyBboxPatch(
        (LEGEND_X - 16.0, LEGEND_Y - 5.5), 32.0, 11.0,
        boxstyle="round,pad=0.5,rounding_size=0.8",
        facecolor="#0F172A", edgecolor="#334155", linewidth=1.5, zorder=3
    )
    ax.add_patch(legend_box)
    ax.text(LEGEND_X, LEGEND_Y + 4.2, "FLOWCHART SYMBOL LEGEND", ha='center', va='center', color='#FFFFFF', fontsize=10, fontweight='bold', zorder=4)

    # Legend Items
    # 1. Oval
    l_oval = patches.FancyBboxPatch((LEGEND_X - 14.0, LEGEND_Y + 1.8), 5.5, 1.6, boxstyle="round,pad=0.2,rounding_size=0.8", facecolor=COLOR_START_END, edgecolor=BORDER_START_END, lw=1.5, zorder=4)
    ax.add_patch(l_oval)
    ax.text(LEGEND_X - 6.5, LEGEND_Y + 2.6, "= Terminal (Start / End)", ha='left', va='center', color='#E2E8F0', fontsize=8.5, zorder=4)

    # 2. Process
    l_proc = patches.FancyBboxPatch((LEGEND_X - 14.0, LEGEND_Y - 0.6), 5.5, 1.6, boxstyle="round,pad=0.2,rounding_size=0.3", facecolor=COLOR_PROCESS, edgecolor=BORDER_PROCESS, lw=1.5, zorder=4)
    ax.add_patch(l_proc)
    ax.text(LEGEND_X - 6.5, LEGEND_Y + 0.2, "= Automated Process", ha='left', va='center', color='#E2E8F0', fontsize=8.5, zorder=4)

    # 3. Decision
    l_poly = patches.Polygon([(LEGEND_X - 11.2, LEGEND_Y - 1.6), (LEGEND_X - 8.5, LEGEND_Y - 2.5), (LEGEND_X - 11.2, LEGEND_Y - 3.4), (LEGEND_X - 13.9, LEGEND_Y - 2.5)], closed=True, facecolor=COLOR_DECISION, edgecolor=BORDER_DECISION, lw=1.5, zorder=4)
    ax.add_patch(l_poly)
    ax.text(LEGEND_X - 6.5, LEGEND_Y - 2.5, "= Decision Gate", ha='left', va='center', color='#E2E8F0', fontsize=8.5, zorder=4)

    # 4. Arrow
    ax.annotate("", xy=(LEGEND_X - 8.5, LEGEND_Y - 4.5), xytext=(LEGEND_X - 14.0, LEGEND_Y - 4.5), arrowprops=dict(arrowstyle="-|>", color=COLOR_ARROW, lw=1.8), zorder=4)
    ax.text(LEGEND_X - 6.5, LEGEND_Y - 4.5, "= Sequential Flow", ha='left', va='center', color='#E2E8F0', fontsize=8.5, zorder=4)

    # Save to PNG and PDF
    plt.tight_layout()
    plt.savefig(str(output_png), dpi=300, facecolor=BG_COLOR, edgecolor='none', bbox_inches='tight')
    plt.savefig(str(output_pdf), facecolor=BG_COLOR, edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"Flowchart successfully saved to:\n  PNG: {output_png}\n  PDF: {output_pdf}")

if __name__ == "__main__":
    current_dir = Path(__file__).resolve().parent
    png_path = current_dir / "DOCUSURE_SYSTEM_FLOWCHART.png"
    pdf_path = current_dir / "DOCUSURE_SYSTEM_FLOWCHART.pdf"
    draw_flowchart(png_path, pdf_path)
