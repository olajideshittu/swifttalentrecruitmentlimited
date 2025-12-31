import pytesseract
from PIL import Image
import io
from typing import Any

# Set the tesseract_cmd path for Windows (update this if your tesseract.exe is elsewhere)
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Olajide.shittu\venv\tesseract.exe'

import logging

class OCRService:
    """
    Service for extracting text from images using OCR (pytesseract).
    """
    def extract_text(self, image_file: Any) -> str:
        """
        Extract text from an image file.

        Args:
            image_file (Any): The uploaded image file (with a .stream attribute).

        Returns:
            str: The extracted text from the image, or an empty string if extraction fails.
        """
        try:
            # Read image file as PIL Image
            image = Image.open(image_file.stream)
            # Use pytesseract to extract text
            extracted_text = pytesseract.image_to_string(image)
            logging.info("OCR extraction successful for image: %s", getattr(image_file, "filename", "unknown"))
            return extracted_text.strip()
        except Exception as e:
            logging.error("OCR extraction failed: %s", str(e))
            return ""
