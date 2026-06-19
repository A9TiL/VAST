import fitz
import re

class PDFExtractor:
    """Extracts and cleans text from PDF documents."""
    
    @staticmethod
    def extract_text(file_path :str) ->str :
        """Reads a PDF and returns a clean, continuous string of text."""
        try:
            doc = fitz.open(file_path)
            full_text = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text("text")
                text = PDFExtractor._clean_pdf_text(text)
                full_text.append(text)
                
            return "\n\n".join(full_text)
        
        except Exception as e:
            raise RuntimeError(f"PuMuPDF failed : {str(e)}")
        
    @staticmethod
    def _clean_pdf_text(text:str) -> str :
        """ Removes common PDF formatting garbage. """
        text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
        text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
        text = re.sub(r' +', ' ', text)
        return text.strip()