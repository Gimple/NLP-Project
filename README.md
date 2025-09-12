# 🧠 NLP-Project

A comprehensive collection of Natural Language Processing (NLP) applications showcasing various techniques and implementations. This repository contains multiple projects ranging from chatbots and language translation to fake news detection and recipe recommendation systems.

## 📚 Project Overview

This repository contains three main phases of NLP projects:

- **🔰 PRELIM**: Basic NLP applications including chatbots and language translation
- **📊 MIDTERM**: Advanced NLP with recipe recommendation system using N-gram models
- **🎯 SEMI-FINALS**: Sophisticated fake news detection with web scraping and OCR

## ✨ Featured Projects

### 🔰 PRELIM Projects

#### 1. GenZ Bot (`PRELIM/Activity1/`)
- **Purpose**: A conversational chatbot that mimics Gen Z language patterns
- **Features**:
  - Context-aware responses using positive/negative response patterns
  - Gen Z slang and terminology integration
  - Interactive command-line interface
  - Personality-based conversation flow

#### 2. Jejemon Translator (`PRELIM/Activity2/`)
- **Purpose**: Translates between standard Filipino/Tagalog and Jejemon language
- **Features**:
  - Bidirectional translation (Standard ↔ Jejemon)
  - GUI interface with Tkinter
  - Comprehensive Jejemon dictionary
  - Real-time translation processing

### 📊 MIDTERM Project

#### 3. Meal & Match (`MIDTERM/Meal&Match/`)
- **Purpose**: Recipe recommendation system using N-gram language models
- **Features**:
  - N-gram model training on recipe data
  - Ingredient and cooking process prediction
  - Interactive GUI for recipe exploration
  - Corpus building from 13k+ recipes dataset
  - Smart ingredient substitution suggestions

### 🎯 SEMI-FINALS Project

#### 4. Fake News Detector (`SEMI-FINALS/FakeNews/`)
- **Purpose**: Comprehensive fake news detection system
- **Features**:
  - **📝 Text Analysis**: Direct text input analysis with automatic cleaning
  - **🌐 Web Scraping**: Automated collection of news articles from various sources
  - **📷 Image Analysis**: Upload images with text and extract content using OCR
  - **🧹 Text Cleaning**: Advanced text preprocessing with spell correction
  - **📊 Dataset Management**: Automated dataset creation and balancing
  - **🎨 Modern GUI**: Beautiful Tkinter interface with dark theme

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Tesseract OCR (for Fake News Detector image analysis)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd NLP-Project
   ```

2. **Install dependencies for each project**
   ```bash
   # For Fake News Detector
   cd SEMI-FINALS/FakeNews
   pip install -r requirements.txt
   
   # For other projects (install as needed)
   pip install tkinter pillow requests beautifulsoup4 pytesseract
   ```

3. **Install Tesseract OCR** (for Fake News Detector)
   - **Windows**: Download and install from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - **macOS**: `brew install tesseract`
   - **Linux**: `sudo apt-get install tesseract-ocr`

## 📖 How to Use Each Project

### 🔰 PRELIM Projects

#### GenZ Bot
```bash
cd PRELIM/Activity1
python main.py
```

#### Jejemon Translator
```bash
cd PRELIM/Activity2
python main.py
```

### 📊 MIDTERM Project

#### Meal & Match Recipe Recommender
```bash
cd MIDTERM/Meal&Match
python main.py
```

### 🎯 SEMI-FINALS Project

#### Fake News Detector
```bash
cd SEMI-FINALS/FakeNews

# For OCR text extraction GUI
python ocrExtractor.py

# For web scraping
python scrapeNews.py

# For text cleaning (command line)
python autoCleaner.py "text to clean"
```

## 🔧 Technical Components

### Language Processing Techniques

#### 1. **Chatbot Development**
- **Pattern Matching**: Response selection based on input patterns
- **Context Awareness**: Maintaining conversation flow
- **Personality Modeling**: Gen Z language characteristics

#### 2. **Language Translation**
- **Dictionary-Based Translation**: Bidirectional word mapping
- **Rule-Based Processing**: Jejemon language rules
- **GUI Integration**: Real-time translation interface

#### 3. **N-Gram Language Models**
- **Corpus Building**: Text preprocessing and tokenization
- **N-Gram Generation**: Statistical language modeling
- **Prediction Algorithms**: Next-word and ingredient prediction
- **Smoothing Techniques**: Handling unseen n-grams

#### 4. **Fake News Detection**
- **Web Scraping**: Automated data collection from news sources
- **OCR Processing**: Text extraction from images
- **Text Cleaning**: Advanced preprocessing with spell correction
- **Dataset Management**: Balanced training data creation

### Advanced Features

#### Text Processing Pipeline
- **Character Normalization**: Special character handling
- **Tokenization**: Word boundary detection
- **Spell Correction**: Levenshtein distance algorithms
- **Language Detection**: Multi-language support (English, Tagalog, Jejemon)

#### Web Scraping Engine
- **Rate Limiting**: Respectful data collection
- **Error Handling**: Robust retry mechanisms
- **Content Validation**: Quality assurance
- **Duplicate Detection**: Efficient data management

#### OCR Integration
- **Image Processing**: PIL-based image handling
- **Text Extraction**: Tesseract OCR integration
- **Multi-threading**: Non-blocking GUI updates
- **Real-time Processing**: Live text cleaning

## 📁 Project Structure

```
NLP-Project/
├── PRELIM/
│   ├── Activity1/GenZBot/          # Gen Z Chatbot
│   │   ├── genz.py                 # Main chatbot logic
│   │   ├── responses.py            # Response patterns
│   │   └── *.json                  # Response data
│   └── Activity2/TransJeje/         # Jejemon Translator
│       ├── core.py                 # Translation logic
│       ├── ui.py                   # GUI interface
│       └── jejemon.json            # Translation dictionary
├── MIDTERM/
│   └── Meal&Match/                 # Recipe Recommender
│       ├── core/
│       │   ├── corpora_builder.py   # Corpus creation
│       │   ├── ngram_model.py      # N-gram implementation
│       │   └── recommender.py      # Recommendation engine
│       ├── ui/ui.py                # GUI interface
│       └── 13k-recipes.csv         # Recipe dataset
├── SEMI-FINALS/
│   └── FakeNews/                   # Fake News Detector
│       ├── scrapeNews.py           # Web scraping engine
│       ├── ocrExtractor.py        # OCR GUI application
│       ├── autoCleaner.py         # Text cleaning module
│       ├── csv/                   # Dictionary files
│       └── news_dataset.csv       # Scraped dataset
├── LICENSE
└── README.md
```

## 🛠️ Technical Stack

### Core Technologies
- **Python 3.8+**: Primary programming language
- **Tkinter**: GUI framework for desktop applications
- **PIL/Pillow**: Image processing and manipulation
- **BeautifulSoup4**: HTML parsing and web scraping
- **requests**: HTTP client for web requests
- **pytesseract**: OCR text extraction
- **CSV**: Data storage and management

### NLP Libraries
- **Custom Algorithms**: Levenshtein distance, N-gram models
- **Text Processing**: Tokenization, normalization, cleaning
- **Language Models**: Statistical language modeling
- **Pattern Matching**: Rule-based text processing

## 🔍 How It Works

### Development Progression

#### **PRELIM Phase**: Foundation
- **Focus**: Basic NLP concepts and simple applications
- **Techniques**: Pattern matching, dictionary-based translation
- **Skills**: GUI development, file I/O, basic text processing

#### **MIDTERM Phase**: Intermediate
- **Focus**: Statistical language modeling and recommendation systems
- **Techniques**: N-gram models, corpus building, prediction algorithms
- **Skills**: Data preprocessing, statistical modeling, advanced GUI

#### **SEMI-FINALS Phase**: Advanced
- **Focus**: Real-world applications with multiple data sources
- **Techniques**: Web scraping, OCR, advanced text cleaning, dataset management
- **Skills**: Multi-threading, error handling, production-ready code

### Data Flow Architecture

```
Input Sources → Preprocessing → NLP Processing → Output Generation
     ↓              ↓              ↓              ↓
Text/Images → Cleaning/Normalization → Analysis → Results/Responses
     ↓              ↓              ↓              ↓
Web Content → Tokenization → Pattern Matching → GUI Display
     ↓              ↓              ↓              ↓
OCR Images → Spell Correction → Classification → File Storage
```

## 🚨 Limitations

- **Language Support**: Primarily optimized for English, Tagalog, and Jejemon
- **Data Quality**: Results depend on training data quality and completeness
- **Real-time Performance**: Some operations may be slower with large datasets
- **External Dependencies**: Requires Tesseract OCR for image processing
- **Website Changes**: Web scraping may break if target sites change structure

## 🔧 Configuration

### Project-Specific Settings

#### Fake News Detector
```python
# Web scraping configuration
PAGES_PER_SITE = 10
MAX_ARTICLES_PER_SITE = 2
BALANCE_DATASET = True

# OCR configuration
DEFAULT_TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

#### Recipe Recommender
```python
# N-gram model configuration
ngram_order = 4  # 4-gram model
corpus_files = ["ingredients_corpus.txt", "process_corpus.txt"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch for your improvements
3. Make your changes with proper documentation
4. Test thoroughly across different projects
5. Submit a pull request with detailed description

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- **BeautifulSoup4** for HTML parsing and web scraping
- **pytesseract** for OCR functionality
- **Pillow** for image processing capabilities
- **requests** for HTTP client functionality
- **Tkinter** for GUI framework
- All contributors and the open-source community

---

**⚠️ Disclaimer**: These tools are for educational and research purposes. Always verify information through multiple reliable sources before making important decisions. Respect website terms of service when scraping content.

**🎓 Educational Value**: This repository demonstrates the progression from basic NLP concepts to advanced real-world applications, making it an excellent resource for learning natural language processing techniques.
