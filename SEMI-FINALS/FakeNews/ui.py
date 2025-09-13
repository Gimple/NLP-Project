import os
import sys
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTextEdit, 
                             QFileDialog, QMessageBox, QScrollArea, QFrame,
                             QSplitter, QSizePolicy, QProgressBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPixmap, QImage, QFont, QPalette, QColor, QKeySequence, QMovie
from PIL import Image, ImageGrab
import pytesseract
from autoCleaner import clean_text


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


class OCRApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fake News Detector")
        self.setGeometry(100, 100, 1200, 900)  # Increased height for vertical layout
        
        # Set enhanced dark blue theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0c1220;
                color: #ffffff;
            }
            QWidget {
                background-color: #0c1220;
                color: #ffffff;
            }
            QTextEdit {
                background-color: #1a1f2e;
                color: #e2e8f0;
                border: 2px solid #2d3748;
                border-radius: 12px;
                padding: 15px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                selection-background-color: #3b82f6;
            }
            QTextEdit:focus {
                border-color: #60a5fa;
                background-color: #1a1f2e;
            }
            QLabel {
                color: #e2e8f0;
                font-weight: bold;
                font-size: 13px;
            }
            QScrollArea {
                border: 2px solid #2d3748;
                border-radius: 12px;
                background-color: #1a1f2e;
            }
            QFrame {
                background-color: #0c1220;
            }
            QSplitter::handle {
                background-color: #2d3748;
                border: 1px solid #4a5568;
            }
            QSplitter::handle:horizontal {
                width: 3px;
            }
            QSplitter::handle:vertical {
                height: 3px;
            }
            QStatusBar {
                background-color: #1a1f2e;
                color: #e2e8f0;
                border-top: 1px solid #2d3748;
            }
        """)
        
        self._setup_ui()
        self._setup_tesseract()
        
        # Internal image storage
        self._current_image = None
        
    def _setup_tesseract(self):
        DEFAULT_TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        if sys.platform.startswith("win"):
            if os.path.exists(DEFAULT_TESSERACT_PATH):
                pytesseract.pytesseract.tesseract_cmd = DEFAULT_TESSERACT_PATH
    
    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout - Vertical layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        
        # Create splitter for resizable panels (vertical)
        splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(splitter)
        
        # Top panel - Image area (landscape)
        image_panel = self._create_image_panel()
        splitter.addWidget(image_panel)
        
        # Bottom panel - Text area
        text_panel = self._create_text_panel()
        splitter.addWidget(text_panel)
        
        # Set splitter proportions (60% image, 40% text)
        splitter.setSizes([400, 300])
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
        
    def _create_image_panel(self):
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #0c1220;
                border: 2px solid #1a1f2e;
                border-radius: 15px;
                margin: 5px;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Image display area (landscape orientation)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(800, 300)  # Landscape: wider than tall
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #1a1f2e;
                border: 2px solid #2d3748;
                border-radius: 12px;
                color: #94a3b8;
                font-size: 14px;
            }
        """)
        self.image_label.setText("No image loaded\n\nPaste image (Ctrl+V) or\nOpen file to begin\n\n⚠️ IMPORTANT NOTICE:\n• Image must be clear and high quality\n• Text in the image must be clearly visible\n• Small or blurry images may not extract properly\n• Ensure good contrast between text and background")
        self.image_label.setWordWrap(True)
        
        # Scroll area for image
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.image_label)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumSize(820, 320)  # Landscape size
        layout.addWidget(scroll_area)
        
        # Button frame (moved below image) - Enhanced dark blue theme
        button_frame = QFrame()
        button_frame.setStyleSheet("""
            QFrame {
                background-color: #0c1220;
                border: 2px solid #1a1f2e;
                border-radius: 15px;
                padding: 15px;
            }
        """)
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(25)  # Increased spacing between buttons
        button_layout.setAlignment(Qt.AlignCenter)
        button_layout.setContentsMargins(25, 15, 25, 15)  # Add margins around button frame
        
        # Paste button (Yellow) - Increased width significantly
        self.paste_btn = QPushButton("Paste Image (Ctrl+V)")
        self.paste_btn.setMinimumWidth(200)  # Significantly increased width
        self.paste_btn.setMaximumWidth(220)
        self.paste_btn.setStyleSheet("""
            QPushButton {
                background-color: #fbbf24;
                color: #000000;
                border-color: #f59e0b;
                border-radius: 10px;
                padding: 12px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #f59e0b;
                border-color: #d97706;
            }
            QPushButton:pressed {
                background-color: #d97706;
            }
        """)
        self.paste_btn.clicked.connect(self.paste_image)
        
        # Open file button (Green) - with minimum and maximum width
        self.open_btn = QPushButton("Open File...")
        self.open_btn.setMinimumWidth(140)
        self.open_btn.setMaximumWidth(160)
        self.open_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: #ffffff;
                border-color: #059669;
                border-radius: 10px;
                padding: 12px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #059669;
                border-color: #047857;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
        """)
        self.open_btn.clicked.connect(self.open_file)
        
        # Clear button (Red) - with minimum and maximum width
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.setMinimumWidth(120)
        self.clear_btn.setMaximumWidth(140)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: #ffffff;
                border-color: #dc2626;
                border-radius: 10px;
                padding: 12px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #dc2626;
                border-color: #b91c1c;
            }
            QPushButton:pressed {
                background-color: #b91c1c;
            }
        """)
        self.clear_btn.clicked.connect(self.clear_all)
        
        button_layout.addWidget(self.paste_btn)
        button_layout.addWidget(self.open_btn)
        button_layout.addWidget(self.clear_btn)
        layout.addWidget(button_frame)
        
        # Loading indicator
        self.loading_label = QLabel()
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("""
            QLabel {
                background-color: #1a1f2e;
                border: 2px solid #2d3748;
                border-radius: 12px;
                color: #60a5fa;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
            }
        """)
        self.loading_label.setText("Processing...")
        self.loading_label.hide()  # Initially hidden
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #2d3748;
                border-radius: 12px;
                text-align: center;
                background-color: #1a1f2e;
                color: #e2e8f0;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #60a5fa;
                border-radius: 10px;
            }
        """)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.hide()  # Initially hidden
        
        layout.addWidget(self.loading_label)
        layout.addWidget(self.progress_bar)
        
        return panel
    
    def _create_text_panel(self):
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #0c1220;
                border: 2px solid #1a1f2e;
                border-radius: 15px;
                margin: 5px;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # OCR Output section - READ ONLY
        ocr_label = QLabel("OCR Output (Read Only):")
        ocr_label.setStyleSheet("""
            QLabel {
                color: #e2e8f0;
                font-weight: bold;
                font-size: 14px;
                padding: 5px;
            }
        """)
        layout.addWidget(ocr_label)
        
        self.ocr_text = QTextEdit()
        self.ocr_text.setReadOnly(True)  # Make OCR output completely read-only
        self.ocr_text.setMinimumHeight(150)
        self.ocr_text.setStyleSheet("""
            QTextEdit {
                background-color: #1a1f2e;
                color: #94a3b8;
                border: 2px solid #2d3748;
                border-radius: 12px;
                padding: 15px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
            QTextEdit:focus {
                border-color: #4a5568;
                background-color: #1a1f2e;
            }
        """)
        layout.addWidget(self.ocr_text)
        
        # Editable text section - FULLY EDITABLE
        edit_label = QLabel("Editable Text:")
        edit_label.setStyleSheet("""
            QLabel {
                color: #e2e8f0;
                font-weight: bold;
                font-size: 14px;
                padding: 5px;
            }
        """)
        layout.addWidget(edit_label)
        
        self.edit_text = QTextEdit()
        self.edit_text.setReadOnly(False)  # Ensure editable text is fully editable
        self.edit_text.setMinimumHeight(120)
        self.edit_text.setStyleSheet("""
            QTextEdit {
                background-color: #1a1f2e;
                color: #e2e8f0;
                border: 2px solid #2d3748;
                border-radius: 12px;
                padding: 15px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                selection-background-color: #3b82f6;
            }
            QTextEdit:focus {
                border-color: #60a5fa;
                background-color: #1a1f2e;
            }
        """)
        layout.addWidget(self.edit_text)
        
        return panel
    
    def paste_image(self):
        try:
            img = ImageGrab.grabclipboard()
        except Exception:
            img = None
            
        if img is None:
            QMessageBox.information(self, 'Paste', 
                                  'No image found in clipboard. Try using Windows+Shift+S to take a screenshot and then paste.')
            return
            
        if isinstance(img, list):
            # List of filenames
            try:
                img = Image.open(img[0])
            except Exception as e:
                QMessageBox.critical(self, 'Clipboard', f'Cannot open clipboard file: {e}')
                return
                
        self._set_image(img)
        self._run_ocr_async(img)
    
    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Open Image", 
            "", 
            "Image files (*.png *.jpg *.jpeg *.bmp *.tif *.tiff);;All files (*.*)"
        )
        
        if not file_path:
            return
            
        try:
            img = Image.open(file_path)
        except Exception as e:
            QMessageBox.critical(self, 'Open image', f'Failed to open image: {e}')
            return
            
        self._set_image(img)
        self._run_ocr_async(img)
    
    def clear_all(self):
        self.image_label.clear()
        self.image_label.setText("No image loaded\n\nPaste image (Ctrl+V) or\nOpen file to begin\n\n⚠️ IMPORTANT NOTICE:\n• Image must be clear and high quality\n• Text in the image must be clearly visible\n• Small or blurry images may not extract properly\n• Ensure good contrast between text and background")
        self.ocr_text.clear()
        self.edit_text.clear()
        self._current_image = None
        
        # Hide loading indicators
        self.loading_label.hide()
        self.progress_bar.hide()
        
        self.status_bar.showMessage("Ready - All content cleared")
    
    def _set_image(self, pil_image: Image.Image):
        self._current_image = pil_image.convert('RGB')
        
        # Convert PIL image to QPixmap
        rgb_image = self._current_image.convert('RGB')
        h, w, ch = rgb_image.height, rgb_image.width, len(rgb_image.getbands())
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.tobytes(), w, h, bytes_per_line, QImage.Format_RGB888)
        
        # Scale image to fit label while maintaining aspect ratio
        pixmap = QPixmap.fromImage(qt_image)
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(), 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        
        self.image_label.setPixmap(scaled_pixmap)
    
    def _run_ocr_async(self, pil_image: Image.Image):
        self.status_bar.showMessage("Processing...")
        self.ocr_text.clear()
        
        # Show loading indicators
        self.loading_label.show()
        self.progress_bar.show()
        
        # Create and start worker thread
        self.worker = OCRWorker(pil_image.copy())
        self.worker.finished.connect(self._on_ocr_finished)
        self.worker.error.connect(self._on_ocr_error)
        self.worker.progress.connect(self._on_ocr_progress)
        self.worker.start()
    
    def _on_ocr_progress(self, message):
        self.status_bar.showMessage(message)
        self.ocr_text.append(message)
    
    def _on_ocr_finished(self, raw_text, cleaned_text):
        # Hide loading indicators
        self.loading_label.hide()
        self.progress_bar.hide()
        
        self.ocr_text.clear()
        self.ocr_text.append("--- OCR Output ---")
        self.ocr_text.append(raw_text)
        self.ocr_text.append("\n--- Cleaned Output ---")
        self.ocr_text.append(cleaned_text)
        
        # Set cleaned text in editable area
        self.edit_text.clear()
        self.edit_text.setPlainText(cleaned_text)
        
        self.status_bar.showMessage("Done")
    
    def _on_ocr_error(self, error_message):
        # Hide loading indicators
        self.loading_label.hide()
        self.progress_bar.hide()
        
        QMessageBox.critical(self, 'OCR Error', error_message)
        self.status_bar.showMessage("OCR failed")
    
    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Paste):
            self.paste_image()
        else:
            super().keyPressEvent(event)

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = OCRApp()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()