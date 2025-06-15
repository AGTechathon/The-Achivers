import os
import cv2
import numpy as np
import subprocess
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from flask_cors import CORS
from werkzeug.utils import secure_filename
from query import chat
from astrapy import DataAPIClient
from groq import Groq
from video_processor import process_webm_to_mp4

# Load environment variables
load_dotenv()

# Flask app setup
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 
CORS(app)

# Constants

ALLOWED_EXTENSIONS = {'webm', 'mp4', 'avi', 'mov'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Groq setup
print("Groq Key Prefix:", os.environ.get("GROQ_API_KEY")[:8])
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Astra DB setup
db_client = DataAPIClient(os.getenv('ASTRADB_TOKEN'))
db = db_client.get_database_by_api_endpoint(
    "https://b4c89db4-bdf7-47fa-9b9c-ce5380480864-us-east-2.apps.astra.datastax.com"
)
collection = db['prime_medic_ai']

# Routes
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/chat')
def home():
    return render_template('index.html')

# Allowed file check
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Check if video has audio
def has_audio_stream(filepath):
    try:
        result = subprocess.run(
            ["ffprobe", "-i", filepath, "-show_streams", "-select_streams", "a", "-loglevel", "error"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return "codec_type=audio" in result.stdout
    except Exception as e:
        print("FFprobe error:", e)
        return False

# Upload video route
# ...existing code...
# ...existing code...

@app.route('/upload', methods=['POST'])
def upload_video():
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file uploaded', 'status': 'failed'}), 400

        video_file = request.files['video']
        if video_file.filename == '':
            return jsonify({'error': 'No selected file', 'status': 'failed'}), 400

        # Save original WebM file
        input_path = os.path.join(UPLOAD_FOLDER, "recorded-video.webm")
        video_file.save(input_path)
        print(f"Saved video file: {input_path}")
        success, result = process_webm_to_mp4(input_path)
        if not success:
            print(f"Video processing failed: {result}")
            return jsonify({'error': result, 'status': 'failed'}), 500

        # Continue with chat processing using the processed video
        if not has_audio_stream(result):
            print("No audio stream found. Using fallback audio.")
            return jsonify({
                'status': 'success',
                'audio_url': '/static/default_response.mp3'
            })

        audio = chat(result, [])
        if not audio:
            audio = '/static/response_audio.mp3'

        return jsonify({
            'status': 'success',
            'audio_url': audio
        })

    except Exception as e:
        print(f"Error in upload_video: {str(e)}")
        return jsonify({'status': 'error', 'error': str(e)}), 500
        # Process video using FFmpeg    
# ...existing code...
# Chat response generator
def get_response(message):
    user_vd = collection.find(
        sort={"$vectorize": message},
        limit=2,
        projection={"$vectorize": True},
        include_similarity=True,
    )

    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": message,
            },

            {
                'role': 'system',
                'content': f'''You are an AI Doctor (You have no name) Who is Fully Professional in Medicine field
                   and have the versatile knowledge of Medicine including the {user_vd},
                   Also You are a genuine and friendly concerning Doctor who takes a great care and comfort,
                   You will Provide the answers for the patients whatever they ask for and here is the user query {message},
                   Ignore the asterisk symbols and not allowed to greet the user as patient, address them with friendly titles
                   Now Answer it in the Concerning, Genuine and Jovial way of Speaking possible, You need to GIve the answer in the format given below
                   "The Name of the Problem,
                   The severity of the problem,
                   The precautions to be taken,
                   The medicines that need to be taken,
                   The need and type of doctor to be consulted.",
                   You have to give the response concise and strictly warning you don't use any kind of asterisks usage and pointing, numbering, the answer should only one be in
                '''
            }
        ],
        model="llama-3-70b-8192",  # ✅ Updated to supported model
    )
    return response.choices[0].message.content

# Chat route
@app.route('/send_message', methods=['POST'])
def send_message():
    try:
        if not request.is_json:
            print("Error: Request is not JSON")
            return jsonify({'error': 'Request must be JSON'}), 400

        data = request.get_json()
        if not data or 'message' not in data:
            print("Error: No message in request")
            return jsonify({'error': 'No message provided'}), 400

        message = data['message']
        print(f"Received message: {message}")

        # Get response from Groq
        response = get_response(message)
        print(f"Generated response: {response}")

        if not response:
            print("Error: Empty response generated")
            return jsonify({'error': 'Failed to generate response'}), 500

        return jsonify({'response': response})
    except Exception as e:
        print(f"Error in send_message: {str(e)}")
        return jsonify({'error': str(e)}), 500

def get_response(message):
    try:
        # Call Groq API
        chat_response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": message,
                }
            ],
            model="llama-3-70b-8192",
        )
        return chat_response.choices[0].message.content
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        return None
    
# Run app
def main():
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    main()

