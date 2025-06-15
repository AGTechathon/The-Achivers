#!/usr/bin/env python3
"""
Simple setup script for the Webcam Video Recorder
This avoids the NumPy compilation issues you encountered.
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install required packages using pip"""
    print("🔧 Installing required Python packages...")
    
    # Basic packages that don't require compilation
    packages = [
        'Flask==2.3.3',
        'Werkzeug==2.3.7'
    ]
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    return True

def create_directory_structure():
    """Create the required directory structure"""
    print("📁 Creating directory structure...")
    
    directories = ['templates', 'uploads', 'static']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created/verified directory: {directory}")

def check_files():
    """Check if required files exist"""
    print("📋 Checking required files...")
    
    required_files = {
        'webcam.py': 'Backend server script',
        'templates/home.html': 'Frontend HTML file (should be in templates folder)'
    }
    
    missing_files = []
    
    for file_path, description in required_files.items():
        if os.path.exists(file_path):
            print(f"✅ Found: {file_path} ({description})")
        else:
            print(f"❌ Missing: {file_path} ({description})")
            missing_files.append(file_path)
    
    return missing_files

def main():
    """Main setup function"""
    print("🚀 Setting up Webcam Video Recorder...")
    print("=" * 50)
    
    # Install requirements
    if not install_requirements():
        print("❌ Installation failed. Please check the errors above.")
        return False
    
    # Create directories
    create_directory_structure()
    
    # Check files
    missing_files = check_files()
    
    print("\n" + "=" * 50)
    
    if missing_files:
        print("⚠️  Setup completed with warnings:")
        print("\nMissing files:")
        for file in missing_files:
            print(f"  - {file}")
        print("\nPlease ensure all files are in the correct locations before running the server.")
    else:
        print("✅ Setup completed successfully!")
    
    print("\n🎯 Next steps:")
    print("1. Make sure your home.html is in the templates/ folder")
    print("2. Run the server: python webcam.py")
    print("3. Open your browser to: http://localhost:5000")
    
    return True

if __name__ == '__main__':
    main()