from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import inch
from PIL import Image
import os

class PDFReportGenerator:
    def __init__(self, output_filename, report_title=None):
        """
        Initialize the PDF generator with an output filename.
        
        Args:
            output_filename (str): Name of the output PDF file
            report_title (str, optional): Title for the report cover page
        """
        self.c = canvas.Canvas(output_filename, pagesize=letter)
        self.width, self.height = letter
        self.y_position = self.height - 50
        self.current_page = 1
        self.sections = []  # Store section titles and their starting pages
        self.report_title = report_title
        
    def add_title_page(self):
        """Create a title page for the report."""
        if not self.report_title:
            return
            
        self.c.setFont("Helvetica-Bold", 24)
        # Center the title
        title_width = self.c.stringWidth(self.report_title, "Helvetica-Bold", 24)
        x_position = (self.width - title_width) / 2
        self.c.drawString(x_position, self.height - 200, self.report_title)
        
        # Add date
        from datetime import datetime
        date_str = datetime.now().strftime("%B %d, %Y")
        self.c.setFont("Helvetica", 12)
        date_width = self.c.stringWidth(date_str, "Helvetica", 12)
        x_position = (self.width - date_width) / 2
        self.c.drawString(x_position, self.height - 250, date_str)
        
        self.c.showPage()
        self.current_page += 1
        
    def add_table_of_contents(self):
        """Create a table of contents page."""
        self.c.setFont("Helvetica-Bold", 16)
        self.c.drawString(50, self.height - 50, "Table of Contents")
        
        self.c.setFont("Helvetica", 12)
        y_position = self.height - 100
        
        for section_title, page_num in self.sections:
            self.c.drawString(50, y_position, section_title)
            self.c.drawString(500, y_position, str(page_num))
            
            # Add dotted line between title and page number
            dots = ". " * 40
            self.c.setFont("Helvetica", 8)
            self.c.drawString(200, y_position, dots)
            self.c.setFont("Helvetica", 12)
            
            y_position -= 20
            
        self.c.showPage()
        self.current_page += 1
        
    def add_page_number(self):
        """Add page number to the current page."""
        self.c.setFont("Helvetica", 10)
        page_text = f"Page {self.current_page}"
        self.c.drawString(self.width - 72, 30, page_text)
        
    def add_section(self, title, image_configs):
        """
        Add a new section with a title and images to the PDF.
        
        Args:
            title (str): Section title
            image_configs (list): List of image configurations
        """
        # Store section information for table of contents
        self.sections.append((title, self.current_page))
        
        # Add title
        if self.y_position < 100:
            self.c.showPage()
            self.current_page += 1
            self.y_position = self.height - 50
            
        self.c.setFont("Helvetica-Bold", 16)
        # Calculate title width and center position
        title_width = self.c.stringWidth(title, "Helvetica-Bold", 16)
        x_position = (self.width - title_width) / 2
        self.c.drawString(x_position, self.y_position, title)
        self.y_position -= 30
        
        # Process image configurations
        current_row = []
        
        for config in image_configs:
            if isinstance(config, str):
                self._process_row([config])
            elif isinstance(config, dict):
                current_row.append(config['path'])
                if len(current_row) == config['row_images']:
                    self._process_row(current_row)
                    current_row = []
            elif isinstance(config, list):
                self._process_row(config)
            
        if current_row:
            self._process_row(current_row)
            
        self.y_position -= 20
        
    def _process_row(self, image_paths):
        """Process and draw a row of images."""
        if not image_paths:
            return
            
        available_width = self.width - 100
        image_width = (available_width - (20 * (len(image_paths) - 1))) / len(image_paths)
        
        max_height = 0
        image_heights = []
        for img_path in image_paths:
            img = Image.open(img_path)
            img_w, img_h = img.size
            aspect_ratio = img_h / img_w
            image_height = image_width * aspect_ratio
            image_heights.append(image_height)
            max_height = max(max_height, image_height)
            
        if self.y_position - max_height < 50:
            self.add_page_number()  # Add page number before new page
            self.c.showPage()
            self.current_page += 1
            self.y_position = self.height - 50
            
        current_x = 50
        for img_path, image_height in zip(image_paths, image_heights):
            self.c.drawImage(
                ImageReader(img_path),
                current_x,
                self.y_position - image_height,
                width=image_width,
                height=image_height
            )
            current_x += image_width + 20
            
        self.y_position -= (max_height + 30)
    
    def save(self):
        """Save and close the PDF document."""
        self.add_page_number()  # Add page number to last page
        self.c.save()

def create_report(output_filename, sections, report_title=None):
    """
    Create a PDF report from multiple sections.
    
    Args:
        output_filename (str): Name of the output PDF file
        sections (list): List of dictionaries containing section information
        report_title (str, optional): Title for the report cover page
    """
    pdf = PDFReportGenerator(output_filename, report_title)
    
    if report_title:
        pdf.add_title_page()
    
    # First pass to collect section information
    for section in sections:
        pdf.add_section(section['title'], section['image_configs'])
        
    # Create a new PDF with table of contents
    final_pdf = PDFReportGenerator(output_filename, report_title)
    if report_title:
        final_pdf.sections = pdf.sections
        final_pdf.add_title_page()
        final_pdf.add_table_of_contents()
    
    # Add all sections again
    for section in sections:
        final_pdf.add_section(section['title'], section['image_configs'])
    
    final_pdf.save()