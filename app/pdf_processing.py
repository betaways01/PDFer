import fitz  # PyMuPDF
import pdfplumber
import pytesseract
from PIL import Image
import io
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_pdf_to_text(pdf_path):
    """
    Extracts plain text and tables from a PDF using PyMuPDF and pdfplumber.
    Args:
        pdf_path (str): The path to the PDF file.
    Returns:
        str: The extracted text.
    """
    try:
        # Attempt text extraction with PyMuPDF
        text = ""
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
        
        if not text.strip():  # If PyMuPDF fails to extract text, fall back to pdfplumber
            logger.warning("PyMuPDF extraction yielded empty text, switching to pdfplumber.")
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text()
        
        if not text.strip():
            raise ValueError("Failed to extract text from PDF.")
        
        return text
    
    except Exception as e:
        logger.error(f"Error extracting text from PDF {pdf_path}: {e}")
        return ""  # Return an empty string or raise an error based on your requirement

def extract_images_from_pdf(pdf_path):
    """
    Extracts text from images embedded in a PDF using OCR.
    Args:
        pdf_path (str): The path to the PDF file.
    Returns:
        str: The text extracted from images.
    """
    text_from_images = ""
    
    try:
        with fitz.open(pdf_path) as doc:
            for page_num, page in enumerate(doc):
                images = page.get_images(full=True)
                for img_index, img in enumerate(images):
                    try:
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        image = Image.open(io.BytesIO(image_bytes))
                        ocr_text = pytesseract.image_to_string(image)
                        text_from_images += ocr_text
                        logger.info(f"OCR extracted text from image {img_index + 1} on page {page_num + 1}")
                    except Exception as img_err:
                        logger.error(f"Failed to extract text from image {img_index + 1} on page {page_num + 1}: {img_err}")
    
    except Exception as e:
        logger.error(f"Error extracting images from PDF {pdf_path}: {e}")
        return ""
    
    return text_from_images

def extract_text_and_images(pdf_path):
    try:
        logger.info(f"Processing PDF: {pdf_path}")
        text = convert_pdf_to_text(pdf_path)
        text_from_images = extract_images_from_pdf(pdf_path)
        
        # Mark OCR text with a special delimiter
        if text_from_images:
            text_from_images = "\n".join([f"[OCR]{line}" for line in text_from_images.splitlines()])
        
        combined_text = text + "\n\n" + text_from_images
        return combined_text
    
    except Exception as e:
        logger.error(f"Failed to process PDF {pdf_path}: {e}")
        return ""

if __name__ == "__main__":
    pdf_path = "path_to_your_pdf.pdf"
    extracted_text = extract_text_and_images(pdf_path)
    if extracted_text:
        logger.info("Extraction completed successfully.")
    else:
        logger.warning("Extraction failed or yielded no text.")