# 🔍 Fake News Detector

A comprehensive dual-mode application for analyzing news content through both image OCR and URL analysis, featuring advanced text processing and cleaning algorithms powered by Natural Language Processing (NLP) techniques.

## ✨ Features

### Dual-Mode Analysis
- **📷 Image Analysis**: Extract and process text from news screenshots using OCR
- **🔗 URL Analysis**: Scrape and analyze news articles directly from web URLs
- **🔄 Seamless Mode Switching**: Toggle between analysis types with a single click

### Advanced Text Processing
- **🤖 OCR Integration**: Tesseract-powered optical character recognition
- **🌐 Web Scraping**: BeautifulSoup-based intelligent content extraction
- **🧹 Text Cleaning Pipeline**: Multi-stage text preprocessing and tokenization
- **📊 Content Analysis**: Structured article parsing with metadata extraction

### User Interface Options
- **🌐 Web Application**: Modern Flask-based responsive web interface
- **💻 Desktop Application**: PyQt5 GUI for offline use with advanced features

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Tesseract OCR (for image text extraction)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd NLP-Project/SEMI-FINALS/FakeNews
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Tesseract OCR**
   - **Windows**: Download and install from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - **macOS**: `brew install tesseract`
   - **Linux**: `sudo apt-get install tesseract-ocr`

4. **Run the applications**
   ```bash
   # Web Application (Flask)
   python app.py
   # Access at http://localhost:5000
   
   # Desktop Application (PyQt5)
   cd desktop_app
   python main.py
   ```

## 📖 How to Use

### Web Application Mode
1. **Start the Flask server**: `python app.py`
2. **Open browser**: Navigate to `http://localhost:5000`
3. **Choose analysis mode**:
   - **📷 Image Analysis**: Click mode button, then upload/paste images
   - **🔗 URL Analysis**: Click mode button, enter news article URL
4. **View results**: Extracted text, cleaned content, and article metadata

### Desktop Application Mode
1. **Launch desktop app**: `cd desktop_app && python main.py`
2. **Upload images**: Use file dialog or paste from clipboard (Ctrl+V)
3. **Process text**: View both raw OCR output and cleaned text
4. **Advanced features**: Progress indicators, threading, error handling

### Image Analysis Features
- **Upload Methods**:
  - File selection via "Open File" button
  - Clipboard paste with Ctrl+V or "Paste Image" button
  - Drag & drop support (web version)
- **Processing**: Tesseract OCR → Text cleaning → Tokenization
- **Output**: Raw OCR text and cleaned/processed version

### URL Analysis Features
- **Input**: Enter any news article URL
- **Processing**: Web scraping → Content extraction → Text cleaning
- **Output**: Article title, content, source domain, and processed text
- **Supported Sites**: Most news websites with standard HTML structure

## 🔧 Technical Components

### 1. OCR Algorithm (Tesseract Integration)
- **Engine**: Tesseract OCR with pytesseract wrapper
- **Process**: Image → PIL processing → OCR extraction → Text output
- **Features**: Multi-format support (PNG, JPG, BMP, TIFF)
- **Performance**: Moderate speed, high accuracy with quality images

### 2. Web Scraping Algorithm
- **Library**: BeautifulSoup4 with requests
- **Strategy**: Multi-selector intelligent content extraction
- **Selectors**: `article`, `[role="main"]`, `.article-content`, `main`
- **Fallback**: Paragraph-based extraction with length filtering

### 3. Text Cleaning Pipeline (4-Stage Process)
- **Stage 1**: Emoji removal using Unicode range patterns
- **Stage 2**: Selective punctuation preservation
- **Stage 3**: Case normalization (lowercase conversion)
- **Stage 4**: Tokenization (whitespace-based word splitting)
- **Algorithm**: Custom implementation with regex patterns

### 4. URL Content Extraction (urlAnalyzer.py)
- **URLAnalyzer Class**: Dedicated module for URL processing
- **Title Extraction**: `<title>` → `og:title` → `<h1>` priority strategy
- **Content Strategy**: Semantic HTML → CSS selectors → paragraph fallback
- **Smart Selectors**: 7 different content selectors with priority order
- **Validation**: URL format checking, domain extraction
- **Error Handling**: Timeout management, request failures
- **Modular Design**: Reusable class with complete processing pipeline

## 📊 Understanding Results

### Dataset Structure
The scraped data is saved in `news_dataset.csv` with the following columns:
- **Title**: Article headline
- **Text**: Full article content
- **Label**: "Real" or "Fake" classification

### Text Cleaning Results
- **Input**: Raw, messy text with errors
- **Output**: Cleaned, normalized text
- **Process**: Character removal → Tokenization → Spell correction → Reconstruction

### OCR Results
- **Raw Output**: Direct OCR text extraction
- **Cleaned Output**: Processed and corrected text
- **Confidence**: Visual feedback on processing success

## 🛠️ Technical Stack

### Backend (Python 3.8+)
- **Web Framework**: Flask for HTTP endpoints and routing
- **OCR Engine**: pytesseract with Tesseract integration
- **Image Processing**: PIL/Pillow for image manipulation
- **Web Scraping**: requests + BeautifulSoup4 for content extraction
- **URL Analysis**: Dedicated urlAnalyzer.py module with URLAnalyzer class
- **Text Processing**: Custom NLP algorithms and regex patterns

### Frontend
- **Web UI**: HTML5, CSS3, JavaScript with responsive design
- **Desktop UI**: PyQt5 with threading and progress indicators
- **Styling**: Modern glassmorphism effects, dual-mode interface

### Core Libraries
- **Flask**: Web application framework
- **PyQt5**: Cross-platform GUI toolkit
- **BeautifulSoup4**: HTML/XML parsing
- **requests**: HTTP client for web scraping
- **urllib.parse**: URL validation and parsing
- **threading**: Asynchronous processing
- **PIL/Pillow**: Image processing and manipulation

## 📁 Project Structure

```
SEMI-FINALS/FakeNews/
├── 🌐 WEB APPLICATION
│   ├── app.py                  # Flask server & routing (109 lines)
│   ├── templates/
│   │   └── index.html         # Web interface template
│   └── static/
│       ├── style.css          # Web styling
│       └── script.js          # Frontend JavaScript
│
├── 💻 DESKTOP APPLICATION
│   └── desktop_app/
│       ├── main.py            # Desktop entry point
│       ├── ui.py              # PyQt5 interface
│       └── README.md          # Desktop documentation
│
├── 🧠 CORE MODULES
│   ├── ocrExtractor.py        # OCR processing engine
│   ├── urlAnalyzer.py         # URL analysis engine (6.9KB)
│   └── autoCleaner.py         # Text cleaning algorithms
│
├── 📊 LEGACY/UTILITIES
│   ├── newsScraper/           # Original scraping tools
│   ├── csv/                   # Dictionary files
│   │   ├── english_words.csv
│   │   ├── tagalog_words.csv
│   │   └── jejemon.csv
│   └── orcExe/                # Tesseract installer
│
└── 📋 CONFIGURATION
    └── requirements.txt       # Python dependencies
```

## 🔍 How It Works

### Image Analysis Pipeline
```
Image Upload → PIL Processing → Tesseract OCR → Text Cleaning → Tokenization → Display
```
1. **Image Input**: File upload, clipboard paste, or drag & drop
2. **OCR Processing**: Tesseract extracts text from image pixels
3. **Text Cleaning**: 4-stage cleaning pipeline removes noise
4. **Tokenization**: Split cleaned text into individual words
5. **Output Display**: Show both raw OCR and processed results

### URL Analysis Pipeline
```
URL Input → Validation → HTTP Request → HTML Parsing → Content Extraction → Text Cleaning → Display
```
1. **URL Validation**: Check format and accessibility
2. **Web Request**: Fetch HTML content with error handling
3. **Content Parsing**: Extract title and article content using multiple strategies
4. **Text Processing**: Apply same cleaning pipeline as OCR
5. **Result Display**: Show article metadata and processed content

### Text Cleaning Algorithm (4-Stage Process)
1. **Emoji Removal**: Unicode pattern matching for emoticons and symbols
2. **Punctuation Processing**: Selective removal while preserving sentence structure
3. **Case Normalization**: Convert to lowercase for consistency
4. **Tokenization**: Whitespace-based word splitting for analysis

## 🚨 Limitations

- **Language**: Optimized for English, Tagalog, and Jejemon text
- **Image Quality**: OCR accuracy depends on image clarity and text readability
- **Website Changes**: Scraping may break if target sites change structure
- **Rate Limiting**: Scraping speed limited to avoid overwhelming servers
- **Dictionary Dependency**: Text cleaning quality depends on dictionary completeness

## 🔧 Configuration

### Scraping Configuration
```python
# Modify these variables in scrapeNews.py
PAGES_PER_SITE = 10          # Pages to scrape per site
MAX_ARTICLES_PER_SITE = 2    # Max articles per site
BALANCE_DATASET = True       # Balance real vs fake news
```

### Application Configuration
```python
# Flask Web App (app.py)
app.run(debug=True, port=5000)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# URL Analyzer (urlAnalyzer.py)
url_analyzer = URLAnalyzer()
url_analyzer.timeout = 10  # Request timeout

# OCR Configuration (ocrExtractor.py)
DEFAULT_TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Text Cleaning (autoCleaner.py)
preserve_punctuation = ".,!?:;\"'"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with different text sources
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- BeautifulSoup4 for HTML parsing
- pytesseract for OCR functionality
- Pillow for image processing
- requests for web scraping
- All contributors and the open-source community

---

**⚠️ Disclaimer**: This tool is for educational and research purposes. Always verify information through multiple reliable sources before making important decisions. Respect website terms of service when scraping content.