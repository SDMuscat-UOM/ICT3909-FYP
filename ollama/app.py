import os
import subprocess
from flask import Flask, request, jsonify, render_template, url_for
from werkzeug.utils import secure_filename

# Roboflow inference client
from inference_sdk import InferenceHTTPClient
from PIL import Image, ImageDraw

# ——— Config ———
BASE_DIR       = os.path.abspath(os.path.dirname(__file__))
UPLOAD_SUBDIR  = 'uploads'
PROCESSED_SUB  = 'processed'
STATIC_DIR     = os.path.join(BASE_DIR, 'static')
UPLOAD_FOLDER  = os.path.join(STATIC_DIR, UPLOAD_SUBDIR)
PROCESSED_FOLDER = os.path.join(STATIC_DIR, PROCESSED_SUB)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Initialise Flask
app = Flask(__name__)
app.config['UPLOAD_FOLDER']   = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER']= PROCESSED_FOLDER

# Initialise Roboflow client
CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="8cAMfdvIvnyyRJECKL1W"
)

def allowed_file(filename):
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_input = request.json.get('prompt', '')
    response = query_ollama(user_input)
    return jsonify({'response': response})

@app.route('/upload-image', methods=['POST'])
def upload_image():
    # 1. Receive & save original
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    filename      = secure_filename(file.filename)
    orig_path     = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(orig_path)

    # 2. Send to CV model
    try:
        result = CLIENT.infer(orig_path, model_id="thesis-q2hxq/10")
    except Exception as e:
        return jsonify({'error': f'Inference failure: {e}'}), 500

    # 3. Annotate image with gender‑coloured boxes
    img = Image.open(orig_path)
    draw = ImageDraw.Draw(img)

    # Define the colour for each class
    colour_map = {
        'Male':    'blue',
        'Female':  'pink',
        'Unknown': 'green'
    }

    for pred in result.get('predictions', []):
        x, y = pred['x'], pred['y']
        w, h = pred['width'], pred['height']
        cls  = pred['class']
        conf = pred['confidence']

        # centre → corner
        left   = x - w/2
        top    = y - h/2
        right  = x + w/2
        bottom = y + h/2

        # pick the right colour (default to red if you get something unexpected)
        col = colour_map.get(cls, 'red')

        # draw the box and label
        draw.rectangle([left, top, right, bottom], outline=col, width=3)
        draw.text((left, top - 10), f"{cls} ({conf:.2f})", fill=col)

    # 4. Save processed
    proc_filename = f"proc_{filename}"
    proc_path     = os.path.join(app.config['PROCESSED_FOLDER'], proc_filename)
    img.save(proc_path)

    # 5. Return URL as before
    file_url = url_for('static',
                       filename=f'{PROCESSED_SUB}/{proc_filename}',
                       _external=False)
    return jsonify({'url': file_url})

def query_ollama(prompt):
    try:
        print(f"Sending prompt to Ollama: {prompt}")  # Debugging log
        result = subprocess.run(
            ['ollama', 'run', 'deepseek-r1:32b'],
            input=prompt, capture_output=True, text=True, shell=True
        )
        if result.stderr:
            print("Ollama stderr:", result.stderr)
        return result.stdout.strip()
    except Exception as e:
        print("Ollama error:", e)
        return f"Error querying Ollama: {e}"

if __name__ == '__main__':
    app.run(debug=True)