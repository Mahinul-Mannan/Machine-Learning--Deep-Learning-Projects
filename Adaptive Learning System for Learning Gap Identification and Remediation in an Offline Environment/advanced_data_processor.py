import PyPDF2
import docx
import os
import re
from nltk.tokenize import sent_tokenize
import nltk

# Download NLTK data if not present
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class AdvancedDataProcessor:
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.txt']
    
    def extract_text_from_file(self, file_path):
        """Extract text from various file formats"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext == '.pdf':
                return self.extract_from_pdf(file_path)
            elif file_ext == '.docx':
                return self.extract_from_docx(file_path)
            elif file_ext == '.txt':
                return self.extract_from_txt(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}. Supported formats: {self.supported_formats}")
        except Exception as e:
            raise Exception(f"Error extracting text from {file_path}: {str(e)}")
    
    def extract_from_pdf(self, file_path):
        """Extract text from PDF files"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            raise Exception(f"PDF extraction error: {str(e)}")
    
    def extract_from_docx(self, file_path):
        """Extract text from DOCX files"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"DOCX extraction error: {str(e)}")
    
    def extract_from_txt(self, file_path):
        """Extract text from TXT files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except UnicodeDecodeError:
            # Try with different encoding if UTF-8 fails
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read().strip()
        except Exception as e:
            raise Exception(f"TXT extraction error: {str(e)}")
    
    def preprocess_text(self, text):
        """Clean and preprocess extracted text"""
        if not text:
            return ""
        
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\-\:\(\)]', '', text)
        
        # Ensure proper spacing after punctuation
        text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)
        
        return text.strip()
    
    def get_file_info(self, file_path):
        """Get basic information about the file"""
        if not os.path.exists(file_path):
            return None
        
        file_stats = os.stat(file_path)
        return {
            'filename': os.path.basename(file_path),
            'size_kb': file_stats.st_size / 1024,
            'file_type': os.path.splitext(file_path)[1].lower(),
            'modified_time': file_stats.st_mtime
        }
    
    def validate_file(self, file_path):
        """Validate if file is supported and accessible"""
        if not os.path.exists(file_path):
            return False, "File does not exist"
        
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in self.supported_formats:
            return False, f"Unsupported file format: {file_ext}"
        
        # Check file size (max 50MB)
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
        if file_size > 50:
            return False, "File size exceeds 50MB limit"
        
        return True, "File is valid"

def test_processor():
    """Test the data processor"""
    processor = AdvancedDataProcessor()
    
    # Create a sample text file for testing
    sample_text = """
    This is a sample text for testing the Advanced Data Processor.
    It contains multiple sentences to demonstrate text extraction capabilities.
    The processor should handle various file formats including PDF, DOCX, and TXT.
    """
    
    # Test text preprocessing
    processed = processor.preprocess_text(sample_text)
    print("Processed text sample:")
    print(processed[:100] + "...")
    
    print("\nSupported formats:", processor.supported_formats)

if __name__ == "__main__":
    test_processor()