# 🔍 Fake News Detector

A web application that helps users analyze and detect potentially fake news articles through text analysis. The application supports both URL analysis and direct text/image input for flexible usage.

## ✨ Features

- **Dual-mode Analysis**
  - **URL Mode**: Analyze news articles by providing their web addresses
  - **Image Mode**: Upload images containing text for OCR processing and analysis

- **Text Processing**
  - Extracts and cleans text from various sources
  - Processes content to identify potential indicators of fake news
  - Provides confidence scores for analysis results

- **User Interface**
  - Clean, intuitive interface with dark theme
  - Real-time processing status updates
  - Detailed results display with confidence metrics
  - Mobile-responsive design

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser (Chrome, Firefox, Edge, or Safari)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/fake-news-detector.git
   cd fake-news-detector
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

## 🖥️ How to Use

### URL Analysis
1. Click on the "URL Mode" button
2. Enter the URL of the news article you want to analyze
3. Click "Analyze" and wait for the results

### Image Analysis
1. Click on the "Image Mode" button
2. Drag and drop an image or click to upload
3. The application will extract text using OCR and analyze it

## 📊 Understanding Results

- **Prediction**: Indicates whether the content is likely "REAL" or "FAKE"
- **Confidence Scores**: Shows the model's confidence level in its prediction
- **Processed Text**: Displays the cleaned and analyzed text

## 🛠️ Technical Stack

- **Backend**: Python, Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **Text Processing**: Custom text cleaning and analysis
- **Web Scraping**: For URL content extraction
- **OCR**: For extracting text from images

## 📁 Project Structure

```
fake-news-detector/
├── static/                  # Static files (CSS, JS, images)
│   ├── script.js            # Frontend JavaScript
│   └── style.css            # CSS styles
│
├── templates/               # HTML templates
│   └── index.html           # Main application interface
│
├── classifier/              # Classification models and utilities
│   ├── boosting.py          # Boosting algorithm implementation
│   ├── naiveBow.py          # Naive Bayes with Bag of Words
│   └── predictor.py         # Prediction interface
│
├── csv/                     # Dataset and language files
│   ├── english_words.csv    # English dictionary
│   ├── jejemon.csv          # Jejemon word list
│   ├── news_dataset.csv     # News dataset
│   └── tagalog_words.csv    # Tagalog word list
│
├── desktop_app/             # Desktop application version
│   ├── main.py             # Desktop app entry point
│   └── ui.py               # Desktop user interface
│
├── newsScraper/             # Web scraping components
│   ├── news_dataset.csv    # Scraped news dataset
│   └── scrapeNews.py       # News scraping implementation
│
├── orcExe/                  # OCR executable
│   └── tesseract-ocr-w64-setup-5.5.0.20241111.exe  # Tesseract OCR installer
│
├── app.py                   # Main Flask application
├── autoCleaner.py           # Text cleaning utilities
├── ocrExtractor.py          # OCR text extraction
├── requirements.txt         # Python dependencies
├── urlAnalyzer.py          # URL analysis module
└── README.md               # This file
```

## 🔍 How It Works

1. **Text Extraction**
   - For URLs: Fetches and extracts article content
   - For Images: Uses OCR to extract text

2. **Text Processing**
   - Cleans and normalizes the extracted text
   - Removes noise and irrelevant content

3. **Analysis**
   - Applies the classification model
   - Calculates confidence scores
   - Returns the prediction

## ⚠️ Limitations

- Accuracy depends on the quality of input text
- May not work well with very short texts
- Performance may vary with different languages
- Not suitable for analyzing images with poor quality or handwriting

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- Built as an educational project
- Special thanks to the open-source community for various libraries and tools

## ⚠️ Disclaimer

This application is for **educational purposes only**. The predictions made by this tool are not guaranteed to be accurate and should not be used as the sole basis for determining the veracity of news content. Always verify information from multiple reliable sources before making any conclusions.
