import os
import base64
import io
from flask import Flask, render_template, request, jsonify
from PIL import Image
from ocrExtractor import OCRProcessor
from urlAnalyzer import URLAnalyzer

app = Flask(__name_s_)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize processors
ocr_processor = OCRProcessor()
url_analyzer = URLAnalyzer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_image', methods=['POST'])
def process_image():
    try:
        data = request.get_json()
        
        if 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Decode base64 image
        image_data = data['image']
        if image_data.startswith('data:image'):
            # Remove data URL prefix
            image_data = image_data.split(',')[1]
        
        # Convert base64 to PIL Image
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Process with OCR
        raw_text, cleaned_text = ocr_processor.process_image_sync(image)
        
        return jsonify({
            'success': True,
            'raw_text': raw_text,
            'cleaned_text': cleaned_text
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/process_file', methods=['POST'])
def process_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check if file is an image
        allowed_extensions = {'png', 'jpg', 'jpeg', 'bmp', 'tif', 'tiff'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'error': 'Invalid file type. Please upload an image file.'}), 400
        
        image = Image.open(file.stream)
        raw_text, cleaned_text = ocr_processor.process_image_sync(image)
        
        return jsonify({
            'success': True,
            'raw_text': raw_text,
            'cleaned_text': cleaned_text
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/process_url', methods=['POST'])
def process_url():
    try:
        data = request.get_json()
        
        if 'url' not in data:
            return jsonify({'error': 'No URL provided'}), 400
        
        url = data['url'].strip()
        if not url:
            return jsonify({'error': 'Empty URL provided'}), 400
        
        # Use URL analyzer for complete processing
        result = url_analyzer.analyze_url(url, log=True)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    app.run(debug=True, host='localhost', port=5000)
