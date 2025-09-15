# Desktop App - Fake News Detector

This folder contains the desktop PyQt5 application for the Fake News Detector.

## Files
- `main.py` - Main application entry point
- `ui.py` - PyQt5 user interface implementation

## Running the Desktop App

1. Make sure you have PyQt5 installed:
```bash
pip install PyQt5
```

2. Run the desktop application:
```bash
cd desktop_app
python main.py
```

## Dependencies
The desktop app uses the following modules from the parent directory:
- `ocrExtractor.py` - OCR processing functionality
- `autoCleaner.py` - Text cleaning utilities

## Note
This desktop app provides a PyQt5 GUI interface for the same OCR functionality available in the web version (app.py).
