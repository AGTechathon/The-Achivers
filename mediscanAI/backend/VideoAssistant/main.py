from flask import Flask, render_template, request, jsonify
import os

from shinymedia import audio_spinner
from query import chat

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('video_recorder.html')

@app.route('/get-video', methods=['POST'])
def get_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file part'}), 400

    video_file = request.files['video']
    if video_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if video_file:
        video_path = os.path.join(UPLOAD_FOLDER, video_file.filename)
        video_file.save(video_path)
        return jsonify({'video_path': video_path}), 200
if __name__ == '__main__':
    app.run(debug=True)