"""
Build PDF della Guida agli Agenti AI — design editoriale, bilingue (IT/EN).

Uso:
    python3 build_pdf.py            # genera entrambe le versioni
    python3 build_pdf.py it         # solo italiano
    python3 build_pdf.py en         # solo inglese
"""

import os
import re
import sys
import html
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString
import markdown as md

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak,
    Preformatted, Table, TableStyle, ListFlowable, ListItem, KeepTogether,
)
from reportlab.platypus.flowables import HRFlowable
from reportlab.platypus.doctemplate import NextPageTemplate

ROOT = Path(__file__).resolve().parent

AUTHOR = "Gabriele Bottai"
YEAR = "2026"

# ----- Palette (warm minimal, coordinata col sito) -----
INK = colors.HexColor("#1a1a1a")
INK_SOFT = colors.HexColor("#3a3a3a")
INK_MUTE = colors.HexColor("#737370")
LINE = colors.HexColor("#dbdbd2")
LINE_SOFT = colors.HexColor("#ededdf")
BG = colors.HexColor("#fcfcf9")
BG_SOFT = colors.HexColor("#f4f3eb")
ACCENT = colors.HexColor("#d4533c")
ACCENT_SOFT = colors.HexColor("#fbe8e2")
ACCENT_DEEP = colors.HexColor("#a83b27")
SUCCESS = colors.HexColor("#2e7d52")
SUCCESS_SOFT = colors.HexColor("#e6f3eb")
WARNING = colors.HexColor("#b86e00")
WARNING_SOFT = colors.HexColor("#fef0d9")

# ----- i18n labels -----
LABELS = {
    "it": {
        "title": "Guida agli\nAgenti AI",
        "subtitle": "Una guida completa, dai fondamenti alla produzione.",
        "by": "scritta da",
        "edition": f"Edizione {YEAR}",
        "copyright_title": "Copyright e licenza",
        "copyright_body": (
            f"<b>© {YEAR} {AUTHOR}. Tutti i diritti riservati.</b><br/><br/>"
            "Quest'opera è protetta dalle leggi sul diritto d'autore. Nessuna parte di "
            "questa pubblicazione può essere riprodotta, distribuita, ritrasmessa o "
            "rivenduta in qualsiasi forma o con qualsiasi mezzo, elettronico o meccanico, "
            "incluse fotocopie, registrazioni o altri sistemi di archiviazione e recupero "
            "delle informazioni, senza il previo permesso scritto dell'autore, salvo i "
            "casi consentiti dalla legge sul diritto d'autore.<br/><br/>"
            "La rivendita non autorizzata, la ridistribuzione commerciale o la "
            "ripubblicazione di questo documento — in tutto o in parte — costituiscono "
            "violazione del diritto d'autore e saranno perseguite a termini di legge.<br/><br/>"
            "Il contenuto è fornito a scopo informativo ed educativo. L'autore non "
            "garantisce l'accuratezza, completezza o adeguatezza delle informazioni a "
            "fini specifici. L'uso delle tecniche descritte è a discrezione e "
            "responsabilità del lettore.<br/><br/>"
            f"<i>Firmato:</i> <b>{AUTHOR}</b><br/>"
            f"<i>Edizione:</i> {YEAR}<br/>"
            "<i>Documento originale:</i> Guida agli Agenti AI"
        ),
        "toc": "Indice",
        "part_intro": "Parte",
        "chapter_intro": "Capitolo",
        "footer_rights": "Tutti i diritti riservati",
        "page": "Pag.",
        "watermark": f"© {AUTHOR} {YEAR}  ·  Guida Agenti AI",
        "parts": [
            ("Parte 1", "Fondamenti", "I quattro mattoni che servono per capire tutto il resto."),
            ("Parte 2", "Tecniche essenziali", "Come parlare con i modelli e dare loro mani e occhi."),
            ("Parte 3", "Usare gli agenti", "Pratica quotidiana: chatbot, terminale, workflow."),
            ("Parte 4", "Costruire agenti", "Codice tuo, dall'SDK ai framework."),
            ("Parte 5", "Lavorare bene", "Qualità, sicurezza, costi — produzione vera."),
            ("Parte 6", "Applicazioni", "Casi d'uso reali e risorse per andare oltre."),
        ],
    },
    "en": {
        "title": "Guide to\nAI Agents",
        "subtitle": "A complete guide, from fundamentals to production.",
        "by": "by",
        "edition": f"{YEAR} edition",
        "copyright_title": "Copyright and license",
        "copyright_body": (
            f"<b>© {YEAR} {AUTHOR}. All rights reserved.</b><br/><br/>"
            "This work is protected under copyright law. No part of this publication "
            "may be reproduced, distributed, retransmitted, or resold in any form or by "
            "any means, electronic or mechanical, including photocopying, recording, or "
            "other storage and retrieval systems, without the prior written permission "
            "of the author, except as permitted by copyright law.<br/><br/>"
            "Unauthorized resale, commercial redistribution, or republication of this "
            "document — in whole or in part — constitutes copyright infringement and "
            "will be prosecuted to the full extent of the law.<br/><br/>"
            "Content is provided for informational and educational purposes. The author "
            "makes no warranty as to the accuracy, completeness, or fitness of the "
            "information for any specific purpose. Use of the techniques described is "
            "at the reader's discretion and responsibility.<br/><br/>"
            f"<i>Signed:</i> <b>{AUTHOR}</b><br/>"
            f"<i>Edition:</i> {YEAR}<br/>"
            "<i>Original document:</i> Guide to AI Agents"
        ),
        "toc": "Contents",
        "part_intro": "Part",
        "chapter_intro": "Chapter",
        "footer_rights": "All rights reserved",
        "page": "p.",
        "watermark": f"© {AUTHOR} {YEAR}  ·  Guide to AI Agents",
        "parts": [
            ("Part 1", "Fundamentals", "The four building blocks needed to understand everything else."),
            ("Part 2", "Essential techniques", "How to talk to models and give them hands and eyes."),
            ("Part 3", "Using agents", "Day-to-day practice: chatbots, terminal, workflows."),
            ("Part 4", "Building agents", "Your own code, from SDK to frameworks."),
            ("Part 5", "Working well", "Quality, security, cost — real production."),
            ("Part 6", "Applications", "Real-world use cases and resources to go further."),
        ],
    },
}

# Chapter manifest — slugs IT (root) and slugs EN (en/ subdir, same slug)
CHAPTERS_IT = [
    "01-cosa-sono-gli-agenti-ai",
    "02-come-funzionano-gli-llm",
    "03-anatomia-di-un-agente",
    "04-tipi-di-agenti-e-architetture",
    "05-prompt-engineering",
    "06-tool-use-e-function-calling",
    "07-memoria-contesto-e-rag",
    "08-usare-i-chatbot-ai",
    "09-claude-code-per-sviluppatori",
    "10-costruire-agenti-con-api-sdk",
    "11-framework-langchain-autogen-crewai",
    "12-best-practice-sviluppo-con-agenti",
    "13-sicurezza-costi-e-limiti",
    "14-valutazione-e-miglioramento",
    "15-casi-uso-e-workflow-reali",
    "16-glossario-e-risorse",
]

# Boundaries: chapter index → part index (1-based)
CHAPTER_TO_PART = {
    1: 1, 2: 1, 3: 1, 4: 1,
    5: 2, 6: 2, 7: 2,
    8: 3, 9: 3,
    10: 4, 11: 4,
    12: 5, 13: 5, 14: 5,
    15: 6, 16: 6,
}

# Fonts
FONTS = {
    "base": "Helvetica",
    "bold": "Helvetica-Bold",
    "italic": "Helvetica-Oblique",
    "bolditalic": "Helvetica-BoldOblique",
    "serif": "Times-Roman",
    "serif_bold": "Times-Bold",
    "serif_italic": "Times-Italic",
    "mono": "Courier",
    "mono_bold": "Courier-Bold",
}


# ============================================================================
# Styles
# ============================================================================
def make_styles():
    body = ParagraphStyle(
        "Body",
        fontName=FONTS["base"], fontSize=10.5, leading=15.5,
        alignment=TA_JUSTIFY, spaceAfter=8, textColor=INK,
    )
    return {
        "CoverEyebrow": ParagraphStyle(
            "CoverEyebrow", parent=body, fontName=FONTS["bold"],
            fontSize=10, leading=14, alignment=TA_CENTER,
            spaceAfter=4, textColor=ACCENT, allowWidows=0,
        ),
        "CoverTitle": ParagraphStyle(
            "CoverTitle", parent=body, fontName=FONTS["bold"],
            fontSize=58, leading=62, alignment=TA_CENTER,
            spaceAfter=12, textColor=INK, allowWidows=0,
        ),
        "CoverSub": ParagraphStyle(
            "CoverSub", parent=body, fontName=FONTS["serif_italic"],
            fontSize=16, leading=22, alignment=TA_CENTER,
            spaceAfter=24, textColor=INK_SOFT,
        ),
        "CoverAuthor": ParagraphStyle(
            "CoverAuthor", parent=body, fontName=FONTS["base"],
            fontSize=11, leading=15, alignment=TA_CENTER,
            spaceAfter=4, textColor=INK_MUTE, allowWidows=0,
        ),
        "CoverAuthorName": ParagraphStyle(
            "CoverAuthorName", parent=body, fontName=FONTS["bold"],
            fontSize=18, leading=22, alignment=TA_CENTER,
            spaceAfter=4, textColor=INK,
        ),
        "CoverEdition": ParagraphStyle(
            "CoverEdition", parent=body, fontName=FONTS["base"],
            fontSize=10, leading=14, alignment=TA_CENTER,
            textColor=INK_MUTE, allowWidows=0,
        ),

        "PartLabel": ParagraphStyle(
            "PartLabel", parent=body, fontName=FONTS["bold"],
            fontSize=11, leading=14, alignment=TA_LEFT,
            spaceAfter=6, textColor=ACCENT,
            wordWrap="LTR", leftIndent=0,
        ),
        "PartNumber": ParagraphStyle(
            "PartNumber", parent=body, fontName=FONTS["bold"],
            fontSize=120, leading=110, alignment=TA_LEFT,
            textColor=LINE,
        ),
        "PartTitle": ParagraphStyle(
            "PartTitle", parent=body, fontName=FONTS["bold"],
            fontSize=42, leading=46, alignment=TA_LEFT,
            spaceAfter=12, textColor=INK,
        ),
        "PartTagline": ParagraphStyle(
            "PartTagline", parent=body, fontName=FONTS["serif_italic"],
            fontSize=14, leading=20, alignment=TA_LEFT,
            textColor=INK_SOFT,
        ),

        "ChapterEyebrow": ParagraphStyle(
            "ChapterEyebrow", parent=body, fontName=FONTS["bold"],
            fontSize=9, leading=12, alignment=TA_LEFT,
            spaceAfter=4, textColor=ACCENT,
        ),
        "ChapterNumber": ParagraphStyle(
            "ChapterNumber", parent=body, fontName=FONTS["bold"],
            fontSize=82, leading=80, alignment=TA_LEFT,
            textColor=LINE_SOFT, spaceAfter=-30,
        ),
        "ChapterTitle": ParagraphStyle(
            "ChapterTitle", parent=body, fontName=FONTS["bold"],
            fontSize=30, leading=34, alignment=TA_LEFT,
            spaceAfter=10, textColor=INK,
        ),
        "ChapterIntro": ParagraphStyle(
            "ChapterIntro", parent=body, fontName=FONTS["serif_italic"],
            fontSize=12, leading=18, alignment=TA_LEFT,
            spaceAfter=14, textColor=INK_SOFT,
        ),
        "TOCTitle": ParagraphStyle(
            "TOCTitle", parent=body, fontName=FONTS["bold"],
            fontSize=42, leading=46, alignment=TA_LEFT,
            spaceAfter=18, textColor=INK,
        ),
        "TOCPart": ParagraphStyle(
            "TOCPart", parent=body, fontName=FONTS["bold"],
            fontSize=11, leading=14, alignment=TA_LEFT,
            spaceBefore=14, spaceAfter=8, textColor=ACCENT,
        ),
        "TOCEntry": ParagraphStyle(
            "TOCEntry", parent=body, fontSize=10.5, leading=16,
            alignment=TA_LEFT, spaceAfter=2, textColor=INK,
        ),

        "H1": ParagraphStyle(
            "H1", parent=body, fontName=FONTS["bold"],
            fontSize=22, leading=28, alignment=TA_LEFT,
            spaceBefore=4, spaceAfter=10, textColor=INK,
            keepWithNext=True,
        ),
        "H2": ParagraphStyle(
            "H2", parent=body, fontName=FONTS["bold"],
            fontSize=14.5, leading=20, alignment=TA_LEFT,
            spaceBefore=14, spaceAfter=6, textColor=INK,
            keepWithNext=True,
        ),
        "H3": ParagraphStyle(
            "H3", parent=body, fontName=FONTS["bold"],
            fontSize=11.5, leading=16, alignment=TA_LEFT,
            spaceBefore=10, spaceAfter=4, textColor=INK,
            keepWithNext=True,
        ),
        "H4": ParagraphStyle(
            "H4", parent=body, fontName=FONTS["bolditalic"],
            fontSize=10.5, leading=14, alignment=TA_LEFT,
            spaceBefore=8, spaceAfter=2, textColor=INK_SOFT,
            keepWithNext=True,
        ),
        "Body": body,

        "BulletItem": ParagraphStyle(
            "BulletItem", parent=body, leftIndent=14, bulletIndent=2,
            spaceAfter=2, alignment=TA_LEFT,
        ),
        "Quote": ParagraphStyle(
            "Quote", parent=body, leftIndent=20, rightIndent=14,
            fontName=FONTS["serif_italic"], fontSize=12, leading=18,
            textColor=INK_SOFT, alignment=TA_LEFT,
            borderColor=ACCENT, borderPadding=(10, 14, 10, 14),
            backColor=ACCENT_SOFT, spaceBefore=10, spaceAfter=12,
        ),
        "Code": ParagraphStyle(
            "Code", parent=body, fontName=FONTS["mono"],
            fontSize=8.2, leading=10.5, alignment=TA_LEFT,
            backColor=colors.HexColor("#1a1d23"),
            textColor=colors.HexColor("#e8e8e3"),
            borderPadding=(8, 10, 8, 10),
            leftIndent=0, rightIndent=0,
            spaceBefore=8, spaceAfter=10,
        ),

        "TableCell": ParagraphStyle(
            "TableCell", parent=body, fontSize=9.5, leading=13,
            alignment=TA_LEFT, spaceAfter=0,
        ),
        "TableHeader": ParagraphStyle(
            "TableHeader", parent=body, fontSize=9.5, leading=13,
            alignment=TA_LEFT, spaceAfter=0,
            fontName=FONTS["bold"], textColor=colors.white,
        ),
    }


# ============================================================================
# Markdown → flowables
# ============================================================================
def md_inline_to_rl(html_text: str) -> str:
    soup = BeautifulSoup(html_text, "html.parser")

    def render(node) -> str:
        if isinstance(node, NavigableString):
            return html.escape(str(node))
        tag = node.name
        inner = "".join(render(c) for c in node.children)
        if tag in ("strong", "b"): return f"<b>{inner}</b>"
        if tag in ("em", "i"): return f"<i>{inner}</i>"
        if tag == "code":
            return f'<font name="{FONTS["mono"]}" size="9" backColor="#f4f3eb"> {inner} </font>'
        if tag == "a":
            href = node.get("href", "")
            if href.startswith("http"):
                return f'<link href="{html.escape(href)}" color="#a83b27"><u>{inner}</u></link>'
            return inner
        if tag == "br": return "<br/>"
        if tag in ("del", "s"): return f"<strike>{inner}</strike>"
        return inner

    return "".join(render(c) for c in soup.children).strip()


def parse_markdown_to_flowables(md_text: str, styles: dict, lang: str,
                                 chapter_n: int = None, chapter_title: str = None) -> list:
    """Parse markdown del capitolo. Riconosce i pattern delle nostre 'box':
       'X.X Da ricordare', 'X.X Errori tipici', 'X.X Pratica:' → callout boxes."""
    html_text = md.markdown(
        md_text,
        extensions=["fenced_code", "tables", "sane_lists", "nl2br"],
    )
    soup = BeautifulSoup(html_text, "html.parser")

    flowables = []
    section_kind = "normal"  # "remember", "errors", "practice", "normal"

    # Capitolo: opener (eyebrow + numero + title) — solo se chapter_n fornito
    # Sostituisce l'h1 originale del markdown
    chapter_opener_added = False

    def render_inline_html(elem) -> str:
        return md_inline_to_rl(str(elem.decode_contents()))

    def detect_section_kind(text: str) -> str:
        t = text.lower()
        if "da ricordare" in t or "key takeaways" in t or "to remember" in t:
            return "remember"
        if "errori tipici" in t or "common mistakes" in t or "common errors" in t:
            return "errors"
        if "pratica" in t.split() or t.startswith("pratica") or "practice" in t.split() or t.startswith("practice"):
            return "practice"
        return "normal"

    def render_list(ul_or_ol, ordered=False, depth=0, kind="normal"):
        items = []
        for li in ul_or_ol.find_all("li", recursive=False):
            inner = []
            sub_lists = []
            for child in li.children:
                if isinstance(child, NavigableString):
                    inner.append(html.escape(str(child)))
                elif child.name in ("ul", "ol"):
                    sub_lists.append(child)
                else:
                    inner.append(md_inline_to_rl(str(child)))
            text = "".join(inner).strip()
            # Stile differenziato in base al kind
            style = styles["BulletItem"]
            if kind == "remember":
                style = ParagraphStyle("li_remember", parent=style, textColor=INK, leftIndent=18)
            elif kind == "errors":
                style = ParagraphStyle("li_errors", parent=style, textColor=INK, leftIndent=18)
            bullet_para = Paragraph(text, style)
            sub_flowables = [bullet_para]
            for sl in sub_lists:
                nested = render_list(sl, ordered=(sl.name == "ol"), depth=depth+1, kind=kind)
                sub_flowables.extend(nested)
            items.append(ListItem(sub_flowables, leftIndent=10))
        start = 1
        if ordered and ul_or_ol.has_attr("start"):
            try:
                start = int(ul_or_ol["start"])
            except (TypeError, ValueError):
                start = 1
        bullet_color = INK_MUTE
        if kind == "remember":
            bullet_color = SUCCESS
        elif kind == "errors":
            bullet_color = ACCENT
        return [ListFlowable(
            items,
            bulletType=("1" if ordered else "bullet"),
            start=(start if ordered else None),
            leftIndent=18, bulletFontSize=8, bulletColor=bullet_color,
        )]

    def render_table(tbl):
        rows = []
        thead = tbl.find("thead")
        if thead:
            header_cells = [
                Paragraph(md_inline_to_rl(str(th.decode_contents())), styles["TableHeader"])
                for th in thead.find_all("th")
            ]
            rows.append(header_cells)
        body = tbl.find("tbody") or tbl
        for tr in body.find_all("tr"):
            cells = [
                Paragraph(md_inline_to_rl(str(td.decode_contents())), styles["TableCell"])
                for td in tr.find_all(["td", "th"])
            ]
            if cells:
                rows.append(cells)
        if not rows:
            return None
        ncols = max(len(r) for r in rows)
        for r in rows:
            while len(r) < ncols:
                r.append(Paragraph("", styles["TableCell"]))
        avail_width = A4[0] - 36 * mm
        col_widths = [avail_width / ncols] * ncols
        t = Table(rows, colWidths=col_widths, repeatRows=1, hAlign="LEFT")
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), INK),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG_SOFT]),
            ("BOX", (0, 0), (-1, -1), 0.4, LINE),
            ("INNERGRID", (0, 0), (-1, -1), 0.3, LINE_SOFT),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        return t

    def make_callout_box(content_flowables, kind):
        """Wrap flowables in a colored callout box."""
        if kind == "remember":
            bg = SUCCESS_SOFT
            border = SUCCESS
            label = "Da ricordare" if lang == "it" else "Key takeaways"
        elif kind == "errors":
            bg = colors.HexColor("#fef0d9")
            border = WARNING
            label = "Errori tipici" if lang == "it" else "Common mistakes"
        elif kind == "practice":
            bg = colors.HexColor("#eef4f7")
            border = colors.HexColor("#1f7a8c")
            label = "Pratica" if lang == "it" else "Practice"
        else:
            return content_flowables

        # Create label as styled paragraph
        label_style = ParagraphStyle(
            "callout_label", fontName=FONTS["bold"], fontSize=8.5, leading=11,
            alignment=TA_LEFT, textColor=border, spaceAfter=4,
        )
        label_para = Paragraph(label.upper(), label_style)
        inner = [label_para] + content_flowables

        wrapper = Table([[inner]], colWidths=[A4[0] - 36 * mm])
        wrapper.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), bg),
            ("BOX", (0, 0), (-1, -1), 0, border),
            ("LINEBEFORE", (0, 0), (0, -1), 3, border),
            ("LEFTPADDING", (0, 0), (-1, -1), 14),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        return [Spacer(1, 4), wrapper, Spacer(1, 8)]

    # ----- Walk top-level elements -----
    pending_section = None
    current_kind = "normal"
    pending_flowables = []  # accumulates flowables for current callout section

    def flush_pending():
        """Emit accumulated callout-section flowables."""
        nonlocal pending_section, pending_flowables, current_kind
        if pending_section is not None and pending_flowables:
            flowables.extend(make_callout_box(pending_flowables, pending_section))
            pending_flowables = []
        pending_section = None
        current_kind = "normal"

    for elem in soup.children:
        if isinstance(elem, NavigableString):
            continue
        name = elem.name
        text_raw = re.sub(r"<[^>]+>", "", str(elem.decode_contents() if hasattr(elem, "decode_contents") else elem))

        # Chapter opener: replace original h1 with our designed opener
        if name == "h1":
            flush_pending()
            if chapter_n is not None and not chapter_opener_added:
                eyebrow = f"{LABELS[lang]['chapter_intro']} {chapter_n}"
                flowables.append(Paragraph(eyebrow.upper(), styles["ChapterEyebrow"]))
                flowables.append(Paragraph(f"{chapter_n:02d}", styles["ChapterNumber"]))
                title_text = md_inline_to_rl(str(elem.decode_contents()))
                title_text = re.sub(r"^\s*\d+\.\s*", "", title_text)
                title_para = Paragraph(title_text, styles["ChapterTitle"])
                # Outline title: strip HTML tags and decode entities for clean display
                title_clean = html.unescape(re.sub(r"<[^>]+>", "", title_text))
                title_para._bookmark = (f"{LABELS[lang]['chapter_intro']} {chapter_n}. {title_clean}", 1)
                flowables.append(title_para)
                flowables.append(HRFlowable(width="60", thickness=1.5,
                                             color=ACCENT, spaceBefore=4, spaceAfter=14, hAlign="LEFT"))
                chapter_opener_added = True
            else:
                flowables.append(Paragraph(md_inline_to_rl(str(elem.decode_contents())), styles["H1"]))
        elif name == "h2":
            flush_pending()
            text = md_inline_to_rl(str(elem.decode_contents()))
            kind = detect_section_kind(re.sub(r"<[^>]+>", "", text))
            if kind in ("remember", "errors", "practice"):
                pending_section = kind
                current_kind = kind
                inner_h_style = ParagraphStyle(
                    "callout_h", fontName=FONTS["bold"], fontSize=12, leading=16,
                    alignment=TA_LEFT, textColor=INK, spaceAfter=6,
                )
                pending_flowables.append(Paragraph(text, inner_h_style))
            else:
                h2_para = Paragraph(text, styles["H2"])
                text_clean = html.unescape(re.sub(r"<[^>]+>", "", text))
                h2_para._bookmark = (text_clean, 2)
                flowables.append(h2_para)
        elif name == "h3":
            text = md_inline_to_rl(str(elem.decode_contents()))
            target = pending_flowables if pending_section else flowables
            target.append(Paragraph(text, styles["H3"]))
        elif name == "h4":
            text = md_inline_to_rl(str(elem.decode_contents()))
            target = pending_flowables if pending_section else flowables
            target.append(Paragraph(text, styles["H4"]))
        elif name == "p":
            text = md_inline_to_rl(str(elem.decode_contents()))
            if not text.strip():
                continue
            target = pending_flowables if pending_section else flowables
            # Chapter intro: first paragraph after opener gets special treatment
            if chapter_opener_added and not pending_section and not any(
                isinstance(f, Paragraph) and f.style.name == "Body" for f in flowables
            ):
                target.append(Paragraph(text, styles["ChapterIntro"]))
            else:
                target.append(Paragraph(text, styles["Body"]))
        elif name == "blockquote":
            inner_p = elem.find("p")
            text = md_inline_to_rl(str(inner_p.decode_contents())) if inner_p else md_inline_to_rl(str(elem.decode_contents()))
            target = pending_flowables if pending_section else flowables
            target.append(Paragraph(text, styles["Quote"]))
        elif name == "ul":
            target = pending_flowables if pending_section else flowables
            target.extend(render_list(elem, ordered=False, kind=current_kind))
        elif name == "ol":
            target = pending_flowables if pending_section else flowables
            target.extend(render_list(elem, ordered=True, kind=current_kind))
        elif name == "pre":
            code_elem = elem.find("code")
            code_text = code_elem.get_text() if code_elem else elem.get_text()
            code_para = Preformatted(code_text.rstrip(), styles["Code"], maxLineLength=98)
            target = pending_flowables if pending_section else flowables
            target.append(code_para)
        elif name == "table":
            t = render_table(elem)
            if t:
                target = pending_flowables if pending_section else flowables
                target.append(KeepTogether(t))
                target.append(Spacer(1, 6))
        elif name == "hr":
            flush_pending()
            flowables.append(HRFlowable(width="100%", thickness=0.4,
                                         color=LINE, spaceBefore=8, spaceAfter=8))

    flush_pending()
    return flowables


# ============================================================================
# Page decorations
# ============================================================================
def make_watermark_drawer(lang: str, footer: bool = True):
    L = LABELS[lang]

    def draw(canv, doc):
        canv.saveState()
        page_w, page_h = A4

        # Subtle diagonal watermark — più piccolo e meno opaco del precedente
        canv.setFillColor(colors.HexColor("#000000"), alpha=0.04)
        canv.setFont(FONTS["bold"], 22)
        text = L["watermark"]
        text_w = canv.stringWidth(text, FONTS["bold"], 22)

        canv.translate(page_w / 2, page_h / 2)
        canv.rotate(28)
        step_x = text_w + 70
        step_y = 95
        n_x = int(page_w / step_x) + 3
        n_y = int(page_h / step_y) + 3
        for i in range(-n_y, n_y + 1):
            for j in range(-n_x, n_x + 1):
                canv.drawString(j * step_x - text_w / 2, i * step_y, text)
        canv.restoreState()

        if footer:
            canv.saveState()
            # Linea sopra il footer
            canv.setStrokeColor(LINE)
            canv.setLineWidth(0.4)
            canv.line(20 * mm, 14 * mm, page_w - 20 * mm, 14 * mm)
            # Footer text: left = title, right = page
            canv.setFillColor(INK_MUTE)
            canv.setFont(FONTS["base"], 7.5)
            canv.drawString(20 * mm, 9 * mm, f"{AUTHOR}  ·  {L['footer_rights']}")
            canv.drawRightString(page_w - 20 * mm, 9 * mm,
                                   f"{L['page']} {canv.getPageNumber()}")
            canv.restoreState()

    return draw


def make_cover_drawer(lang: str):
    L = LABELS[lang]

    def draw(canv, doc):
        canv.saveState()
        page_w, page_h = A4

        # Subtle watermark
        canv.setFillColor(colors.HexColor("#000000"), alpha=0.025)
        canv.setFont(FONTS["bold"], 22)
        text = L["watermark"]
        text_w = canv.stringWidth(text, FONTS["bold"], 22)
        canv.translate(page_w / 2, page_h / 2)
        canv.rotate(28)
        step_x = text_w + 70
        step_y = 95
        n_x = int(page_w / step_x) + 3
        n_y = int(page_h / step_y) + 3
        for i in range(-n_y, n_y + 1):
            for j in range(-n_x, n_x + 1):
                canv.drawString(j * step_x - text_w / 2, i * step_y, text)
        canv.restoreState()

        # Decorative top accent
        canv.saveState()
        canv.setFillColor(ACCENT)
        canv.rect(0, page_h - 6 * mm, page_w, 6 * mm, fill=1, stroke=0)
        # Decorative bottom accent
        canv.setFillColor(INK)
        canv.rect(0, 0, page_w, 6 * mm, fill=1, stroke=0)
        canv.restoreState()

    return draw


def make_part_drawer(lang: str):
    """Decoration for Part divider pages — keep watermark only, no footer."""
    L = LABELS[lang]

    def draw(canv, doc):
        canv.saveState()
        page_w, page_h = A4
        # Watermark
        canv.setFillColor(colors.HexColor("#000000"), alpha=0.035)
        canv.setFont(FONTS["bold"], 22)
        text = L["watermark"]
        text_w = canv.stringWidth(text, FONTS["bold"], 22)
        canv.translate(page_w / 2, page_h / 2)
        canv.rotate(28)
        step_x = text_w + 70
        step_y = 95
        for i in range(-6, 7):
            for j in range(-4, 5):
                canv.drawString(j * step_x - text_w / 2, i * step_y, text)
        canv.restoreState()

    return draw


# ============================================================================
# Document template (with PDF outline / bookmarks)
# ============================================================================
class GuideDoc(BaseDocTemplate):
    def __init__(self, filename, lang, **kw):
        BaseDocTemplate.__init__(self, filename, **kw)
        page_w, page_h = A4
        margin = 20 * mm

        cover_frame = Frame(margin, margin, page_w - 2 * margin, page_h - 2 * margin,
                             id="cover", showBoundary=0)
        body_frame = Frame(margin, 18 * mm, page_w - 2 * margin, page_h - margin - 18 * mm,
                            id="body", showBoundary=0)
        part_frame = Frame(margin, margin + 20 * mm, page_w - 2 * margin,
                            page_h - 2 * margin - 40 * mm,
                            id="part", showBoundary=0)

        self.addPageTemplates([
            PageTemplate(id="Cover", frames=cover_frame, onPage=make_cover_drawer(lang)),
            PageTemplate(id="Body", frames=body_frame, onPage=make_watermark_drawer(lang, footer=True)),
            PageTemplate(id="Part", frames=part_frame, onPage=make_part_drawer(lang)),
        ])

        self._bookmark_counter = 0

    def afterFlowable(self, flowable):
        """Intercept paragraphs marked with _bookmark and add to PDF outline."""
        bm = getattr(flowable, "_bookmark", None)
        if bm is None:
            return
        title, level = bm
        self._bookmark_counter += 1
        key = f"bm_{self._bookmark_counter}"
        # Anchor on the current page
        self.canv.bookmarkPage(key)
        # Add outline entry; closed=True keeps subtree collapsed by default
        self.canv.addOutlineEntry(title, key, level=level, closed=(level == 0 and self._bookmark_counter == 1) or False)


# ============================================================================
# Page builders
# ============================================================================
def build_cover(styles, lang):
    L = LABELS[lang]
    flowables = []
    flowables.append(Spacer(1, 70 * mm))
    flowables.append(Paragraph(L["edition"].upper(), styles["CoverEyebrow"]))
    flowables.append(Spacer(1, 6 * mm))
    title_html = L["title"].replace("\n", "<br/>")
    flowables.append(Paragraph(title_html, styles["CoverTitle"]))
    flowables.append(Spacer(1, 8 * mm))
    flowables.append(HRFlowable(width="80", thickness=2, color=ACCENT,
                                  hAlign="CENTER", spaceBefore=0, spaceAfter=14))
    flowables.append(Paragraph(L["subtitle"], styles["CoverSub"]))
    flowables.append(Spacer(1, 50 * mm))
    flowables.append(Paragraph(L["by"], styles["CoverAuthor"]))
    flowables.append(Spacer(1, 2 * mm))
    flowables.append(Paragraph(AUTHOR, styles["CoverAuthorName"]))
    return flowables


def build_copyright(styles, lang):
    L = LABELS[lang]
    f = []
    f.append(Spacer(1, 25 * mm))
    h_style = ParagraphStyle("CopyrightTitle", fontName=FONTS["bold"],
                              fontSize=20, leading=24, alignment=TA_LEFT,
                              spaceAfter=14, textColor=INK)
    p = Paragraph(L["copyright_title"], h_style)
    p._bookmark = (L["copyright_title"], 0)
    f.append(p)
    f.append(HRFlowable(width="100%", thickness=0.5, color=LINE, spaceBefore=0, spaceAfter=14))
    f.append(Paragraph(L["copyright_body"], styles["Body"]))
    return f


def build_toc(styles, lang, chapter_titles):
    L = LABELS[lang]
    f = []
    p = Paragraph(L["toc"], styles["TOCTitle"])
    p._bookmark = (L["toc"], 0)
    f.append(p)
    f.append(HRFlowable(width="60", thickness=2, color=ACCENT,
                          hAlign="LEFT", spaceBefore=0, spaceAfter=18))
    f.append(Spacer(1, 4 * mm))

    for part_idx in range(1, 7):
        part_label, part_title, _ = L["parts"][part_idx - 1]
        f.append(Paragraph(f"{part_label} — {part_title}", styles["TOCPart"]))
        for n in range(1, 17):
            if CHAPTER_TO_PART[n] != part_idx:
                continue
            title = chapter_titles.get(n, "")
            line = f'<font name="{FONTS["bold"]}" color="{ACCENT.hexval()}">{n:02d}</font>&nbsp;&nbsp;&nbsp;{title}'
            f.append(Paragraph(line, styles["TOCEntry"]))
    return f


def build_part_divider(styles, lang, part_idx):
    L = LABELS[lang]
    part_label, part_title, tagline = L["parts"][part_idx - 1]

    f = []
    f.append(Spacer(1, 30 * mm))
    f.append(Paragraph(L["part_intro"].upper(), styles["PartLabel"]))
    f.append(Paragraph(f"{part_idx:02d}", styles["PartNumber"]))
    f.append(Spacer(1, 6 * mm))
    f.append(HRFlowable(width="40", thickness=2, color=ACCENT,
                          hAlign="LEFT", spaceBefore=0, spaceAfter=10))
    title_para = Paragraph(part_title, styles["PartTitle"])
    title_para._bookmark = (f"{part_label} — {part_title}", 0)
    f.append(title_para)
    f.append(Paragraph(tagline, styles["PartTagline"]))
    return f


# ============================================================================
# Build
# ============================================================================
def get_chapter_path(slug: str, lang: str) -> Path:
    if lang == "it":
        return ROOT / f"{slug}.md"
    return ROOT / "en" / f"{slug}.md"


def extract_chapter_title(md_text: str, n: int, lang: str) -> str:
    """Extract title from first h1, stripping '1. ' prefix."""
    m = re.search(r"^# (.+)$", md_text, re.MULTILINE)
    if not m:
        return f"Chapter {n}"
    title = m.group(1).strip()
    title = re.sub(r"^\d+\.\s*", "", title)
    return title


def build_pdf(lang: str):
    out = ROOT / (f"Guida-Agenti-AI.pdf" if lang == "it" else "Guide-AI-Agents-EN.pdf")
    L = LABELS[lang]
    styles = make_styles()

    # Pre-load chapter titles for TOC
    chapter_titles = {}
    chapter_md_texts = {}
    for n, slug in enumerate(CHAPTERS_IT, start=1):
        path = get_chapter_path(slug, lang)
        if not path.exists():
            print(f"  [{lang}] WARN: missing {path.name}")
            continue
        text = path.read_text(encoding="utf-8")
        chapter_md_texts[n] = text
        chapter_titles[n] = extract_chapter_title(text, n, lang)

    doc = GuideDoc(
        str(out), lang=lang, pagesize=A4,
        title=("Guida agli Agenti AI" if lang == "it" else "Guide to AI Agents"),
        author=AUTHOR,
        subject=("Guida completa agli Agenti AI" if lang == "it" else "Complete guide to AI Agents"),
        creator=AUTHOR,
    )

    story = []

    # --- Cover (no trailing PageBreak, we control breaks here) ---
    story.append(NextPageTemplate("Cover"))
    story.extend(build_cover(styles, lang))

    # --- Switch to Body and emit copyright + TOC ---
    story.append(NextPageTemplate("Body"))
    story.append(PageBreak())  # → Body template
    story.extend(build_copyright(styles, lang))
    story.append(PageBreak())  # copyright → TOC, both on Body
    story.extend(build_toc(styles, lang, chapter_titles))

    # --- Chapters with part dividers ---
    last_part = 0
    for n, slug in enumerate(CHAPTERS_IT, start=1):
        if n not in chapter_md_texts:
            continue
        part_idx = CHAPTER_TO_PART[n]
        if part_idx != last_part:
            # Insert part divider
            story.append(NextPageTemplate("Part"))
            story.append(PageBreak())  # → Part template
            story.extend(build_part_divider(styles, lang, part_idx))
            story.append(NextPageTemplate("Body"))
            story.append(PageBreak())  # → Body template
            last_part = part_idx
        else:
            story.append(PageBreak())

        # Render chapter
        ch_flowables = parse_markdown_to_flowables(
            chapter_md_texts[n], styles, lang, chapter_n=n,
            chapter_title=chapter_titles[n],
        )
        story.extend(ch_flowables)

    print(f"  [{lang}] Building {out.name}…")
    doc.build(story)
    size_kb = out.stat().st_size / 1024
    print(f"  [{lang}] OK → {out.name} ({size_kb:.0f} KB)")


def main():
    args = sys.argv[1:]
    if not args or "all" in args:
        targets = ["it", "en"]
    else:
        targets = [a for a in args if a in ("it", "en")]
    for lang in targets:
        # Verifica esistenza file in corretta lingua
        first_chap = get_chapter_path(CHAPTERS_IT[0], lang)
        if not first_chap.exists():
            print(f"⚠️  Capitoli {lang.upper()} non trovati in {first_chap.parent}/. Skip.")
            continue
        build_pdf(lang)


if __name__ == "__main__":
    main()
