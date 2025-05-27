import os
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import re
import json
from typing import Dict, List, Any, Tuple, Optional

class FileProcessor:
    """
    Service for processing uploaded files (PDF, images) and extracting content
    """
    
    def __init__(self, upload_folder: str):
        """
        Initialize the file processor
        
        Args:
            upload_folder: Path to the folder where uploaded files are stored
        """
        self.upload_folder = upload_folder
        
        # Ensure upload folder exists
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """
        Process a file and extract its content
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            Dictionary containing extracted content
        """
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension in ['.pdf']:
            return self._process_pdf(file_path)
        elif file_extension in ['.jpg', '.jpeg', '.png', '.bmp']:
            return self._process_image(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    def _process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Process a PDF file and extract text and images
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted text and images
        """
        result = {
            "title": os.path.basename(pdf_path),
            "pages": [],
            "images": []
        }
        
        # Open the PDF
        pdf_document = fitz.open(pdf_path)
        
        # Process each page
        for page_num, page in enumerate(pdf_document):
            # Extract text
            text = page.get_text()
            
            # Extract images
            image_list = self._extract_images_from_pdf_page(page, page_num)
            
            # Add page content to result
            result["pages"].append({
                "page_number": page_num + 1,
                "text": text,
                "images": [img["image_id"] for img in image_list]
            })
            
            # Add images to result
            result["images"].extend(image_list)
        
        # Close the PDF
        pdf_document.close()
        
        # Extract structure (headings, paragraphs, etc.)
        result["structure"] = self._extract_structure(result["pages"])
        
        return result
    
    def _extract_images_from_pdf_page(self, page, page_num: int) -> List[Dict[str, Any]]:
        """
        Extract images from a PDF page
        
        Args:
            page: PDF page object
            page_num: Page number
            
        Returns:
            List of dictionaries containing image information
        """
        image_list = []
        
        # Get images
        image_dict = page.get_images(full=True)
        
        for img_index, img_info in enumerate(image_dict):
            xref = img_info[0]
            base_image = page.parent.extract_image(xref)
            
            if base_image:
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                # Generate a unique image ID
                image_id = f"page_{page_num + 1}_img_{img_index + 1}.{image_ext}"
                image_path = os.path.join(self.upload_folder, image_id)
                
                # Save the image
                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)
                
                # Add image info to list
                image_list.append({
                    "image_id": image_id,
                    "path": image_path,
                    "page_number": page_num + 1,
                    "format": image_ext
                })
        
        return image_list
    
    def _process_image(self, image_path: str) -> Dict[str, Any]:
        """
        Process an image file and extract text using OCR
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing extracted text
        """
        result = {
            "title": os.path.basename(image_path),
            "pages": [],
            "images": []
        }
        
        # Open the image
        image = Image.open(image_path)
        
        # Extract text using OCR
        text = pytesseract.image_to_string(image, lang='ara+eng')
        
        # Add image to result
        image_id = os.path.basename(image_path)
        result["images"].append({
            "image_id": image_id,
            "path": image_path,
            "page_number": 1,
            "format": os.path.splitext(image_path)[1][1:]
        })
        
        # Add page content to result
        result["pages"].append({
            "page_number": 1,
            "text": text,
            "images": [image_id]
        })
        
        # Extract structure (headings, paragraphs, etc.)
        result["structure"] = self._extract_structure(result["pages"])
        
        return result
    
    def _extract_structure(self, pages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract structure (headings, paragraphs, etc.) from text
        
        Args:
            pages: List of pages with extracted text
            
        Returns:
            Dictionary containing structured content
        """
        structure = {
            "title": "",
            "headings": [],
            "paragraphs": [],
            "bullet_points": []
        }
        
        # Extract title (first line of first page)
        if pages and "text" in pages[0]:
            lines = pages[0]["text"].split('\n')
            if lines:
                structure["title"] = lines[0].strip()
        
        # Process all pages
        for page in pages:
            if "text" not in page:
                continue
                
            text = page["text"]
            lines = text.split('\n')
            
            current_paragraph = ""
            in_bullet_list = False
            bullet_list = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    # End of paragraph
                    if current_paragraph:
                        structure["paragraphs"].append(current_paragraph)
                        current_paragraph = ""
                    
                    # End of bullet list
                    if in_bullet_list and bullet_list:
                        structure["bullet_points"].append(bullet_list)
                        bullet_list = []
                        in_bullet_list = False
                    
                    continue
                
                # Check if line is a heading
                if self._is_heading(line):
                    # End current paragraph if any
                    if current_paragraph:
                        structure["paragraphs"].append(current_paragraph)
                        current_paragraph = ""
                    
                    # End bullet list if any
                    if in_bullet_list and bullet_list:
                        structure["bullet_points"].append(bullet_list)
                        bullet_list = []
                        in_bullet_list = False
                    
                    # Add heading
                    structure["headings"].append({
                        "text": line,
                        "level": self._get_heading_level(line)
                    })
                    continue
                
                # Check if line is a bullet point
                if self._is_bullet_point(line):
                    # End current paragraph if any
                    if current_paragraph:
                        structure["paragraphs"].append(current_paragraph)
                        current_paragraph = ""
                    
                    # Start or continue bullet list
                    in_bullet_list = True
                    bullet_list.append(line)
                    continue
                
                # Regular text - add to current paragraph
                if in_bullet_list:
                    # End bullet list
                    if bullet_list:
                        structure["bullet_points"].append(bullet_list)
                    bullet_list = []
                    in_bullet_list = False
                
                if current_paragraph:
                    current_paragraph += " " + line
                else:
                    current_paragraph = line
            
            # Add final paragraph if any
            if current_paragraph:
                structure["paragraphs"].append(current_paragraph)
            
            # Add final bullet list if any
            if in_bullet_list and bullet_list:
                structure["bullet_points"].append(bullet_list)
        
        return structure
    
    def _is_heading(self, line: str) -> bool:
        """
        Check if a line is a heading
        
        Args:
            line: Line of text
            
        Returns:
            True if the line is a heading, False otherwise
        """
        # Simple heuristic: headings are short, often end with a colon,
        # and may contain numbers at the beginning
        line = line.strip()
        
        # Check if line starts with a number followed by a dot or parenthesis
        if re.match(r'^\d+[\.\)]', line):
            return True
        
        # Check if line is short and ends with a colon
        if len(line) < 100 and line.endswith(':'):
            return True
        
        # Check if line is all uppercase and short
        if line.isupper() and len(line) < 50:
            return True
        
        return False
    
    def _get_heading_level(self, heading: str) -> int:
        """
        Get the level of a heading
        
        Args:
            heading: Heading text
            
        Returns:
            Heading level (1, 2, 3, etc.)
        """
        # Simple heuristic: level based on indentation, presence of numbers, etc.
        heading = heading.strip()
        
        # Check if heading starts with a number
        match = re.match(r'^(\d+)[\.\)]', heading)
        if match:
            # Level based on the number of digits
            num = match.group(1)
            if int(num) < 10:
                return 2
            else:
                return 3
        
        # Default to level 1 for short headings
        if len(heading) < 30:
            return 1
        
        return 2
    
    def _is_bullet_point(self, line: str) -> bool:
        """
        Check if a line is a bullet point
        
        Args:
            line: Line of text
            
        Returns:
            True if the line is a bullet point, False otherwise
        """
        line = line.strip()
        
        # Check if line starts with a bullet character
        if line.startswith('•') or line.startswith('-') or line.startswith('*'):
            return True
        
        # Check if line starts with a number or letter followed by a dot or parenthesis
        if re.match(r'^[a-zA-Z0-9][\.\)]', line):
            return True
        
        return False
