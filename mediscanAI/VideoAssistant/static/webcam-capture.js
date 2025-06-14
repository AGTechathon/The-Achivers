document.addEventListener('DOMContentLoaded', () => {
   

 const webcamPreview = document.getElementById('webcamPreview');
    const startRecordingBtn = document.getElementById('startRecording');
    const stopRecordingBtn = document.getElementById('stopRecording');
    const uploadVideoBtn = document.getElementById('uploadVideo');
    const uploadedVideo = document.getElementById('uploadedVideo');
    const statusDiv = document.getElementById('status');

    let mediaRecorder;
    let recordedChunks = [];
    let stream;
    

    async function startWebcam() {
        // First, check browser compatibility
        if (!checkBrowserCompatibility()) {
            return;
        }

        try {
            // Specify detailed constraints
            const constraints = {
                video: {
                    width: { ideal: 640, max: 1280 },
                    height: { ideal: 480, max: 720 },
                    aspectRatio: { ideal: 1.333 },
                    facingMode: 'user' // Prefer front camera
                },
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            };

            stream = await navigator.mediaDevices.getUserMedia(constraints);
            
            // Additional checks after getting the stream
            if (!stream) {
                throw new Error('No stream obtained from getUserMedia');
            }

            // Set video source and play
            webcamPreview.srcObject = stream;
            
            // Ensure video plays
            webcamPreview.onloadedmetadata = (e) => {
                webcamPreview.play().catch(err => {
                    console.error('Error playing video:', err);
                    statusDiv.textContent = 'Could not play webcam stream: ' + err.message;
                });
            };

            // Enable recording button
            startRecordingBtn.disabled = false;
            statusDiv.textContent = 'Webcam access granted. Ready to record.';

        } catch (err) {
            console.error('Comprehensive webcam access error:', err);
            
            // Detailed error messaging
            let errorMessage = 'Error accessing webcam: ';
            switch(err.name) {
                case 'NotAllowedError':
                    errorMessage += 'Permission denied. Please grant webcam access.';
                    break;
                case 'NotFoundError':
                    errorMessage += 'No webcam found on this device.';
                    break;
                case 'NotReadableError':
                    errorMessage += 'Webcam is already in use or blocked.';
                    break;
                case 'OverconstrainedError':
                    errorMessage += 'No camera meets the specified constraints.';
                    break;
                default:
                    errorMessage += err.message || 'Unknown error occurred.';
            }

            statusDiv.textContent = errorMessage;
            startRecordingBtn.disabled = true;
        }
    }

    // Start video recording
    function startRecording() {
        if (!stream) {
            statusDiv.textContent = 'No webcam stream available. Please check webcam access.';
            return;
        }

        recordedChunks = [];
        
        try {
            // Use the most compatible MIME type
            const mimeTypes = [
                'video/webm;codecs=vp9,opus',
                'video/webm;codecs=vp8,vorbis',
                'video/webm'
            ];

            let supportedType = mimeTypes.find(type => 
                MediaRecorder.isTypeSupported(type)
            );

            if (!supportedType) {
                throw new Error('No supported video MIME type found');
            }

            mediaRecorder = new MediaRecorder(stream, {
                mimeType: supportedType
            });

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    recordedChunks.push(event.data);
                }
            };

            mediaRecorder.onstop = () => {
                const blob = new Blob(recordedChunks, { 
                    type: supportedType 
                });
                
                uploadVideoBtn.disabled = false;
                uploadedVideo.src = URL.createObjectURL(blob);
            };

            mediaRecorder.start();
            startRecordingBtn.disabled = true;
            stopRecordingBtn.disabled = false;
            statusDiv.textContent = 'Recording started...';

        } catch (err) {
            console.error('Recording start error:', err);
            statusDiv.textContent = 'Could not start recording: ' + err.message;
        }
  
    }

    function stopRecording() {
       if (!mediaRecorder) {
            statusDiv.textContent = 'No active recording to stop.';
            return;
        }

        try {
            mediaRecorder.stop();
            startRecordingBtn.disabled = false;
            stopRecordingBtn.disabled = true;
            statusDiv.textContent = 'Recording stopped.';
        } catch (err) {
            console.error('Recording stop error:', err);
            statusDiv.textContent = 'Error stopping recording: ' + err.message;
        }
    }

    async function uploadVideo() {
       
    }

    startRecordingBtn.addEventListener('click', startRecording);
    stopRecordingBtn.addEventListener('click', stopRecording);
    uploadVideoBtn.addEventListener('click', uploadVideo);

    startWebcam();
});