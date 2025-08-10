# flask_mvp/app.py
from flask import Flask, request, jsonify
import os
import uuid
from werkzeug.utils import secure_filename
import io
from extractors import extract_text_from_file
import openai

app = Flask(__name__)
openai.api_key = os.environ.get('OPENAI_API_KEY')

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status':'ok'})

@app.route('/extract_text', methods=['POST'])
def extract_text():
    # Accepts multipart/form-data file under 'file'
    if 'file' not in request.files:
        return jsonify({'error':'no file'}), 400
    f = request.files['file']
    filename = secure_filename(f.filename)
    raw = f.read()
    text = extract_text_from_file(raw, filename)
    return jsonify({'text': text})

@app.route('/summarize', methods=['POST'])
def summarize():
    # Accepts either text in JSON {text: ...} or file under 'file'
    if request.is_json and 'text' in request.json:
        text = request.json['text']
    elif 'file' in request.files:
        f = request.files['file']
        filename = secure_filename(f.filename)
        raw = f.read()
        text = extract_text_from_file(raw, filename)
    else:
        return jsonify({'error':'no input'}), 400

    # Small safety: trim text length
    trimmed = text[:20000]

    prompt = (
        "You are a concise assistant. Produce a 3-6 bullet-point summary (each bullet 15-40 words) of the following document. Use plain language.\n\n" + trimmed
    )

    resp = openai.ChatCompletion.create(
        model='gpt-4o-mini', # or gpt-4o if available
        messages=[{'role':'user','content': prompt}],
        max_tokens=300,
        temperature=0.2,
    )

    summary = resp['choices'][0]['message']['content'].strip()
    return jsonify({'summary': summary})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('FLASK_PORT', 5001)), debug=True)