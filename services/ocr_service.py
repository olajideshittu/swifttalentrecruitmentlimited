import pytesseract
from PIL import Image
import io

# Set the tesseract_cmd path for Windows (update this if your tesseract.exe is elsewhere)
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Olajide.shittu\venv\tesseract.exe'

class OCRService:
    def extract_text(self, image_file):
        # Read image file as PIL Image
        image = Image.open(image_file.stream)
        # Use pytesseract to extract text
        extracted_text = pytesseract.image_to_string(image)
        return extracted_text.strip()
