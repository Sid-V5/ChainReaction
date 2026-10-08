"""
ChainReaction - High-Impact Light-Mode Architecture Presentation
Built using python-pptx following strict design guidelines from the PowerPoint skill:
- Premium light theme (Gallery Off-White #F8FAFC background, Pure White #FFFFFF cards, Crisp Slate #E2E8F0 borders)
- Zero AI-slop: NO underline lines beneath titles, active statement headers, high-contrast typography
- Code blocks in elegant dark terminal containers (#0F172A) for max contrast
- Mathematically proportioned screenshot frames matching exact 1.995:1 aspect ratios
- Strict text-frame word-wrapping and boundary padding to prevent any clipping or overflow
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# --- COLOR PALETTE (Clean Light Architecture Theme) ---
BG_LIGHT = RGBColor(248, 250, 252)     # #F8FAFC Premium Off-White
CARD_BG = RGBColor(255, 255, 255)      # #FFFFFF Pure White
CARD_BORDER = RGBColor(226, 232, 240)  # #E2E8F0 Subtle Slate Border
CARD_ALT_BG = RGBColor(241, 245, 249)  # #F1F5F9 Soft Ice Slate (for table alt rows)

TEXT_TITLE = RGBColor(15, 23, 42)      # #0F172A Deep Charcoal / Near-Black
TEXT_BODY = RGBColor(51, 65, 85)       # #334155 Dark Slate
TEXT_MUTED = RGBColor(100, 116, 139)   # #64748B Secondary Slate

# Accents
ACCENT_GREEN = RGBColor(5, 150, 105)   # #059669 Emerald Green (MongoDB & Security)
ACCENT_GREEN_BG = RGBColor(236, 253, 245) # #ECFDF5 Tint
ACCENT_CYAN = RGBColor(2, 132, 199)    # #0284C7 Tech Blue/Cyan (Neo4j & Orchestration)
ACCENT_CYAN_BG = RGBColor(240, 249, 255)  # #F0F9FF Tint
ACCENT_PURPLE = RGBColor(124, 58, 237) # #7C3AED Deep Purple (Redis & In-Memory)
ACCENT_PURPLE_BG = RGBColor(245, 243, 255) # #F5F3FF Tint
ACCENT_RED = RGBColor(220, 38, 38)     # #DC2626 Crimson (Log4Shell & Critical Alerts)
ACCENT_RED_BG = RGBColor(254, 242, 242)   # #FEF2F2 Tint

# Code block colors
CODE_BG = RGBColor(15, 23, 42)         # #0F172A Dark Slate Editor
CODE_BORDER = RGBColor(51, 65, 85)     # #334155 Editor Border
CODE_LABEL = RGBColor(148, 163, 184)   # #94A3B8 Crisp Slate Label
CODE_TEXT = RGBColor(56, 189, 248)     # #38BDF8 Electric Cyan Code

FONT_TITLE = "Segoe UI"
FONT_BODY = "Segoe UI"
FONT_CODE = "Consolas"

ASSETS_DIR = os.path.abspath("d:/NoSQLProj/presentation_assets")


def add_card_textbox(slide, x, y, w, h, word_wrap=True, margin_h=0, margin_v=0):
    """Helper to ensure every textbox strictly enables word wrapping and zero unwanted margins."""
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = word_wrap
    tf.margin_left = Inches(margin_h)
    tf.margin_right = Inches(margin_h)
    tf.margin_top = Inches(margin_v)
    tf.margin_bottom = Inches(margin_v)
    return tb, tf


def create_light_slide(prs, category_text, title_text, pill_color=ACCENT_GREEN, pill_bg=ACCENT_GREEN_BG, pill_w=Inches(3.6)):
    """Creates a slide with clean off-white background and uppercase category badge + title."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Background
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = BG_LIGHT
    bg.line.fill.background()

    # Category Pill (NO lines beneath title!)
    badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.42), pill_w, Inches(0.32))
    badge.fill.solid()
    badge.fill.fore_color.rgb = pill_bg
    badge.line.color.rgb = pill_color
    badge.line.width = Pt(1)
    tf_b = badge.text_frame
    tf_b.word_wrap = False
    tf_b.margin_left = Inches(0.12)
    tf_b.margin_top = Inches(0.04)
    p_b = tf_b.paragraphs[0]
    p_b.text = category_text
    p_b.font.size = Pt(10)
    p_b.font.bold = True
    p_b.font.name = FONT_TITLE
    p_b.font.color.rgb = pill_color

    # Slide Title
    tb_t, tf_t = add_card_textbox(slide, Inches(0.8), Inches(0.82), Inches(11.7), Inches(0.65))
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.size = Pt(25)
    p_t.font.bold = True
    p_t.font.name = FONT_TITLE
    p_t.font.color.rgb = TEXT_TITLE

    return slide


def add_light_card(slide, x, y, w, h, bg_color=CARD_BG, border_color=CARD_BORDER):
    """Adds a rounded rectangle card container with crisp modern rounded corners."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1)
    card.adjustments[0] = 0.035
    return card


def add_code_card(slide, x, y, w, h, code_text, label="EXCERPT", font_size=Pt(9.5)):
    """Adds a dark terminal code editor inside the light slide with safe border margins."""
    editor = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    editor.fill.solid()
    editor.fill.fore_color.rgb = CODE_BG
    editor.line.color.rgb = CODE_BORDER
    editor.line.width = Pt(1)
    editor.adjustments[0] = 0.035

    pad_x = Inches(0.32)
    if label:
        lbl_box, tf_l = add_card_textbox(slide, x + pad_x, y + Inches(0.22), w - (pad_x * 2), Inches(0.25))
        p_l = tf_l.paragraphs[0]
        p_l.text = label
        p_l.font.size = Pt(9)
        p_l.font.bold = True
        p_l.font.name = FONT_TITLE
        p_l.font.color.rgb = CODE_LABEL

    code_y = y + (Inches(0.54) if label else Inches(0.25))
    code_h = h - (Inches(0.70) if label else Inches(0.40))
    tb_c, tf_c = add_card_textbox(slide, x + pad_x, code_y, w - (pad_x * 2), code_h)
    p = tf_c.paragraphs[0]
    p.text = code_text.strip()
    p.font.size = font_size
    p.font.name = FONT_CODE
    p.font.color.rgb = CODE_TEXT
    return editor


def add_proportional_image(slide, x, y, w, image_filename, border_color=CARD_BORDER):
    """Adds a 1.995:1 aspect ratio screenshot with clean white frame and subtle border."""
    img_path = os.path.join(ASSETS_DIR, image_filename)
    aspect = 1.9948
    h = w / aspect

    # Background card frame
    frame = add_light_card(slide, x, y, w, h, bg_color=CARD_BG, border_color=border_color)
    pad = Inches(0.04)
    if os.path.exists(img_path):
        slide.shapes.add_picture(img_path, x + pad, y + pad, width=w - (pad * 2), height=h - (pad * 2))
    return h


def build_light_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # ==========================================================================
    # SLIDE 1: Title & Executive Summary
    # ==========================================================================
    slide1 = prs.slides.add_slide(prs.slide_layouts[6])
    bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = BG_LIGHT
    bg1.line.fill.background()

    # Category Badge
    badge1 = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.85), Inches(3.6), Inches(0.35))
    badge1.fill.solid()
    badge1.fill.fore_color.rgb = ACCENT_GREEN_BG
    badge1.line.color.rgb = ACCENT_GREEN
    badge1.line.width = Pt(1)
    tf1_b = badge1.text_frame
    p1_b = tf1_b.paragraphs[0]
    p1_b.text = "SOFTWARE SUPPLY CHAIN TELEMETRY"
    p1_b.font.size = Pt(10)
    p1_b.font.bold = True
    p1_b.font.color.rgb = ACCENT_GREEN

    # Title & Subtitle
    tb1_t, tf1_t = add_card_textbox(slide1, Inches(0.8), Inches(1.35), Inches(5.8), Inches(1.8))
    p1_t = tf1_t.paragraphs[0]
    p1_t.text = "ChainReaction"
    p1_t.font.size = Pt(44)
    p1_t.font.bold = True
    p1_t.font.color.rgb = TEXT_TITLE

    p1_sub = tf1_t.add_paragraph()
    p1_sub.text = "Built around the workload"
    p1_sub.font.size = Pt(20)
    p1_sub.font.bold = True
    p1_sub.font.color.rgb = ACCENT_CYAN
    p1_sub.space_before = Pt(4)

    p1_desc = tf1_t.add_paragraph()
    p1_desc.text = "Real-Time Polyglot NoSQL Dependency & Transitive Blast Radius Engine"
    p1_desc.font.size = Pt(13)
    p1_desc.font.color.rgb = TEXT_MUTED
    p1_desc.space_before = Pt(6)

    # Left Side: Tech Architecture Stack Cards
    add_light_card(slide1, Inches(0.8), Inches(3.40), Inches(5.3), Inches(1.50), bg_color=CARD_BG)
    tb_s1, tf_s1 = add_card_textbox(slide1, Inches(1.05), Inches(3.55), Inches(4.8), Inches(1.20))
    p_s1_t = tf_s1.paragraphs[0]
    p_s1_t.text = "MongoDB  ·  Neo4j  ·  Redis"
    p_s1_t.font.size = Pt(16)
    p_s1_t.font.bold = True
    p_s1_t.font.color.rgb = ACCENT_GREEN

    p_s1_d1 = tf_s1.add_paragraph()
    p_s1_d1.text = "• MongoDB: Polymorphic manifests, schema validation & analytics"
    p_s1_d1.font.size = Pt(11)
    p_s1_d1.font.color.rgb = TEXT_BODY
    p_s1_d1.space_before = Pt(4)

    p_s1_d2 = tf_s1.add_paragraph()
    p_s1_d2.text = "• Neo4j: Multi-hop graph traversal for transitive blast paths"
    p_s1_d2.font.size = Pt(11)
    p_s1_d2.font.color.rgb = TEXT_BODY

    p_s1_d3 = tf_s1.add_paragraph()
    p_s1_d3.text = "• Redis: Sub-millisecond risk rank leaderboard & live alert ticker"
    p_s1_d3.font.size = Pt(11)
    p_s1_d3.font.color.rgb = TEXT_BODY

    add_light_card(slide1, Inches(0.8), Inches(5.05), Inches(5.3), Inches(1.35), bg_color=CARD_BG)
    tb_s2, tf_s2 = add_card_textbox(slide1, Inches(1.05), Inches(5.20), Inches(4.8), Inches(1.05))
    p_s2_t = tf_s2.paragraphs[0]
    p_s2_t.text = "FastAPI  +  React Cytoscape"
    p_s2_t.font.size = Pt(16)
    p_s2_t.font.bold = True
    p_s2_t.font.color.rgb = ACCENT_CYAN

    p_s2_d = tf_s2.add_paragraph()
    p_s2_d.text = "Asynchronous ASGI API coordinating the three stores; pushes live WebSocket zero-day telemetry directly to the interactive canvas."
    p_s2_d.font.size = Pt(11.5)
    p_s2_d.font.color.rgb = TEXT_BODY
    p_s2_d.space_before = Pt(4)

    # Right Side: Framed Screenshot (6.4" wide -> 3.21" high)
    add_proportional_image(slide1, Inches(6.35), Inches(1.8), Inches(6.2), "01_dashboard_dark.png")

    # Author Footer
    tb_foot, tf_f = add_card_textbox(slide1, Inches(0.8), Inches(6.75), Inches(11.7), Inches(0.4))
    p_f = tf_f.paragraphs[0]
    p_f.text = "Siddhant Mishra   |   AIM3141 NoSQL Database   |   Manipal University Jaipur   |   github.com/Sid-V5/ChainReaction"
    p_f.font.size = Pt(11)
    p_f.font.color.rgb = TEXT_MUTED

    # ==========================================================================
    # SLIDE 2: The Failure Mode (Log4Shell)
    # ==========================================================================
    slide2 = create_light_slide(prs, "THE FAILURE MODE", "One buried package can expose every service above it", ACCENT_RED, ACCENT_RED_BG)

    # Left: Big Stat Callout Card
    add_light_card(slide2, Inches(0.8), Inches(1.65), Inches(4.6), Inches(5.1), bg_color=CARD_BG, border_color=CARD_BORDER)
    tb_stat, tf_st = add_card_textbox(slide2, Inches(1.1), Inches(1.95), Inches(4.0), Inches(4.4))

    p_num = tf_st.paragraphs[0]
    p_num.text = "10.0"
    p_num.font.size = Pt(72)
    p_num.font.bold = True
    p_num.font.color.rgb = ACCENT_RED
    p_num.font.name = FONT_TITLE

    p_lbl = tf_st.add_paragraph()
    p_lbl.text = "LOG4SHELL · CVSS CRITICAL"
    p_lbl.font.size = Pt(12)
    p_lbl.font.bold = True
    p_lbl.font.color.rgb = ACCENT_RED
    p_lbl.space_before = Pt(4)

    p_cve = tf_st.add_paragraph()
    p_cve.text = "CVE-2021-44228"
    p_cve.font.size = Pt(18)
    p_cve.font.bold = True
    p_cve.font.color.rgb = TEXT_TITLE
    p_cve.space_before = Pt(8)

    p_sub = tf_st.add_paragraph()
    p_sub.text = "A simple logging utility became an all-hands zero-day emergency for thousands of engineering teams worldwide."
    p_sub.font.size = Pt(13)
    p_sub.font.color.rgb = TEXT_BODY
    p_sub.space_before = Pt(10)

    # Right: Narrative Cards
    add_light_card(slide2, Inches(5.8), Inches(1.65), Inches(6.7), Inches(2.4), bg_color=CARD_BG)
    tb_r1, tf_r1 = add_card_textbox(slide2, Inches(6.1), Inches(1.85), Inches(6.1), Inches(2.0))
    p_r1_h = tf_r1.paragraphs[0]
    p_r1_h.text = "The Transitive Dependency Blindspot"
    p_r1_h.font.size = Pt(18)
    p_r1_h.font.bold = True
    p_r1_h.font.color.rgb = TEXT_TITLE

    p_r1_b = tf_r1.add_paragraph()
    p_r1_b.text = "Several layers down, the vulnerable package was completely invisible to developers. Modern applications pull 500+ direct and indirect dependencies. Nested dependency trees hide who actually depends on what."
    p_r1_b.font.size = Pt(13.5)
    p_r1_b.font.color.rgb = TEXT_BODY
    p_r1_b.space_before = Pt(8)

    add_light_card(slide2, Inches(5.8), Inches(4.35), Inches(6.7), Inches(2.4), bg_color=CARD_BG)
    tb_r2, tf_r2 = add_card_textbox(slide2, Inches(6.1), Inches(4.55), Inches(6.1), Inches(2.0))
    p_r2_h = tf_r2.paragraphs[0]
    p_r2_h.text = "The Blast Radius Reality"
    p_r2_h.font.size = Pt(18)
    p_r2_h.font.bold = True
    p_r2_h.font.color.rgb = TEXT_TITLE

    p_r2_b = tf_r2.add_paragraph()
    p_r2_b.text = "Blast radius stays unseen until someone traces it by hand. Conventional flat scanners dump disconnected CSV vulnerability lists without computing graph geometry or upstream impact paths."
    p_r2_b.font.size = Pt(13.5)
    p_r2_b.font.color.rgb = TEXT_BODY
    p_r2_b.space_before = Pt(8)

    # ==========================================================================
    # SLIDE 3: Polyglot Persistence
    # ==========================================================================
    slide3 = create_light_slide(prs, "POLYGLOT PERSISTENCE", "No single database fits all three workloads", ACCENT_CYAN, ACCENT_CYAN_BG)

    # Top Table
    tbl_shape = slide3.shapes.add_table(4, 3, Inches(0.8), Inches(1.55), Inches(11.7), Inches(2.5))
    tbl = tbl_shape.table
    tbl.columns[0].width = Inches(3.6)
    tbl.columns[1].width = Inches(2.2)
    tbl.columns[2].width = Inches(5.9)

    headers = ["Workload", "Engine", "Why a single store stalls"]
    for i, h_text in enumerate(headers):
        c = tbl.cell(0, i)
        c.fill.solid()
        c.fill.fore_color.rgb = CARD_ALT_BG
        c.vertical_anchor = MSO_ANCHOR.MIDDLE
        c.text_frame.word_wrap = True
        p = c.text_frame.paragraphs[0]
        p.text = h_text
        p.font.bold = True
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_TITLE

    rows = [
        ("Manifests, CVE advisories, aggregations", "MongoDB", "Flexible records fit documents naturally; repeated path expansion does not."),
        ("Multi-hop dependency traversal", "Neo4j", "Relationships are native; document joins add exponential traversal overhead."),
        ("Risk ranking, query cache, alert broadcast", "Redis", "Hot reads and broadcasts need a dedicated in-memory sub-millisecond path.")
    ]
    for row_idx, (w, e, why) in enumerate(rows, start=1):
        for col_idx, text in enumerate([w, e, why]):
            c = tbl.cell(row_idx, col_idx)
            c.fill.solid()
            c.fill.fore_color.rgb = CARD_BG if row_idx % 2 == 1 else CARD_ALT_BG
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            c.text_frame.word_wrap = True
            p = c.text_frame.paragraphs[0]
            p.text = text
            p.font.size = Pt(12)
            if col_idx == 1:
                p.font.bold = True
                p.font.color.rgb = ACCENT_GREEN if e == "MongoDB" else (ACCENT_CYAN if e == "Neo4j" else ACCENT_PURPLE)
            elif col_idx == 0:
                p.font.bold = True
                p.font.color.rgb = TEXT_TITLE
            else:
                p.font.color.rgb = TEXT_BODY

    # Bottom Split
    add_light_card(slide3, Inches(0.8), Inches(4.35), Inches(5.6), Inches(2.75), bg_color=CARD_BG)
    tb_b1, tf_b1 = add_card_textbox(slide3, Inches(1.05), Inches(4.55), Inches(5.1), Inches(2.35))
    p_b1_h = tf_b1.paragraphs[0]
    p_b1_h.text = "FastAPI Orchestrates the Triad"
    p_b1_h.font.size = Pt(18)
    p_b1_h.font.bold = True
    p_b1_h.font.color.rgb = ACCENT_CYAN

    p_b1_d = tf_b1.add_paragraph()
    p_b1_d.text = "One unified asynchronous API coordinates MongoDB document writes, synchronizes Neo4j graph relationships, and broadcasts Redis WebSocket events to the React Cytoscape frontend."
    p_b1_d.font.size = Pt(12.5)
    p_b1_d.font.color.rgb = TEXT_BODY
    p_b1_d.space_before = Pt(8)

    add_proportional_image(slide3, Inches(6.8), Inches(4.35), Inches(5.7), "01_dashboard_dark.png")

    # ==========================================================================
    # SLIDE 4: MongoDB Document Model
    # ==========================================================================
    slide4 = create_light_slide(prs, "MONGODB · DOCUMENT MODEL", "Polymorphic manifests fit BSON documents naturally", ACCENT_GREEN, ACCENT_GREEN_BG)

    code_s4 = """// MongoDB BSON Collection: repositories
{
  repo: "apache/logging-log4j2",
  primary_language: "Java",
  dependencies: [
    { name: "log4j-core", version: "2.14.1", is_direct: true }
  ],
  cves: [
    {
      id: "CVE-2021-44228",
      severity: "CRITICAL",
      cvss: 10.0,
      affected_packages: ["log4j-core"]
    }
  ],
  last_scanned: ISODate("2026-10-06T10:15:00Z")
}"""
    add_code_card(slide4, Inches(0.8), Inches(1.65), Inches(5.7), Inches(5.2), code_s4, "ILLUSTRATIVE REPOSITORY DOCUMENT")

    add_light_card(slide4, Inches(6.8), Inches(1.65), Inches(5.7), Inches(2.45), bg_color=CARD_BG)
    tb_m1, tf_m1 = add_card_textbox(slide4, Inches(7.05), Inches(1.85), Inches(5.2), Inches(2.05))
    p_m1_h = tf_m1.paragraphs[0]
    p_m1_h.text = "One Collection, Multiple Ecosystem Shapes"
    p_m1_h.font.size = Pt(17)
    p_m1_h.font.bold = True
    p_m1_h.font.color.rgb = TEXT_TITLE

    p_m1_d = tf_m1.add_paragraph()
    p_m1_d.text = "package.json, requirements.txt, and pom.xml have fundamentally different manifest structures. BSON stores all ecosystems in one collection without migrations or rigid column conversions."
    p_m1_d.font.size = Pt(12.5)
    p_m1_d.font.color.rgb = TEXT_BODY
    p_m1_d.space_before = Pt(8)

    add_light_card(slide4, Inches(6.8), Inches(4.40), Inches(5.7), Inches(2.45), bg_color=CARD_BG)
    tb_m2, tf_m2 = add_card_textbox(slide4, Inches(7.05), Inches(4.60), Inches(5.2), Inches(2.05))
    p_m2_h = tf_m2.paragraphs[0]
    p_m2_h.text = "Dependencies & Advisories Stay Nested"
    p_m2_h.font.size = Pt(17)
    p_m2_h.font.bold = True
    p_m2_h.font.color.rgb = TEXT_TITLE

    p_m2_d = tf_m2.add_paragraph()
    p_m2_d.text = "The repository document carries an embedded dependencies array alongside active CVEs with severity, CVSS scores, and affected packages in a single atomic record."
    p_m2_d.font.size = Pt(12.5)
    p_m2_d.font.color.rgb = TEXT_BODY
    p_m2_d.space_before = Pt(8)

    # ==========================================================================
    # SLIDE 5: MongoDB Write Contract ($jsonSchema)
    # ==========================================================================
    slide5 = create_light_slide(prs, "MONGODB · WRITE CONTRACT", "The database enforces structure, not the ORM", ACCENT_GREEN, ACCENT_GREEN_BG)

    code_s5 = """db.createCollection("repositories", {
  validator: { $jsonSchema: {
    bsonType: "object",
    required: ["repo", "primary_language"],
    properties: {
      repo: { bsonType: "string" },
      primary_language: { enum: ["Java", "JavaScript", "Python"] },
      cves: {
        bsonType: "array",
        items: {
          bsonType: "object",
          properties: {
            cvss: { bsonType: "number", minimum: 0, maximum: 10 }
          }
        }
      }
    }
  }}
})"""
    add_code_card(slide5, Inches(0.8), Inches(1.65), Inches(5.7), Inches(5.2), code_s5, "COLLECTION-LEVEL VALIDATOR · EXCERPT")

    # Right: Description and 2 validation cards
    tb_c_head, tf_ch = add_card_textbox(slide5, Inches(6.8), Inches(1.65), Inches(5.7), Inches(0.95))
    p_ch_t = tf_ch.paragraphs[0]
    p_ch_t.text = "Every client meets the same contract."
    p_ch_t.font.size = Pt(18)
    p_ch_t.font.bold = True
    p_ch_t.font.color.rgb = ACCENT_GREEN

    p_ch_s = tf_ch.add_paragraph()
    p_ch_s.text = "Required fields, BSON type checks, a language enum, and CVSS bounds are enforced inside the database engine."
    p_ch_s.font.size = Pt(12.5)
    p_ch_s.font.color.rgb = TEXT_BODY
    p_ch_s.space_before = Pt(4)

    # Card 1: Valid Write
    add_light_card(slide5, Inches(6.8), Inches(2.80), Inches(5.7), Inches(1.85), bg_color=CARD_BG, border_color=ACCENT_GREEN)
    tb_v, tf_v = add_card_textbox(slide5, Inches(7.05), Inches(2.95), Inches(5.2), Inches(1.50))
    p_v_h = tf_v.paragraphs[0]
    p_v_h.text = "✓  Valid Write"
    p_v_h.font.size = Pt(16)
    p_v_h.font.bold = True
    p_v_h.font.color.rgb = ACCENT_GREEN

    p_v_b = tf_v.add_paragraph()
    p_v_b.text = "Accepted directly by the collection validator without application-level overhead."
    p_v_b.font.size = Pt(12.5)
    p_v_b.font.color.rgb = TEXT_BODY
    p_v_b.space_before = Pt(4)

    # Card 2: Invalid Write
    add_light_card(slide5, Inches(6.8), Inches(4.95), Inches(5.7), Inches(1.85), bg_color=CARD_BG, border_color=ACCENT_RED)
    tb_iv, tf_iv = add_card_textbox(slide5, Inches(7.05), Inches(5.10), Inches(5.2), Inches(1.50))
    p_iv_h = tf_iv.paragraphs[0]
    p_iv_h.text = "✕  Invalid Write"
    p_iv_h.font.size = Pt(16)
    p_iv_h.font.bold = True
    p_iv_h.font.color.rgb = ACCENT_RED

    p_iv_b = tf_iv.add_paragraph()
    p_iv_b.text = "Rejected immediately at the engine, preventing corrupt records from external scripts or services."
    p_iv_b.font.size = Pt(12.5)
    p_iv_b.font.color.rgb = TEXT_BODY
    p_iv_b.space_before = Pt(4)

    # ==========================================================================
    # SLIDE 6: MongoDB Computed + Extended Reference
    # ==========================================================================
    slide6 = create_light_slide(prs, "MONGODB · COMPUTED + EXTENDED REFERENCE", "Pre-compute risk on write, so reads stay cheap", ACCENT_GREEN, ACCENT_GREEN_BG)

    # Left Column Lead
    tb_s6_lead, tf_s6l = add_card_textbox(slide6, Inches(0.8), Inches(1.55), Inches(5.8), Inches(0.80))
    p_s6_lead = tf_s6l.paragraphs[0]
    p_s6_lead.text = "Store risk_score on each repository; render CLEAN / ELEV / CRIT badges without recomputing risk on reads."
    p_s6_lead.font.size = Pt(13.5)
    p_s6_lead.font.bold = True
    p_s6_lead.font.color.rgb = TEXT_TITLE

    # Prototype Table
    tbl_s6 = slide6.shapes.add_table(5, 3, Inches(0.8), Inches(2.45), Inches(5.8), Inches(2.30)).table
    tbl_s6.columns[0].width = Inches(3.2)
    tbl_s6.columns[1].width = Inches(1.3)
    tbl_s6.columns[2].width = Inches(1.3)

    t6_headers = ["Prototype repo", "Score", "Badge"]
    for i, h in enumerate(t6_headers):
        c = tbl_s6.cell(0, i)
        c.fill.solid()
        c.fill.fore_color.rgb = CARD_ALT_BG
        c.vertical_anchor = MSO_ANCHOR.MIDDLE
        c.text_frame.word_wrap = True
        p = c.text_frame.paragraphs[0]
        p.text = h
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_TITLE

    t6_data = [
        ("apache/logging-log4j2", "80.0", "CRIT"),
        ("spring-projects/spring-boot", "78.5", "CRIT"),
        ("pallets/flask", "61.2", "CRIT"),
        ("psf/requests", "44.8", "ELEV"),
    ]
    for r_idx, (r, s, b) in enumerate(t6_data, start=1):
        for c_idx, val in enumerate([r, s, b]):
            c = tbl_s6.cell(r_idx, c_idx)
            c.fill.solid()
            c.fill.fore_color.rgb = CARD_BG if r_idx % 2 == 1 else CARD_ALT_BG
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            c.text_frame.word_wrap = True
            p = c.text_frame.paragraphs[0]
            p.text = val
            p.font.size = Pt(11.5)
            if c_idx == 2:
                p.font.bold = True
                p.font.color.rgb = ACCENT_RED if b == "CRIT" else ACCENT_GREEN
            elif c_idx == 0:
                p.font.color.rgb = TEXT_TITLE
            else:
                p.font.color.rgb = TEXT_BODY

    # Extended Reference Card below table
    add_light_card(slide6, Inches(0.8), Inches(4.95), Inches(5.8), Inches(1.90), bg_color=CARD_BG)
    tb_er, tf_er = add_card_textbox(slide6, Inches(1.05), Inches(5.10), Inches(5.3), Inches(1.60))
    p_er_h = tf_er.paragraphs[0]
    p_er_h.text = "Copy the hot fields, retain the link"
    p_er_h.font.size = Pt(15)
    p_er_h.font.bold = True
    p_er_h.font.color.rgb = ACCENT_CYAN

    p_er_b = tf_er.add_paragraph()
    p_er_b.text = "Embed frequently queried CVE id, severity, and score directly in the repository manifest for instant table rendering; link to full advisories in canonical collections."
    p_er_b.font.size = Pt(12)
    p_er_b.font.color.rgb = TEXT_BODY
    p_er_b.space_before = Pt(4)

    # Right: Framed Screenshot + Zero-Join Card
    add_proportional_image(slide6, Inches(6.8), Inches(1.8), Inches(5.7), "05_repository_telemetry_table.png")

    add_light_card(slide6, Inches(6.8), Inches(4.95), Inches(5.7), Inches(1.90), bg_color=CARD_BG, border_color=ACCENT_GREEN)
    tb_zj, tf_zj = add_card_textbox(slide6, Inches(7.05), Inches(5.10), Inches(5.2), Inches(1.60))
    p_zj_h = tf_zj.paragraphs[0]
    p_zj_h.text = "Zero-Join Manifest Retrieval"
    p_zj_h.font.size = Pt(16)
    p_zj_h.font.bold = True
    p_zj_h.font.color.rgb = ACCENT_GREEN

    p_zj_b = tf_zj.add_paragraph()
    p_zj_b.text = "The monitored repository view renders stars, languages, and severity badges from a single collection fetch—eliminating costly multi-table SQL joins."
    p_zj_b.font.size = Pt(12)
    p_zj_b.font.color.rgb = TEXT_BODY
    p_zj_b.space_before = Pt(4)

    # ==========================================================================
    # SLIDE 7: MongoDB Access Path & Indexing
    # ==========================================================================
    slide7 = create_light_slide(prs, "MONGODB · ACCESS PATH", "Compound indexes match the way analysts filter", ACCENT_GREEN, ACCENT_GREEN_BG)

    # 3 Step Cards Across Top
    steps = [
        ("01", "Equality", "Filter on primary_language."),
        ("02", "Ordered scan", "Read stars descending."),
        ("03", "No blocking sort", "The compound index supplies the order.")
    ]
    sw = Inches(3.64)
    sgap = Inches(0.39)
    for i, (num, h_text, d_text) in enumerate(steps):
        sx = Inches(0.8) + (i * (sw + sgap))
        add_light_card(slide7, sx, Inches(1.65), sw, Inches(1.3), bg_color=CARD_BG)
        tb_st, tf_st = add_card_textbox(slide7, sx + Inches(0.2), Inches(1.75), sw - Inches(0.4), Inches(1.1))
        p_n = tf_st.paragraphs[0]
        p_n.text = f"{num}  ·  {h_text}"
        p_n.font.size = Pt(14)
        p_n.font.bold = True
        p_n.font.color.rgb = ACCENT_GREEN

        p_d = tf_st.add_paragraph()
        p_d.text = d_text
        p_d.font.size = Pt(12)
        p_d.font.color.rgb = TEXT_BODY
        p_d.space_before = Pt(4)

    # Bottom Left: Code Editor with explain
    code_s7 = """db.repositories.createIndex({
  primary_language: 1, stars: -1
})
db.repositories.createIndex({ repo: "text" })

db.repositories.find({
  primary_language: "Java"
}).sort({ stars: -1 }).explain("executionStats")

// Winning-plan stage: IXSCAN
// No blocking SORT for this query"""
    add_code_card(slide7, Inches(0.8), Inches(3.20), Inches(5.7), Inches(3.70), code_s7, "INDEX DEFINITION & EXPLAIN PLAN")

    # Bottom Right: Screenshot
    add_proportional_image(slide7, Inches(6.8), Inches(3.30), Inches(5.7), "05_repository_telemetry_table.png")

    # ==========================================================================
    # SLIDE 8: MongoDB Live Analytics & Aggregation
    # ==========================================================================
    slide8 = create_light_slide(prs, "MONGODB · LIVE ANALYTICS", "Aggregation pipelines turn telemetry into live analytics", ACCENT_GREEN, ACCENT_GREEN_BG)

    # Subtitle lead
    tb_s8_sub, tf_s8s = add_card_textbox(slide8, Inches(0.8), Inches(1.50), Inches(11.7), Inches(0.55))
    p_s8s = tf_s8s.paragraphs[0]
    p_s8s.text = "$match → $group → $project derives per-language risk index, CVE counts and peak CVSS. $facet runs parallel pipelines over one shared input scan."
    p_s8s.font.size = Pt(13)
    p_s8s.font.color.rgb = TEXT_BODY

    # Left: Code Card
    code_s8 = """db.repositories.aggregate([
  { $match: { risk_score: { $exists: true } } },
  { $facet: {
      byLanguage: [
        { $group: {
            _id: "$primary_language",
            risk_index: { $avg: "$risk_score" }
        }},
        { $project: { _id: 0, language: "$_id", risk_index: 1 } }
      ],
      peak: [
        { $unwind: "$cves" },
        { $group: { _id: null, peak_cvss: { $max: "$cves.cvss" } } }
      ]
  }}
])"""
    add_code_card(slide8, Inches(0.8), Inches(2.15), Inches(5.8), Inches(4.75), code_s8, "$FACET PIPELINE · EXCERPT")

    # Right: Screenshot & Metric Cards
    add_proportional_image(slide8, Inches(6.8), Inches(2.15), Inches(5.7), "04_mongodb_analytics_panel.png")

    add_light_card(slide8, Inches(6.8), Inches(5.20), Inches(5.7), Inches(1.70), bg_color=CARD_BG, border_color=ACCENT_GREEN)
    tb_m8, tf_m8 = add_card_textbox(slide8, Inches(7.05), Inches(5.35), Inches(5.2), Inches(1.40))
    p_m8_1 = tf_m8.paragraphs[0]
    p_m8_1.text = "12 repos  ·  7 active CVEs"
    p_m8_1.font.size = Pt(16)
    p_m8_1.font.bold = True
    p_m8_1.font.color.rgb = ACCENT_GREEN

    p_m8_2 = tf_m8.add_paragraph()
    p_m8_2.text = "Java risk index: 52.83   |   Peak CVSS: 10.0 (Log4Shell)"
    p_m8_2.font.size = Pt(13)
    p_m8_2.font.bold = True
    p_m8_2.font.color.rgb = TEXT_TITLE
    p_m8_2.space_before = Pt(4)

    p_m8_3 = tf_m8.add_paragraph()
    p_m8_3.text = "All computed dynamically via single-pass aggregation pipeline."
    p_m8_3.font.size = Pt(11.5)
    p_m8_3.font.color.rgb = TEXT_MUTED
    p_m8_3.space_before = Pt(2)

    # ==========================================================================
    # SLIDE 9: Neo4j Dependency Traversal
    # ==========================================================================
    slide9 = create_light_slide(prs, "NEO4J · DEPENDENCY TRAVERSAL", "Neo4j traces 1..5 hop blast radius where joins stall", ACCENT_CYAN, ACCENT_CYAN_BG)

    # Left: Content
    add_light_card(slide9, Inches(0.8), Inches(1.65), Inches(5.7), Inches(2.05), bg_color=CARD_BG)
    tb_n1, tf_n1 = add_card_textbox(slide9, Inches(1.05), Inches(1.85), Inches(5.2), Inches(1.65))
    p_n1_h = tf_n1.paragraphs[0]
    p_n1_h.text = "Index-Free Adjacency"
    p_n1_h.font.size = Pt(18)
    p_n1_h.font.bold = True
    p_n1_h.font.color.rgb = ACCENT_CYAN

    p_n1_b = tf_n1.add_paragraph()
    p_n1_b.text = "Each hop follows relationship pointers directly in memory, not relational join tables. Sub-5ms traversal across deep microservice dependency graphs."
    p_n1_b.font.size = Pt(13)
    p_n1_b.font.color.rgb = TEXT_BODY
    p_n1_b.space_before = Pt(6)

    # Cypher Code Card
    code_s9 = """MATCH (p:Package)<-[:DEPENDS_ON*1..5]-(r:Repository)
WHERE p.name = "log4j-core"
RETURN DISTINCT r.slug, length(path) AS depth"""
    add_code_card(slide9, Inches(0.8), Inches(3.90), Inches(5.7), Inches(2.95), code_s9, "CYPHER BLAST RADIUS QUERY")

    # Right: Screenshot & Stat Card
    add_proportional_image(slide9, Inches(6.8), Inches(1.65), Inches(5.7), "02_blast_radius_trace.png")

    add_light_card(slide9, Inches(6.8), Inches(4.75), Inches(5.7), Inches(2.10), bg_color=CARD_BG)
    tb_n2, tf_n2 = add_card_textbox(slide9, Inches(7.05), Inches(4.90), Inches(5.2), Inches(1.80))
    p_n2_st = tf_n2.paragraphs[0]
    p_n2_st.text = "3 Services Exposed"
    p_n2_st.font.size = Pt(20)
    p_n2_st.font.bold = True
    p_n2_st.font.color.rgb = ACCENT_RED

    p_n2_b = tf_n2.add_paragraph()
    p_n2_b.text = "The log4j-core trace reached hop depths 1 and 2 in sub-5ms; repeat reads served as a Redis cache hit under 1ms."
    p_n2_b.font.size = Pt(13)
    p_n2_b.font.color.rgb = TEXT_BODY
    p_n2_b.space_before = Pt(4)

    # ==========================================================================
    # SLIDE 10: Redis Low-Latency Delivery
    # ==========================================================================
    slide10 = create_light_slide(prs, "REDIS · LOW-LATENCY DELIVERY", "Redis makes risk ranking and alerts instant", ACCENT_PURPLE, ACCENT_PURPLE_BG)

    # 3 Structured Vertical Cards
    rw = Inches(3.64)
    rgap = Inches(0.39)
    redis_cards = [
        ("ZSET", "Risk Leaderboard", "Repository risk scores are sorted on write for ranked reads in O(log N).",
         'ZADD risk:repos 80.0 "apache/logging-log4j2"\nZREVRANGE risk:repos 0 4 WITHSCORES', ACCENT_PURPLE),
        ("TTL CACHE", "Repeated Traces", "TTL-cached blast-radius queries return in under 1ms; expiry bounds cache lifetime.",
         'SETEX trace:log4j-core 180 "{\\"exposed\\": 3}"\nGET trace:log4j-core', ACCENT_CYAN),
        ("PUB/SUB", "Live CVE Ticker", "New CVE zero-day alerts broadcast to WebSocket subscribers without database polling.",
         'PUBLISH cve:alerts "{\\"cve\\": \\"CVE-2021-44228\\"}"\nSUBSCRIBE cve:alerts', ACCENT_RED)
    ]

    for i, (badge_txt, h_txt, desc_txt, cmd_txt, col) in enumerate(redis_cards):
        rx = Inches(0.8) + (i * (rw + rgap))
        add_light_card(slide10, rx, Inches(1.65), rw, Inches(5.20), bg_color=CARD_BG)

        tb_rc, tf_rc = add_card_textbox(slide10, rx + Inches(0.25), Inches(1.85), rw - Inches(0.5), Inches(2.20))
        p_b = tf_rc.paragraphs[0]
        p_b.text = badge_txt
        p_b.font.size = Pt(11.5)
        p_b.font.bold = True
        p_b.font.color.rgb = col

        p_h = tf_rc.add_paragraph()
        p_h.text = h_txt
        p_h.font.size = Pt(18)
        p_h.font.bold = True
        p_h.font.color.rgb = TEXT_TITLE
        p_h.space_before = Pt(4)

        p_d = tf_rc.add_paragraph()
        p_d.text = desc_txt
        p_d.font.size = Pt(12.5)
        p_d.font.color.rgb = TEXT_BODY
        p_d.space_before = Pt(8)

        # Code Block inside card
        add_code_card(slide10, rx + Inches(0.20), Inches(4.30), rw - Inches(0.40), Inches(2.35), cmd_txt, label="REDIS COMMAND", font_size=Pt(9))

    # ==========================================================================
    # SLIDE 11: Simple Conclusion & Engineering Takeaway
    # ==========================================================================
    slide11 = create_light_slide(prs, "CONCLUSION", "Three engines, zero architectural compromises", ACCENT_GREEN, ACCENT_GREEN_BG, pill_w=Inches(1.8))

    # Lead text
    tb_s11_lead, tf_s11l = add_card_textbox(slide11, Inches(0.8), Inches(1.48), Inches(11.7), Inches(0.40))
    p_s11_l = tf_s11l.paragraphs[0]
    p_s11_l.text = "What we built, what worked, and why a single database was never an option."
    p_s11_l.font.size = Pt(13)
    p_s11_l.font.color.rgb = TEXT_MUTED

    # 3 Simple Outcome Columns
    col_w = Inches(3.64)
    col_gap = Inches(0.39)

    synthesis_cols = [
        {
            "tag": "MONGODB · DOCUMENTS",
            "title": "Fits messy manifests",
            "color": ACCENT_GREEN,
            "bullets": [
                "Stored package.json, pom.xml, and requirements.txt in one BSON collection without schema migrations.",
                "Pre-computed risk scores on ingest so the repository view loads instantly without joins.",
                "Enforced CVSS bounds (0–10) and required fields in the database using $jsonSchema validation."
            ]
        },
        {
            "tag": "NEO4J · GRAPHS",
            "title": "Traces deep blast radius",
            "color": ACCENT_CYAN,
            "bullets": [
                "Traced 1 to 5 hops of dependencies in under 5ms using native Cypher graph traversal.",
                "Used index-free adjacency to avoid the slow, painful joins of relational databases.",
                "Instantly highlighted every upstream service exposed when a buried library breaks."
            ]
        },
        {
            "tag": "REDIS · IN-MEMORY",
            "title": "Keeps the UI real-time",
            "color": ACCENT_PURPLE,
            "bullets": [
                "Sorted Sets (ZSET) gave us an instant, live risk leaderboard in O(log N) time.",
                "Cached repeat graph lookups with TTL for sub-1ms response times.",
                "Pub/Sub streamed live zero-day alerts straight to the browser without polling."
            ]
        }
    ]

    for i, col in enumerate(synthesis_cols):
        cx = Inches(0.8) + (i * (col_w + col_gap))
        add_light_card(slide11, cx, Inches(1.92), col_w, Inches(3.85), bg_color=CARD_BG)

        tb_col, tf_col = add_card_textbox(slide11, cx + Inches(0.24), Inches(2.10), col_w - Inches(0.48), Inches(3.50))

        # Tag
        p_co = tf_col.paragraphs[0]
        p_co.text = col["tag"]
        p_co.font.size = Pt(10)
        p_co.font.bold = True
        p_co.font.color.rgb = col["color"]

        # Title
        p_ct = tf_col.add_paragraph()
        p_ct.text = col["title"]
        p_ct.font.size = Pt(17)
        p_ct.font.bold = True
        p_ct.font.color.rgb = TEXT_TITLE
        p_ct.space_before = Pt(4)

        # Bullets
        for b_text in col["bullets"]:
            p_pt = tf_col.add_paragraph()
            p_pt.text = f"•  {b_text}"
            p_pt.font.size = Pt(11)
            p_pt.font.color.rgb = TEXT_BODY
            p_pt.space_before = Pt(10)

    # Bottom Synthesis Banner
    add_light_card(slide11, Inches(0.8), Inches(5.95), Inches(11.7), Inches(1.15), bg_color=CARD_BG, border_color=ACCENT_GREEN)
    tb_bot, tf_bot = add_card_textbox(slide11, Inches(1.05), Inches(6.08), Inches(11.2), Inches(0.90))

    p_b1 = tf_bot.paragraphs[0]
    p_b1.text = "THE TAKEAWAY"
    p_b1.font.size = Pt(10.5)
    p_b1.font.bold = True
    p_b1.font.color.rgb = ACCENT_GREEN

    p_b2 = tf_bot.add_paragraph()
    p_b2.text = "Don't force one database to do every job. MongoDB handled the polymorphic documents, Neo4j traced the 5-hop relationships in under 5ms, and Redis kept the UI real-time. Pairing them made the system fast, simple, and resilient."
    p_b2.font.size = Pt(12)
    p_b2.font.color.rgb = TEXT_TITLE
    p_b2.space_before = Pt(3)

    # Save
    out_file = os.path.abspath("d:/NoSQLProj/ChainReaction-Engineering-a-Polyglot-NoSQL-Dependency-and-Blast-Radius-Engine.pptx")
    prs.save(out_file)
    print(f"Successfully generated light presentation: {out_file}")
    return out_file


if __name__ == "__main__":
    build_light_deck()
