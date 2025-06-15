import subprocess
import os
from typing import Tuple, Optional

def process_webm_to_mp4(input_path: str) -> Tuple[bool, str]:
    """
    Convert WebM video to MP4 using FFmpeg command line directly
    Returns: (success, error_message or output_path)
    """
    try:
        # Validate input file
        if not os.path.exists(input_path):
            return False, f"Input file not found: {input_path}"
            
        output_path = input_path.replace('.webm', '_processed.mp4')
        
        # FFmpeg command with explicit codecs
        command = [
            'ffmpeg',
            '-y',  # Overwrite output file
            '-i', input_path,  # Input file
            '-c:v', 'libx264',  # Video codec
            '-c:a', 'aac',      # Audio codec
            '-strict', 'experimental',
            output_path
        ]

        # Run FFmpeg process
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False  # Don't raise exception on non-zero return
        )

        if result.returncode != 0:
            return False, f"FFmpeg error: {result.stderr}"

        if os.path.exists(output_path):
            return True, output_path
        else:
            return False, "Output file was not created"

    except Exception as e:
        return False, f"Processing error: {str(e)}"