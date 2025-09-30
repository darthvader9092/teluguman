# app.py - Main Flask Application

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pytesseract
from PIL import Image
import io
import os
import requests
from urllib.parse import quote

app = Flask(__name__)
CORS(app)

# Configure Tesseract path (update this based on your system)
# For Windows: pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# For Linux/Mac: usually auto-detected

def translate_to_telugu(text):
    """
    Translate English text to Telugu using Google Translate API
    """
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=te&dt=t&q={quote(text)}"
        response = requests.get(url, timeout=10)
        result = response.json()
        
        # Extract translated text
        translated_text = ""
        for item in result[0]:
            if item[0]:
                translated_text += item[0]
        
        return translated_text
    except Exception as e:
        raise Exception(f"Translation failed: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'No image selected'}), 400
        
        # Read image
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Perform OCR
        extracted_text = pytesseract.image_to_string(image, lang='eng')
        
        if not extracted_text.strip():
            return jsonify({'error': 'No text found in image'}), 400
        
        # Translate to Telugu
        telugu_text = translate_to_telugu(extracted_text.strip())
        
        return jsonify({
            'success': True,
            'extracted_text': extracted_text,
            'telugu_text': telugu_text
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
