

from flask import Flask, render_template, request, jsonify, url_for
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'webm', 'mp4', 'avi', 'mov', 'mkv'}
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_upload_folder():
    """Create uploads folder if it doesn't exist"""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        print(f"Created uploads folder: {UPLOAD_FOLDER}")

def get_next_video_number():
    """Get the next video number based on existing files"""
    if not os.path.exists(UPLOAD_FOLDER):
        return 1
    
    existing_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.startswith('video') and '.' in f]
    video_numbers = []
    
    for filename in existing_files:
        # Extract number from filename like "video1.webm", "video2.mp4", etc.
        try:
            base_name = filename.split('.')[0]  # Remove extension
            if base_name.startswith('video'):
                number_part = base_name.replace('video', '')
                if number_part.isdigit():
                    video_numbers.append(int(number_part))
        except:
            continue
    
    return max(video_numbers) + 1 if video_numbers else 1

def generate_meaningful_filename(original_filename):
    """Generate meaningful filename like video1.webm, video2.mp4, etc."""
    file_extension = os.path.splitext(original_filename)[1].lower()
    video_number = get_next_video_number()
    return f"video{video_number}{file_extension}"

@app.route('/')
def home():
    """Render the home page"""
    return render_template('home.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    """Handle video upload"""
    try:
        # Check if file is present in request
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        file = request.files['video']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file extension
        if not allowed_file(file.filename):
            return jsonify({'error': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        # Generate meaningful filename
        filename = generate_meaningful_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save the file
        file.save(file_path)
        
        # Get file info
        file_size = os.path.getsize(file_path)
        file_size_mb = round(file_size / (1024 * 1024), 2)
        
        print(f"Video uploaded successfully:")
        print(f"  - Original filename: {file.filename}")
        print(f"  - Saved as: {filename}")
        print(f"  - File size: {file_size_mb} MB")
        print(f"  - Saved to: {file_path}")
        
        return jsonify({
            'message': 'Video uploaded successfully',
            'filename': filename,
            'original_filename': file.filename,
            'file_size_mb': file_size_mb,
            'upload_time': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/uploads')
def list_uploads():
    """List all uploaded files"""
    try:
        files = []
        if os.path.exists(UPLOAD_FOLDER):
            for filename in os.listdir(UPLOAD_FOLDER):
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                if os.path.isfile(file_path):
                    file_size = os.path.getsize(file_path)
                    file_size_mb = round(file_size / (1024 * 1024), 2)
                    modification_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    files.append({
                        'filename': filename,
                        'file_size_mb': file_size_mb,
                        'upload_time': modification_time.isoformat()
                    })
        
        files.sort(key=lambda x: x['upload_time'], reverse=True)  # Sort by newest first
        
        return jsonify({
            'files': files,
            'total_files': len(files)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to list files: {str(e)}'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'upload_folder': UPLOAD_FOLDER,
        'upload_folder_exists': os.path.exists(UPLOAD_FOLDER),
        'allowed_extensions': list(ALLOWED_EXTENSIONS),
        'max_file_size_mb': app.config['MAX_CONTENT_LENGTH'] / (1024 * 1024)
    }), 200

@app.errorhandler(413)
def file_too_large(error):
    """Handle file too large error"""
    return jsonify({
        'error': 'File too large',
        'max_size_mb': app.config['MAX_CONTENT_LENGTH'] / (1024 * 1024)
    }), 413

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create upload folder on startup
    create_upload_folder()
    
    print("=" * 50)
    print("🎥 Webcam Video Capture Server")
    print("=" * 50)
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Allowed file types: {', '.join(ALLOWED_EXTENSIONS)}")
    print(f"Max file size: {app.config['MAX_CONTENT_LENGTH'] / (1024 * 1024):.0f} MB")
    print("=" * 50)
    print("Available endpoints:")
    print("  GET  /          - Home page")
    print("  POST /upload    - Upload video")
    print("  GET  /uploads   - List uploaded files")
    print("  GET  /health    - Health check")
    print("=" * 50)
    
    # Run the Flask application
    app.run(debug=True, host='0.0.0.0', port=5000)