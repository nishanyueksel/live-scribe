import io
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

class PDFService:
    def __init__(self):
        self.styles = getSampleStyleSheet()

        # Custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.darkblue,
            alignment=1  # Center alignment
        )

        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkblue
        )

        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            leading=14
        )

        self.action_item_style = ParagraphStyle(
            'ActionItem',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            leftIndent=20,
            bulletIndent=10
        )

    def generate_transcript_pdf(self, transcript: str, summary: str, action_items: list) -> bytes:
        """Generate a PDF from transcript data and return as bytes"""
        buffer = io.BytesIO()

        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # Build content
        story = []

        # Title
        story.append(Paragraph("Meeting Transcript Report", self.title_style))
        story.append(Spacer(1, 20))

        # Date
        current_date = datetime.now().strftime("%B %d, %Y")
        story.append(Paragraph(f"Generated on: {current_date}", self.body_style))
        story.append(Spacer(1, 30))

        # Summary Section
        story.append(Paragraph("Executive Summary", self.heading_style))
        story.append(Paragraph(summary, self.body_style))
        story.append(Spacer(1, 20))

        # Action Items Section
        if action_items:
            story.append(Paragraph("Action Items", self.heading_style))
            for i, item in enumerate(action_items, 1):
                story.append(Paragraph(f"{i}. {item}", self.action_item_style))
            story.append(Spacer(1, 30))

        # Full Transcript Section
        story.append(Paragraph("Full Transcript", self.heading_style))

        # Split transcript into paragraphs for better formatting
        transcript_paragraphs = transcript.split('\n\n')
        for para in transcript_paragraphs:
            if para.strip():
                story.append(Paragraph(para.strip(), self.body_style))
                story.append(Spacer(1, 8))

        # Build PDF
        doc.build(story)

        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes