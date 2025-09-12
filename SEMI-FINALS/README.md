# 🔍 Fake News Detector

A powerful Python-based application that detects fake news using Natural Language Processing (NLP) and Machine Learning techniques. The system can analyze text from multiple sources including direct text input, web scraping, and images using OCR technology.

## ✨ Features

- **📝 Text Analysis**: Direct text input analysis with automatic cleaning
- **🌐 Web Scraping**: Automated collection of news articles from various sources
- **📷 Image Analysis**: Upload images with text and extract content using OCR
- **🧹 Text Cleaning**: Advanced text preprocessing with spell correction
- **📊 Dataset Management**: Automated dataset creation and balancing
- **🎨 Modern GUI**: Beautiful Tkinter interface with dark theme
- **🔧 Dual Processing**: Both automated scraping and manual text processing

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
   # For OCR text extraction GUI
   python ocrExtractor.py
   
   # For web scraping
   python scrapeNews.py
   
   # For text cleaning (command line)
   python autoCleaner.py "text to clean"
   ```

## 📖 How to Use

### 1. Web Scraping (`scrapeNews.py`)
- **Purpose**: Automatically collect news articles from various sources
- **Features**:
  - Scrapes from legitimate news sites (Rappler, Philstar, Reuters, AP, Al Jazeera)
  - Collects from known fake news sources (PeoplesVoice, NewsPunch)
  - Automatically labels articles as "Real" or "Fake"
  - Balances dataset to ensure equal representation
  - Saves data to `news_dataset.csv`

**Configuration**:
```python
SCRAPE_SITES = {
    "Rappler": True,
    "Philstar": True,
    "Reuters": True,
    "AP": True,
    "AlJazeera": True,
    "PeoplesVoice": True,
    "NewsPunch": True
}
```

### 2. OCR Text Extraction (`ocrExtractor.py`)
- **Purpose**: Extract text from images and clean it automatically
- **Features**:
  - Upload image files or paste from clipboard (Ctrl+V)
  - Uses Tesseract OCR for text extraction
  - Automatic text cleaning with spell correction
  - Supports multiple dictionaries (English, Tagalog, Jejemon)
  - Real-time processing with progress indicators

**Usage**:
- Click "Open File..." to select an image
- Use Ctrl+V to paste images from clipboard
- View both raw OCR output and cleaned text

### 3. Text Cleaning (`autoCleaner.py`)
- **Purpose**: Clean and normalize messy text using dictionary-based correction
- **Features**:
  - Removes special characters while preserving punctuation
  - Spell correction using Levenshtein distance algorithm
  - Supports multiple language dictionaries
  - Command-line interface for batch processing

**Usage**:
```bash
python autoCleaner.py "text with misspellings and special chars!"
```

## 🔧 Technical Components

### Web Scraping Engine
- **Speed**: ⚡ Fast with rate limiting
- **Reliability**: ✅ Robust error handling and retry logic
- **Scalability**: Handles multiple sites simultaneously
- **Features**:
  - BeautifulSoup for HTML parsing
  - Requests with session management
  - User agent rotation
  - Duplicate detection
  - Content validation

### OCR Processing
- **Speed**: 🐌 Moderate (depends on image complexity)
- **Accuracy**: High with good image quality
- **Languages**: Supports multiple languages
- **Features**:
  - Tesseract OCR integration
  - Image preprocessing
  - Multi-threaded processing
  - Real-time GUI updates

### Text Cleaning Pipeline
- **Speed**: ⚡ Very fast
- **Accuracy**: High with comprehensive dictionaries
- **Languages**: English, Tagalog, Jejemon support
- **Features**:
  - Levenshtein distance spell checking
  - Special character removal
  - Punctuation preservation
  - Token-based processing

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

- **Backend**: Python 3.8+
- **Web Scraping**: requests, BeautifulSoup4
- **OCR**: pytesseract, Pillow
- **GUI**: Tkinter
- **Text Processing**: Custom algorithms with Levenshtein distance
- **Data Storage**: CSV files
- **Image Processing**: PIL (Python Imaging Library)

## 📁 Project Structure

```
SEMI-FINALS/FakeNews/
├── scrapeNews.py           # Web scraping engine
├── ocrExtractor.py         # OCR GUI application
├── autoCleaner.py          # Text cleaning module
├── requirements.txt        # Python dependencies
├── news_dataset.csv        # Scraped dataset
├── csv/                   # Dictionary files
│   ├── english_words.csv
│   ├── tagalog_words.csv
│   └── jejemon.csv
└── orcExe/                # Tesseract installer
    └── tesseract-ocr-w64-setup-5.5.0.20241111.exe
```

## 🔍 How It Works

### Web Scraping Pipeline
1. **Configuration**: Define target sites and parameters
2. **Request Management**: Handle HTTP requests with retry logic
3. **Content Extraction**: Parse HTML and extract article content
4. **Data Validation**: Ensure content quality and uniqueness
5. **Dataset Creation**: Balance and save collected data

### OCR Processing Pipeline
1. **Image Input**: Load image from file or clipboard
2. **OCR Extraction**: Use Tesseract to extract text
3. **Text Cleaning**: Apply cleaning algorithms
4. **Result Display**: Show both raw and processed text

### Text Cleaning Pipeline
1. **Character Removal**: Remove non-printable characters
2. **Tokenization**: Split text into individual words
3. **Spell Checking**: Find best matches using Levenshtein distance
4. **Reconstruction**: Rebuild text with corrections
5. **Punctuation Fix**: Adjust spacing around punctuation

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

### OCR Configuration
```python
# Modify Tesseract path in ocrExtractor.py
DEFAULT_TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
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