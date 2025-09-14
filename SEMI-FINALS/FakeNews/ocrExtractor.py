import os
import sys
import threading
from PIL import Image, ImageGrab
import pytesseract
from autoCleaner import clean_text
from PyQt5.QtCore import QThread, pyqtSignal


class OCRWorker(QThread):
    finished = pyqtSignal(str, str)  # raw_text, cleaned_text
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    
    def __init__(self, image):
        super().__init__()
        self.image = image
        
    def run(self):
        try:
            self.progress.emit("Running OCR...")
            # Convert to RGB and run Tesseract
            raw_text = pytesseract.image_to_string(self.image)
            
            self.progress.emit("Cleaning text...")
            # Clean the text
            cleaned = clean_text(raw_text, log=True, logger=self.progress.emit)
            
            self.finished.emit(raw_text, cleaned)
            
        except Exception as e:
            self.error.emit(str(e))


class OCRProcessor:
    def __init__(self):
        self._setup_tesseract()
        
    def _setup_tesseract(self):
        DEFAULT_TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        if sys.platform.startswith("win"):
            if os.path.exists(DEFAULT_TESSERACT_PATH):
                pytesseract.pytesseract.tesseract_cmd = DEFAULT_TESSERACT_PATH
    
    def create_worker(self, image):
        return OCRWorker(image)
    
    def process_image_sync(self, image):
        try:
            # Convert to RGB and run Tesseract
            raw_text = pytesseract.image_to_string(image)
            
            # Clean the text
            cleaned = clean_text(raw_text, log=True)
            
            return raw_text, cleaned
            
        except Exception as e:
            raise Exception(f"OCR processing failed: {str(e)}")


# OCR logic module - import this from main.py or ui.py