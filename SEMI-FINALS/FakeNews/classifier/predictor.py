import os
import sys
from PIL import Image
from typing import Tuple, Dict, Any, Union
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ocrExtractor import OCRProcessor
from urlAnalyzer import URLAnalyzer
from classifier.naiveBow import predict_news_with_logs
from classifier.boosting import compute_prior_boosts

class NewsPredictor:
    def __init__(self):
        self.ocr_processor = OCRProcessor()
        self.url_analyzer = URLAnalyzer()
        self._model_loaded = False
        self.class_counts = None
        self.word_counts_per_class = None
        self.vocab_size = None
    
    def _load_model(self):
        if not self._model_loaded:
            # Import and run the main function to get the trained model
            from classifier.naiveBow import main
            
            # This will train the model if not already trained
            self.class_counts, self.word_counts_per_class, self.vocab_size = main()
            self._model_loaded = True
    
    def predict_from_image(self, image_path: Union[str, Image.Image]) -> Dict[str, Any]:
        try:
            # Load image if path is provided
            if isinstance(image_path, str):
                image = Image.open(image_path)
            else:
                image = image_path
                
            # Process image with OCR
            raw_text, cleaned_text = self.ocr_processor.process_image_sync(image)
            
            # Load model if not already loaded
            self._load_model()
            
            # Get prediction
            prediction = predict_news_with_logs(
                cleaned_text,
                self.class_counts,
                self.word_counts_per_class,
                self.vocab_size
            )
            
            return {
                'success': True,
                'prediction': prediction,
                'raw_text': raw_text,
                'cleaned_text': cleaned_text,
                'source_type': 'image'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'source_type': 'image'
            }
    
    def predict_from_url(self, url: str) -> Dict[str, Any]:
        try:
            # Analyze URL and get cleaned text
            result = self.url_analyzer.analyze_url(url, log=False)
            cleaned_text = result['cleaned_text']
            source = result['article']['source']
            try:
                print(f"[Boost] URL source detected: {source}")
            except Exception:
                pass
            
            # Load model if not already loaded
            self._load_model()
            
            # Get prediction
            # Compute source-based prior boosts
            prior_boosts = compute_prior_boosts(source)
            try:
                print(f"[Boost] Computed prior boosts: {prior_boosts}")
            except Exception:
                pass
            prediction = predict_news_with_logs(
                cleaned_text,
                self.class_counts,
                self.word_counts_per_class,
                self.vocab_size,
                prior_boosts=prior_boosts
            )
            
            return {
                'success': True,
                'prediction': prediction,
                'title': result['article']['title'],
                'cleaned_text': cleaned_text,
                'source': result['article']['source'],
                'source_type': 'url',
                'url': url
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'source_type': 'url',
                'url': url
            }


def get_predictor():
    return NewsPredictor()

# === Manual Input ===
# if __name__ == "__main__":
#     predictor = get_predictor()
    
#     print("Testing URL prediction...")
#     url_result = predictor.predict_from_url("https://example.com/news-article")
#     print("URL Prediction Result:", url_result)

#     print("\nTesting image prediction...")
#     image_result = predictor.predict_from_image("path/to/your/image.png")
#     print("Image Prediction Result:", image_result)
