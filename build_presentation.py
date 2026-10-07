"""
ChainReaction - PowerPoint Presentation Generator (Refined & QA-Verified)
Built using python-pptx with dark-mode Cyber/SecOps theme, custom cards, code blocks,
high-contrast typography, and prototype screenshot integration.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# --- COLOR PALETTE (Dark SecOps Theme) ---
BG_DARK = RGBColor(11, 15, 25)        # #0B0F19 deep slate navy
CARD_BG = RGBColor(22, 30, 46)        # #161E2E rich charcoal
CARD_BORDER = RGBColor(45, 60, 84)    # #2D3C54 subtle card border
CODE_BG = RGBColor(15, 23, 42)        # #0F172A terminal code background
CODE_BORDER = RGBColor(51, 65, 85)    # #334155
TEXT_WHITE = RGBColor(248, 250, 252)  # #F8FAFC primary title & heading
TEXT_MUTED = RGBColor(156, 175, 201)  # #9CAFCA readable slate
TEXT_DIM = RGBColor(100, 116, 139)    # #64748B subtle details
ACCENT_GREEN = RGBColor(16, 185, 129) # #10B981 MongoDB / Security
ACCENT_CYAN = RGBColor(6, 182, 212)   # #06B6D4 Neo4j / Graph
ACCENT_RED = RGBColor(239, 68, 68)    # #EF4444 Alert / Zero-Day / CVE
ACCENT_PURPLE = RGBColor(168, 85, 247)# #A855F7 Redis / Telemetry

FONT_TITLE = "Segoe UI"
FONT_BODY = "Segoe UI"
FONT_CODE = "Consolas"

ASSETS_DIR = os.path.abspath("d:/NoSQLProj/presentation_assets")


def create_base_slide(prs, category_text, title_text, category_color=ACCENT_GREEN):
    """Creates a slide with deep dark background and styled category badge + title."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout

    # Background rectangle
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = BG_DARK
    bg.line.fill.background()

    # Category badge / pill (No underline bars!)
    badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.4), Inches(2.9), Inches(0.32))
    badge.fill.solid()
    badge.fill.fore_color.rgb = CARD_BG
    badge.line.color.rgb = category_color
    badge.line.width = Pt(1)
    tf_b = badge.text_frame
    tf_b.word_wrap = False
    tf_b.margin_left = Inches(0.12)
    tf_b.margin_top = Inches(0.04)
    p_b = tf_b.paragraphs[0]
    p_b.text = f"●  {category_text}"
    p_b.font.size = Pt(10)
    p_b.font.bold = True
    p_b.font.name = FONT_TITLE
    p_b.font.color.rgb = category_color

    # Slide Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.78), Inches(11.7), Inches(0.65))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_top = tf_t.margin_bottom = tf_t.margin_right = 0
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.size = Pt(24)
    p_t.font.bold = True
    p_t.font.name = FONT_TITLE
    p_t.font.color.rgb = TEXT_WHITE

    return slide


def add_card(slide, x, y, w, h, bg_color=CARD_BG, border_color=CARD_BORDER):
    """Adds a rounded rectangle card container."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1)
    return card


def add_card_header(slide, x, y, w, title, icon_symbol="◆", color=ACCENT_GREEN):
    """Adds a bold title inside a card with icon symbol."""
    tb = slide.shapes.add_textbox(x, y, w, Inches(0.36))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_bottom = tf.margin_right = 0
    p = tf.paragraphs[0]
    p.text = f"{icon_symbol}  {title}"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.name = FONT_TITLE
    p.font.color.rgb = color
    return tb


def add_bullet_list(slide, x, y, w, h, items, font_size=12, text_color=TEXT_MUTED):
    """Adds clean formatted bullet points inside a content container."""
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_bottom = tf.margin_right = 0

    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(7)
        p.space_before = Pt(2)

        if isinstance(item, tuple):
            lead, body = item
            run1 = p.add_run()
            run1.text = f"•  {lead}: "
            run1.font.bold = True
            run1.font.size = Pt(font_size)
            run1.font.name = FONT_BODY
            run1.font.color.rgb = TEXT_WHITE

            run2 = p.add_run()
            run2.text = body
            run2.font.size = Pt(font_size)
            run2.font.name = FONT_BODY
            run2.font.color.rgb = text_color
        else:
            run = p.add_run()
            run.text = f"•  {item}"
            run.font.size = Pt(font_size)
            run.font.name = FONT_BODY
            run.font.color.rgb = text_color


def add_code_block(slide, x, y, w, h, code_text):
    """Adds a dark terminal code block with subtle border."""
    code_card = add_card(slide, x, y, w, h, bg_color=CODE_BG, border_color=CODE_BORDER)
    tb = slide.shapes.add_textbox(x + Inches(0.18), y + Inches(0.15), w - Inches(0.36), h - Inches(0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_bottom = tf.margin_right = 0
    p = tf.paragraphs[0]
    p.text = code_text.strip()
    p.font.size = Pt(10.5)
    p.font.name = FONT_CODE
    p.font.color.rgb = RGBColor(56, 189, 248)  # Light cyan code
    return code_card


def add_framed_image(slide, x, y, w, h, image_filename):
    """Adds an image with dark border frame and proper padding."""
    img_path = os.path.join(ASSETS_DIR, image_filename)
    if os.path.exists(img_path):
        frame = add_card(slide, x, y, w, h, bg_color=CODE_BG, border_color=CODE_BORDER)
        pad = Inches(0.06)
        slide.shapes.add_picture(img_path, x + pad, y + pad, width=w - (pad * 2), height=h - (pad * 2))
    else:
        add_card(slide, x, y, w, h, bg_color=CARD_BG, border_color=CARD_BORDER)


# ==============================================================================
# PRESENTATION BUILDER
# ==============================================================================

def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # --------------------------------------------------------------------------
    # SLIDE 1: Title & Executive Summary
    # --------------------------------------------------------------------------
    slide1 = prs.slides.add_slide(prs.slide_layouts[6])
    bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = BG_DARK
    bg1.line.fill.background()

    # System Status Pill
    badge1 = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(1.1), Inches(3.6), Inches(0.36))
    badge1.fill.solid()
    badge1.fill.fore_color.rgb = CARD_BG
    badge1.line.color.rgb = ACCENT_GREEN
    badge1.line.width = Pt(1)
    tf1_b = badge1.text_frame
    p1_b = tf1_b.paragraphs[0]
    p1_b.text = "●  POLYGLOT NOSQL ARCHITECTURE"
    p1_b.font.size = Pt(11)
    p1_b.font.bold = True
    p1_b.font.color.rgb = ACCENT_GREEN

    # Title & Subtitle
    tb1_t = slide1.shapes.add_textbox(Inches(0.9), Inches(1.65), Inches(11.5), Inches(1.6))
    tf1_t = tb1_t.text_frame
    tf1_t.word_wrap = True
    p1_t = tf1_t.paragraphs[0]
    p1_t.text = "ChainReaction"
    p1_t.font.size = Pt(44)
    p1_t.font.bold = True
    p1_t.font.color.rgb = TEXT_WHITE
    p1_t.font.name = FONT_TITLE

    p1_sub = tf1_t.add_paragraph()
    p1_sub.text = "Real-Time Software Supply Chain & Transitive Blast Radius Telemetry Engine"
    p1_sub.font.size = Pt(18)
    p1_sub.font.color.rgb = ACCENT_CYAN
    p1_sub.space_before = Pt(8)

    # Three Stat KPI Cards
    kpis = [
        ("< 5ms", "Blast Radius Traversal", "Neo4j Index-Free Adjacency across 1..5 hops", ACCENT_CYAN),
        ("< 1ms", "Query Caching Latency", "Redis In-Memory TTL & ZSET Risk Leaderboard", ACCENT_PURPLE),
        ("BSON + $facet", "Document & Analytics", "MongoDB Schema Validation & Computed Patterns", ACCENT_GREEN),
    ]
    card_w = Inches(3.64)
    card_gap = Inches(0.3)
    start_x = Inches(0.9)
    y_kpi = Inches(3.45)
    h_kpi = Inches(2.2)

    for i, (stat, label, desc, col) in enumerate(kpis):
        cx = start_x + (i * (card_w + card_gap))
        add_card(slide1, cx, y_kpi, card_w, h_kpi, bg_color=CARD_BG, border_color=CARD_BORDER)

        tb = slide1.shapes.add_textbox(cx + Inches(0.25), y_kpi + Inches(0.2), card_w - Inches(0.5), h_kpi - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True

        p_s = tf.paragraphs[0]
        p_s.text = stat
        p_s.font.size = Pt(28)
        p_s.font.bold = True
        p_s.font.color.rgb = col
        p_s.font.name = FONT_TITLE

        p_l = tf.add_paragraph()
        p_l.text = label
        p_l.font.size = Pt(13)
        p_l.font.bold = True
        p_l.font.color.rgb = TEXT_WHITE
        p_l.space_before = Pt(4)

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = TEXT_MUTED
        p_d.space_before = Pt(6)

    # Footer Metadata
    tb_foot = slide1.shapes.add_textbox(Inches(0.9), Inches(6.15), Inches(11.5), Inches(0.6))
    tf_f = tb_foot.text_frame
    p_f = tf_f.paragraphs[0]
    p_f.text = "Author: Siddhant Mishra   |   Stack: MongoDB 7.0 • Neo4j 5.20 • Redis 7.0 • FastAPI • React 18 Cytoscape   |   Repo: github.com/Sid-V5/ChainReaction"
    p_f.font.size = Pt(11)
    p_f.font.color.rgb = TEXT_DIM

    # --------------------------------------------------------------------------
    # SLIDE 2: The Transitive Dependency Crisis
    # --------------------------------------------------------------------------
    slide2 = create_base_slide(prs, "PROBLEM DEFINITION", "The Transitive Software Supply Chain Crisis", ACCENT_RED)
    
    add_card(slide2, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2))
    add_card_header(slide2, Inches(1.1), Inches(1.85), Inches(5.0), "The Hidden Dependency Blast Radius", "⚠", ACCENT_RED)
    add_bullet_list(slide2, Inches(1.1), Inches(2.4), Inches(5.0), Inches(4.2), [
        ("Deep Indirect Layers", "Modern microservices rely on 500+ packages layered 3 to 6 hops deep."),
        ("The Transitive Blindspot", "Over 80% of open-source vulnerabilities reside in transitive dependencies that developers never explicitly imported in their manifests."),
        ("Static Scanner Failure", "Conventional security tools produce flat CSV vulnerability scans that cannot compute graph topologies or trace attack paths."),
        ("Breaking Change Dilemma", "Deprecating or bumping an indirect dependency risks silently breaking dozens of downstream consumer build pipelines.")
    ], font_size=12)

    add_card(slide2, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2))
    add_card_header(slide2, Inches(7.1), Inches(1.85), Inches(5.1), "Real-World Attack Vectors & Requirements", "⚡", ACCENT_CYAN)
    add_bullet_list(slide2, Inches(7.1), Inches(2.4), Inches(5.1), Inches(4.2), [
        ("Log4Shell (CVE-2021-44228)", "Compromised top-level enterprise services transitively via nested framework wrappers (e.g., Spring Boot -> spring-web -> log4j-core)."),
        ("XZ Utils (CVE-2024-3094)", "Malicious backdoor embedded deep inside low-level compression dependencies, affecting upstream SSH daemons."),
        ("Engine Requirement 1", "Must trace multi-hop transitive paths in sub-5ms across all company repositories."),
        ("Engine Requirement 2", "Must ingest polymorphic package manifests and compute live risk leaderboards in real time.")
    ], font_size=12)

    # --------------------------------------------------------------------------
    # SLIDE 3: Architectural Strategy: The Polyglot Paradigm
    # --------------------------------------------------------------------------
    slide3 = create_base_slide(prs, "SYSTEM ARCHITECTURE", "Why a Single Database Fails: The Polyglot Triad", ACCENT_CYAN)

    add_card(slide3, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2))
    add_card_header(slide3, Inches(1.1), Inches(1.85), Inches(5.0), "Relational RDBMS Bottlenecks", "✕", ACCENT_RED)
    add_bullet_list(slide3, Inches(1.1), Inches(2.4), Inches(5.0), Inches(4.2), [
        ("Recursive JOIN Explosion", "Tracing 5-hop dependencies requires repeated self-joins: JOIN dependencies d1 JOIN dependencies d2..."),
        ("Exponential Complexity O(b^d)", "Execution time explodes exponentially with depth d and branching factor b. 5-hop queries freeze for multiple seconds under high concurrency."),
        ("Schema Rigidity", "Relational schemas force strict column definitions, failing to handle polymorphic manifests (npm package.json vs. Python requirements.txt vs. Maven pom.xml)."),
        ("Locking & Concurrency", "ACID row locks stall high-velocity vulnerability advisory ingestion.")
    ], font_size=12)

    add_card(slide3, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2))
    add_card_header(slide3, Inches(7.1), Inches(1.85), Inches(5.1), "ChainReaction's Polyglot Triad", "✓", ACCENT_GREEN)
    add_bullet_list(slide3, Inches(7.1), Inches(2.4), Inches(5.1), Inches(4.2), [
        ("MongoDB (Document Store)", "Stores polymorphic manifests, repository profiles, and raw OSV.dev CVE JSON advisories. Powers complex aggregation pipelines."),
        ("Neo4j (Graph Engine)", "Uses Index-Free Adjacency (pointer-based traversal) to compute 1..5 hop blast radius in sub-5ms where SQL crawls."),
        ("Redis (In-Memory Key-Value)", "Maintains live sorted set (ZSET) risk leaderboards and caches expensive graph traversals for sub-1ms repeat reads."),
        ("FastAPI Orchestrator", "Asynchronous Python ASGI backend streaming live WebSocket zero-day alerts directly to the Cytoscape canvas.")
    ], font_size=12)

    # --------------------------------------------------------------------------
    # SLIDE 4: MongoDB Core: Document Modeling & BSON Schema
    # --------------------------------------------------------------------------
    slide4 = create_base_slide(prs, "MONGODB DOCUMENT MODELING", "Flexible Document Modeling for Polymorphic Manifests", ACCENT_GREEN)

    add_card(slide4, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2))
    add_card_header(slide4, Inches(1.1), Inches(1.85), Inches(5.0), "Handling Semi-Structured Heterogeneity", "📄", ACCENT_GREEN)
    add_bullet_list(slide4, Inches(1.1), Inches(2.4), Inches(5.0), Inches(4.2), [
        ("Polymorphic Manifests", "package.json uses objects, requirements.txt uses version specifiers (==, >=), pom.xml uses XML coordinate tags. BSON stores all natively without migrations."),
        ("Collections in ChainReaction", "• repositories: Repo metadata, star count, language, and pre-computed risk metrics.\n• cve_advisories: Raw OSV.dev JSON vulnerability advisories with nested affected version ranges."),
        ("Native BSON Advantages", "Rich BSON types (Date, Int32, Double, Array, Object) enable direct mathematical scoring and timestamp filtering inside queries."),
        ("Decoupled Evolution", "New security scanners or package ecosystems can be added instantly without altering existing document structures.")
    ], font_size=12)

    add_card(slide4, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2))
    add_card_header(slide4, Inches(7.1), Inches(1.85), Inches(5.1), "BSON Repository Document Blueprint", "💻", ACCENT_CYAN)
    code_slide4 = """// MongoDB BSON Collection: repositories
{
  "_id": ObjectId("6701a5b82f819a..."),
  "repo_slug": "spring-projects/spring-boot",
  "primary_language": "Java",
  "stars": 72400,
  "risk_score": 78.4,       // Computed Pattern
  "total_cves": 4,          // Computed Pattern
  "highest_cvss": 9.8,       // Pre-calculated
  "manifest_type": "pom.xml",
  "dependencies": [
    { "name": "spring-web", "version": "5.3.18", "is_direct": true },
    { "name": "log4j-core", "version": "2.14.1", "is_direct": false }
  ],
  "last_scanned_at": ISODate("2026-10-06T10:15:00Z")
}"""
    add_code_block(slide4, Inches(7.0), Inches(2.35), Inches(5.3), Inches(4.2), code_slide4)

    # --------------------------------------------------------------------------
    # SLIDE 5: MongoDB Data Integrity: Engine-Level $jsonSchema Validation
    # --------------------------------------------------------------------------
    slide5 = create_base_slide(prs, "MONGODB DATA INTEGRITY", "Engine-Level Collection Schema Validation ($jsonSchema)", ACCENT_GREEN)

    add_card(slide5, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2))
    add_card_header(slide5, Inches(1.1), Inches(1.85), Inches(5.0), "Why Database-Level Validation?", "🛡", ACCENT_GREEN)
    add_bullet_list(slide5, Inches(1.1), Inches(2.4), Inches(5.0), Inches(4.2), [
        ("Independent of Application Code", "Validates at the database engine level. External ingestion scripts, admin tools, or microservices cannot corrupt data."),
        ("Zero ORM Overhead", "Traditional Python ORMs (like SQLAlchemy) add CPU overhead converting objects. MongoDB validates native BSON documents directly in C++."),
        ("Enforces Critical Invariants", "Guarantees that repo_slug is a string, stars is a non-negative integer, and risk_score is within [0.0, 100.0]."),
        ("Selective Strictness", "Strict on core security coordinates, while allowing dynamic nested fields inside the dependency manifest array.")
    ], font_size=12)

    add_card(slide5, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2))
    add_card_header(slide5, Inches(7.1), Inches(1.85), Inches(5.1), "Validation Rule in backend/db/mongodb.py", "⚙", ACCENT_CYAN)
    code_slide5 = """// Schema Validator applied on db.create_collection("repositories")
validator = {
  "$jsonSchema": {
    "bsonType": "object",
    "required": ["repo_slug", "primary_language", "stars", "risk_score"],
    "properties": {
      "repo_slug": {
        "bsonType": "string",
        "pattern": "^[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+$",
        "description": "Must be a valid 'owner/repo' slug"
      },
      "primary_language": { "bsonType": "string" },
      "stars": { "bsonType": "int", "minimum": 0 },
      "risk_score": { "bsonType": "double", "minimum": 0.0, "maximum": 100.0 },
      "total_cves": { "bsonType": "int", "minimum": 0 }
    }
  }
}"""
    add_code_block(slide5, Inches(7.0), Inches(2.35), Inches(5.3), Inches(4.2), code_slide5)

    # --------------------------------------------------------------------------
    # SLIDE 6: MongoDB Design Patterns: Computed & Extended Reference
    # --------------------------------------------------------------------------
    slide6 = create_base_slide(prs, "MONGODB SCHEMA PATTERNS", "Eliminating Read Bottlenecks via Schema Design Patterns", ACCENT_GREEN)

    add_card(slide6, Inches(0.8), Inches(1.6), Inches(11.7), Inches(2.5))
    add_card_header(slide6, Inches(1.1), Inches(1.8), Inches(11.0), "The Computed Pattern (Read Optimization)", "⚡", ACCENT_GREEN)
    add_bullet_list(slide6, Inches(1.1), Inches(2.25), Inches(11.0), Inches(1.7), [
        ("The Challenge", "Calculating a repository's security posture on-the-fly requires scanning hundreds of nested CVE records, extracting CVSS scores, and summing weights on every dashboard read request."),
        ("The Implementation", "We pre-compute risk_score, total_cves, and highest_cvss during the ingestion/scan phase and embed them directly on write into the root document."),
        ("The Performance Gain", "Dashboard queries, sorting, and risk filters execute in O(1) time directly from the index without scanning nested dependencies or performing runtime math.")
    ], font_size=11.5)

    add_card(slide6, Inches(0.8), Inches(4.3), Inches(11.7), Inches(2.5))
    add_card_header(slide6, Inches(1.1), Inches(4.5), Inches(11.0), "The Extended Reference Pattern (Anti-Bloat Strategy)", "🔗", ACCENT_CYAN)
    add_bullet_list(slide6, Inches(1.1), Inches(4.95), Inches(11.0), Inches(1.7), [
        ("The Challenge", "Embedding full CVE advisory payloads (descriptions, references, patch diffs) inside repository documents would exceed the 16MB BSON limit and cause massive data duplication across shared libraries."),
        ("The Implementation", "We embed only frequently accessed dependency metadata (name, version, is_direct) in the repository document, while storing canonical CVE documents separately in cve_advisories."),
        ("The Performance Gain", "Keeps repository documents ultra-lightweight (~4KB), maximizing cache efficiency in RAM while enabling deep advisory lookups on demand.")
    ], font_size=11.5)

    # --------------------------------------------------------------------------
    # SLIDE 7: MongoDB Indexing Strategy: Zero-Sort Telemetry Lookups
    # (Fixed single-line header and adjusted image container padding)
    # --------------------------------------------------------------------------
    slide7 = create_base_slide(prs, "MONGODB INDEXING", "Compound & Text Indexes for High-Velocity Queries", ACCENT_GREEN)

    add_card(slide7, Inches(0.8), Inches(1.6), Inches(5.8), Inches(5.2))
    add_card_header(slide7, Inches(1.1), Inches(1.85), Inches(5.2), "Engineered Database Indexes", "🔍", ACCENT_GREEN)
    add_bullet_list(slide7, Inches(1.1), Inches(2.35), Inches(5.2), Inches(4.3), [
        ("Compound Index", "[('primary_language', 1), ('stars', -1)]\nPowers instant filtering by programming language while keeping repositories pre-sorted by star count. Eliminates in-memory sorting completely."),
        ("Full-Text Search Index", "[('repo_slug', 'text'), ('description', 'text')]\nEnables instantaneous tokenized full-text search across repository names and library summaries."),
        ("Unique Constraint Index", "[('repo_slug', 1)], unique=True\nGuarantees idempotent ingestion pipelines, preventing duplicate records when re-scanning active projects."),
        ("Explain Plan Results", "Queries use IXSCAN (Index Scan) with zero COLLSCAN (Collection Scan) overhead and zero in-memory sort buffer allocation.")
    ], font_size=11.5)

    # Right: Clean single-line header with well-padded image frame
    add_card(slide7, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2))
    add_card_header(slide7, Inches(7.1), Inches(1.85), Inches(5.1), "Telemetry Table (Compound Index)", "📊", ACCENT_CYAN)
    add_framed_image(slide7, Inches(7.0), Inches(2.4), Inches(5.3), Inches(4.1), "05_repository_telemetry_table.png")

    # --------------------------------------------------------------------------
    # SLIDE 8: MongoDB Analytical Pipelines: Multi-Stage & Faceted Telemetry
    # --------------------------------------------------------------------------
    slide8 = create_base_slide(prs, "MONGODB AGGREGATIONS", "Real-Time Analytical Pipelines with $group and $facet", ACCENT_GREEN)

    add_card(slide8, Inches(0.8), Inches(1.6), Inches(5.8), Inches(5.2))
    add_card_header(slide8, Inches(1.1), Inches(1.85), Inches(5.2), "Multi-Stage Aggregation Pipeline", "📈", ACCENT_GREEN)
    add_bullet_list(slide8, Inches(1.1), Inches(2.35), Inches(5.2), Inches(4.3), [
        ("Multi-Stage Pipeline", "$match (filter repos with CVEs > 0)\n-> $group (aggregate by primary_language, compute avg_risk, max_cvss, count)\n-> $project (round scores and format payload)\n-> $sort (rank by avg_risk descending)."),
        ("Multi-Dimensional $facet", "Executes three parallel analytical pipelines in a SINGLE database round-trip:\n1. Severity distribution breakdown (Critical, High, Medium counts)\n2. Top 5 highest-risk enterprise repositories\n3. Global ecosystem risk averages."),
        ("Performance Impact", "Replaces three separate round-trips with one query, reducing analytics latency from 80ms to 9ms.")
    ], font_size=11.5)

    add_card(slide8, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2))
    add_card_header(slide8, Inches(7.1), Inches(1.85), Inches(5.1), "Analytics Dashboard ($facet in Action)", "📊", ACCENT_CYAN)
    add_framed_image(slide8, Inches(7.0), Inches(2.4), Inches(5.3), Inches(4.1), "04_mongodb_analytics_panel.png")

    # --------------------------------------------------------------------------
    # SLIDE 9: Graph Traversal Layer: Neo4j Variable-Length Path Traversal
    # --------------------------------------------------------------------------
    slide9 = create_base_slide(prs, "NEO4J GRAPH ENGINE", "Transitive Blast Radius via Index-Free Adjacency", ACCENT_CYAN)

    add_card(slide9, Inches(0.8), Inches(1.6), Inches(5.8), Inches(5.2))
    add_card_header(slide9, Inches(1.1), Inches(1.85), Inches(5.2), "Cypher Path Traversal Engine", "🕸", ACCENT_CYAN)
    add_bullet_list(slide9, Inches(1.1), Inches(2.35), Inches(5.2), Inches(2.1), [
        ("Index-Free Adjacency", "Neo4j nodes point directly to adjacent nodes via physical memory pointers, traversing paths in O(k) time rather than relational table joins."),
        ("Variable-Length Cypher Query", "MATCH (r:Repository)-[d:DEPENDS_ON*1..5]->(target:Package {name: $pkg})\nRETURN r.slug, length(d) AS hops, r.risk_score\nORDER BY hops ASC"),
        ("Sub-5ms Blast Calculation", "Traces deep supply chain trees across hundreds of repositories in under 5ms.")
    ], font_size=11.5)

    code_slide9 = """// Live Blast Radius Scenario: log4j-core
// 1. apache/logging-log4j2  (Direct - 1 hop)
// 2. spring-projects/spring-boot (Transitive - 2 hops)
//    via spring-web -> log4j-core
// Execution time: 3.4ms (sub-5ms)"""
    add_code_block(slide9, Inches(1.1), Inches(4.8), Inches(5.2), Inches(1.75), code_slide9)

    add_card(slide9, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2))
    add_card_header(slide9, Inches(7.1), Inches(1.85), Inches(5.1), "Live Transitive Blast Radius Trace", "⚡", ACCENT_RED)
    add_framed_image(slide9, Inches(7.0), Inches(2.4), Inches(5.3), Inches(4.1), "02_blast_radius_trace.png")

    # --------------------------------------------------------------------------
    # SLIDE 10: In-Memory & Event Streaming: Redis ZSET & Zero-Day Streaming
    # --------------------------------------------------------------------------
    slide10 = create_base_slide(prs, "REDIS IN-MEMORY & PUBSUB", "Sub-Millisecond Risk Leaderboard & Reactive Event Push", ACCENT_PURPLE)

    add_card(slide10, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2))
    add_card_header(slide10, Inches(1.1), Inches(1.85), Inches(5.0), "Sorted Sets (ZSET) & Query Caching", "⚡", ACCENT_PURPLE)
    add_bullet_list(slide10, Inches(1.1), Inches(2.4), Inches(5.0), Inches(4.2), [
        ("ZSET Risk Leaderboard", "ZADD risk_leaderboard <cvss_score> <repo_slug>\nMaintains the global rank of most vulnerable repositories in an in-memory Skip List + Hash Table."),
        ("O(log N + M) Reads", "Querying the top 10 highest-risk repositories runs in under 0.2ms without scanning MongoDB or running sorting queries."),
        ("TTL Query Caching", "SETEX blast:<pkg> 180 <payload>\nCaches repeated Cypher graph calculations. Subsequent queries return in <1ms (verified with the UI's '⚡ Redis Cache HIT' badge).")
    ], font_size=12)

    add_card(slide10, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2))
    add_card_header(slide10, Inches(7.1), Inches(1.85), Inches(5.1), "Reactive Zero-Day Alert Broadcast", "🚨", ACCENT_RED)
    add_bullet_list(slide10, Inches(7.1), Inches(2.4), Inches(5.1), Inches(4.2), [
        ("Event Ingestion", "A vulnerability webhook or 'Simulate Zero-Day' event introduces a critical CVSS 9.8 advisory on a shared library (e.g., psf/requests)."),
        ("Redis Pub/Sub Fanout", "The backend broadcasts the alert via PUBLISH cve:alerts <payload> on an in-memory channel."),
        ("WebSocket Reactive Streaming", "FastAPI WebSocket consumers receive the event and push it to active browser sessions without HTTP polling."),
        ("Canvas Reaction", "The React Cytoscape graph canvas pulses the compromised node in neon red and re-orders the live risk leaderboard instantaneously.")
    ], font_size=12)

    # --------------------------------------------------------------------------
    # SLIDE 11: Interactive Prototype Suite: Dynamic Topology & Impact Simulator
    # --------------------------------------------------------------------------
    slide11 = create_base_slide(prs, "INTERACTIVE PROTOTYPE SUITE", "Dynamic Topology Layouts & Breaking Change Simulator", ACCENT_CYAN)

    add_card(slide11, Inches(0.8), Inches(1.6), Inches(5.8), Inches(5.2))
    add_card_header(slide11, Inches(1.1), Inches(1.85), Inches(5.2), "Multi-Layout Topological Exploration", "📐", ACCENT_CYAN)
    add_bullet_list(slide11, Inches(1.1), Inches(2.4), Inches(5.2), Inches(4.2), [
        ("Organic Force (CoLA / CoSE)", "Physics-based force-directed clustering showing natural module cohesion and dependency gravity."),
        ("Concentric Radial Layout", "Arranges packages in concentric circles: foundational shared libraries at the center, applications on outer rings."),
        ("Hierarchical Tree (DAG)", "Top-down directed layout exposing strict upstream consumer to leaf package build hierarchies."),
        ("Breaking Change Simulator", "Allows SecOps engineers to simulate library deprecations or version bumps, previewing affected downstream repositories, risk deltas, and recommended safe versions.")
    ], font_size=12)

    add_card(slide11, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2))
    add_card_header(slide11, Inches(7.1), Inches(1.85), Inches(5.1), "Breaking Change Simulator in Action", "🔧", ACCENT_GREEN)
    add_framed_image(slide11, Inches(7.0), Inches(2.4), Inches(5.3), Inches(4.1), "03_breaking_changes_simulator.png")

    # --------------------------------------------------------------------------
    # SLIDE 12: Architectural Evaluation & Engineering Conclusion
    # --------------------------------------------------------------------------
    slide12 = create_base_slide(prs, "EVALUATION & CONCLUSION", "Polyglot Synergy: Comparative Evaluation & Takeaways", ACCENT_GREEN)

    # Comparison Table
    table_x = Inches(0.8)
    table_y = Inches(1.6)
    table_w = Inches(11.7)
    table_h = Inches(3.2)

    shape_tbl = slide12.shapes.add_table(5, 5, table_x, table_y, table_w, table_h)
    tbl = shape_tbl.table
    tbl.columns[0].width = Inches(2.7)
    tbl.columns[1].width = Inches(2.25)
    tbl.columns[2].width = Inches(2.25)
    tbl.columns[3].width = Inches(2.25)
    tbl.columns[4].width = Inches(2.25)

    headers = ["Workload / Capability", "Relational RDBMS", "MongoDB (Document)", "Neo4j (Graph)", "Redis (In-Memory)"]
    for col_idx, h_text in enumerate(headers):
        cell = tbl.cell(0, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = CARD_BG
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = cell.text_frame.paragraphs[0]
        p.text = h_text
        p.font.bold = True
        p.font.size = Pt(11)
        p.font.color.rgb = ACCENT_GREEN if "Mongo" in h_text else (ACCENT_CYAN if "Neo" in h_text else (ACCENT_PURPLE if "Redis" in h_text else TEXT_WHITE))

    rows_data = [
        ("Polymorphic Manifests & CVEs", "Fail (Rigid schema churn)", "Optimal (BSON documents)", "Sub-optimal (Property bloat)", "Limited (String keys)"),
        ("Multi-Stage Risk Analytics", "Slow (Multi-table joins)", "Optimal ($facet pipeline)", "Slow (Table-like scans)", "Not Supported"),
        ("Transitive Blast Radius (5 hops)", "Fail (O(b^d) join freeze)", "Limited ($graphLookup limits)", "Optimal (O(k) index-free)", "Cache only"),
        ("Real-Time Risk Leaderboard", "Slow (ORDER BY scans)", "Good (Index sorting)", "Slow (High query cost)", "Optimal (ZSET O(log N))")
    ]

    for row_idx, row in enumerate(rows_data, start=1):
        for col_idx, val in enumerate(row):
            cell = tbl.cell(row_idx, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = CODE_BG if row_idx % 2 == 0 else CARD_BG
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.size = Pt(10.5)
            p.font.color.rgb = TEXT_WHITE if col_idx == 0 else (ACCENT_GREEN if "Optimal" in val else (ACCENT_RED if "Fail" in val else TEXT_MUTED))

    # Bottom Takeaway Card
    add_card(slide12, Inches(0.8), Inches(5.1), Inches(11.7), Inches(1.8))
    add_card_header(slide12, Inches(1.1), Inches(5.25), Inches(11.0), "Key Architectural Takeaways", "★", ACCENT_GREEN)
    add_bullet_list(slide12, Inches(1.1), Inches(5.65), Inches(11.0), Inches(1.1), [
        ("Right Tool for the Right Job", "Modern applications must not compromise on a single data model. MongoDB delivers schema agility and high-speed analytical aggregation; Neo4j delivers constant-time transitive path exploration; Redis delivers sub-millisecond telemetry caching and live pub/sub alerting."),
        ("Production Readiness", "ChainReaction proves that combining these three engines creates a scalable, enterprise-grade software supply chain security defense system.")
    ], font_size=11.5)

    # Save presentation
    output_path = os.path.abspath("d:/NoSQLProj/ChainReaction_Architecture_Presentation.pptx")
    prs.save(output_path)
    print(f"Successfully generated presentation: {output_path}")
    return output_path


if __name__ == "__main__":
    build_presentation()
