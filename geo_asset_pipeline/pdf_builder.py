# PDF Builder: ReportLab Search-Optimized Companion Geo-PDF Generator
import sys, os
from datetime import datetime

# Include vendor_py
vendor_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'vendor_py')
if os.path.exists(vendor_dir) and vendor_dir not in sys.path:
    sys.path.insert(0, vendor_dir)

from PIL import Image as PILImage
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, 
    Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.pdfgen import canvas
from .registry import DEFAULT_BUSINESS, get_city_geo

class NumberedCanvas(canvas.Canvas):
    """Custom canvas that tracks total pages and writes page numbers & running header/footer."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Running header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(0.6 * inch, 10.5 * inch, "Gold Standard Local SEO & GEO Engine — Official Regional Publication")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(0.6 * inch, 10.42 * inch, 7.9 * inch, 10.42 * inch)
        
        # Running footer (all pages)
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(7.9 * inch, 0.4 * inch, page_str)
        self.drawString(0.6 * inch, 0.4 * inch, "Gold Standard Local SEO • Folsom, CA • Verified Google Maps Entity")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(0.6 * inch, 0.52 * inch, 7.9 * inch, 0.52 * inch)
        self.restoreState()

def build_companion_pdf(
    output_pdf_path,
    variant_image_path,
    content_bundle,
    service,
    city_name,
    heading,
    business=None
):
    business = business or DEFAULT_BUSINESS
    geo = get_city_geo(city_name)
    article = content_bundle['article']
    keywords = content_bundle.get('keywords', [])
    keywords_str = ", ".join(keywords[:10])

    # Setup DocTemplate with Document Metadata
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=letter,
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
        title=article['article_title'],
        author=business['legal_name'],
        subject=f"{service} Google Maps 3-Pack Optimization in {geo['name']}, CA",
        keywords=keywords_str
    )

    # Styles
    styles = getSampleStyleSheet()
    
    brand_header_style = ParagraphStyle(
        'BrandHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#B45309"),
        textTransform='uppercase'
    )
    
    brand_sub_style = ParagraphStyle(
        'BrandSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#64748B")
    )
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=6
    )

    badge_style = ParagraphStyle(
        'Badge',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#1E293B")
    )
    
    meta_style = ParagraphStyle(
        'MetaLine',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#475569"),
        spaceAfter=12
    )
    
    body_style = ParagraphStyle(
        'BodyP',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=10
    )
    
    h2_style = ParagraphStyle(
        'SubHead',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    
    caption_style = ParagraphStyle(
        'ImageCaption',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#64748B"),
        alignment=1, # Center
        spaceBefore=4,
        spaceAfter=12
    )

    footer_title_style = ParagraphStyle(
        'FooterTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#0F172A")
    )
    
    footer_text_style = ParagraphStyle(
        'FooterText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#334155")
    )

    story = []

    # 1. Header Table (Brand Logo/Name + Authority Badge)
    header_data = [
        [
            Paragraph("<b>GOLD STANDARD LOCAL SEO & GEO ENGINE</b>", brand_header_style),
            Paragraph(f"<b>REGION:</b> {geo['name'].upper()}, CA • SACRAMENTO METRO", badge_style)
        ],
        [
            Paragraph(f"Official Entity Publication • CID: {business['cid']}", brand_sub_style),
            Paragraph(f"<b>GEO COORDINATES:</b> {geo['lat']}° N, {abs(geo['lon'])}° W", brand_sub_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[4.2 * inch, 2.6 * inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#F59E0B"), spaceBefore=2, spaceAfter=10))

    # 2. Document Title & Publication Subheader
    story.append(Paragraph(article['article_title'], title_style))
    focus_label = article.get('focus_type', 'Entity Authority Publication')
    date_str = datetime.now().strftime("%B %d, %Y")
    meta_line = f"<b>Format:</b> {focus_label} &nbsp;|&nbsp; <b>Territory:</b> {geo['name']}, {geo['county']} &nbsp;|&nbsp; <b>Published:</b> {date_str} &nbsp;|&nbsp; <b>Words:</b> {article['word_count']}"
    story.append(Paragraph(meta_line, meta_style))

    # 3. Insert Re-Cropped / Re-Scaled Variant Image (Distinct Perceptual Hash)
    if variant_image_path and os.path.exists(variant_image_path):
        try:
            with PILImage.open(variant_image_path) as p_img:
                img_w, img_h = p_img.size
                max_w = 5.8 * inch
                max_h = 2.4 * inch
                ratio = min(max_w / img_w, max_h / img_h)
                render_w = img_w * ratio
                render_h = img_h * ratio
            
            rl_img = RLImage(variant_image_path, width=render_w, height=render_h)
            story.append(rl_img)
            
            caption_text = (
                f"<b>Fig 1:</b> {heading} — Geotagged Authority Asset registered for {service} in {geo['name']}, CA.<br/>"
                f"GPS: {geo['lat']}, {geo['lon']} (Elev: {geo['altitude_m']}m) | "
                f"Google Maps Entity CID: <a href=\"{business['cid_url']}\" color=\"#2563EB\"><b>{business['cid']}</b></a>"
            )
            story.append(Paragraph(caption_text, caption_style))
        except Exception as e:
            # Continue if image rendering fails
            story.append(Spacer(1, 6))

    # 4. Article Body Flowables (Parsing Markdown Headings & Paragraphs)
    raw_markdown = article['content_markdown']
    paragraphs = raw_markdown.split('\n\n')

    for block in paragraphs:
        block = block.strip()
        if not block:
            continue
        
        if block.startswith('### '):
            clean_head = block.replace('### ', '').strip()
            story.append(Paragraph(clean_head, h2_style))
        elif block.startswith('## '):
            clean_head = block.replace('## ', '').strip()
            story.append(Paragraph(clean_head, h2_style))
        elif block.startswith('# '):
            clean_head = block.replace('# ', '').strip()
            story.append(Paragraph(clean_head, h2_style))
        else:
            # Replace inline markdown formatting for ReportLab:
            # Convert **text** to <b>text</b>
            # Convert [text](url) to <a href="url" color="#2563eb">text</a>
            formatted_text = block
            formatted_text = formatted_text.replace('&', '&amp;')
            # Re-escape entities carefully
            formatted_text = formatted_text.replace('&amp;nbsp;', '&nbsp;')
            
            import re
            # **bold**
            formatted_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', formatted_text)
            # *italic*
            formatted_text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', formatted_text)
            # [link](url)
            formatted_text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" color="#2563EB"><u>\1</u></a>', formatted_text)
            
            story.append(Paragraph(formatted_text, body_style))

    # 5. Callout & Conversion Box (Keep Together)
    story.append(Spacer(1, 8))
    box_content = [
        [
            Paragraph("<b>VERIFIED LOCAL GOOGLE BUSINESS ENTITY & INTAKE DESK</b>", footer_title_style)
        ],
        [
            Paragraph(
                f"<b>Business Entity:</b> {business['legal_name']} ({business['name']})<br/>"
                f"<b>Physical Address:</b> {business['street_address']}, {business['city']}, {business['state']} {business['postal_code']}<br/>"
                f"<b>Direct Phone:</b> <a href=\"tel:19162343457\" color=\"#2563EB\"><b>{business['display_phone']}</b></a> (24/7 Rapid Intake Desk)<br/>"
                f"<b>Regional Web Portal:</b> <a href=\"{business['website']}\" color=\"#2563EB\">{business['website']}</a><br/>"
                f"<b>Official Google Maps CID:</b> <a href=\"{business['cid_url']}\" color=\"#2563EB\"><b>View Verified Google 3-Pack Record ({business['cid']})</b></a>",
                footer_text_style
            )
        ]
    ]
    box_table = Table(box_content, colWidths=[6.8 * inch])
    box_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    
    story.append(KeepTogether([box_table]))

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    return output_pdf_path
