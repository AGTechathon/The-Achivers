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
        
    }

    // Start video recording
    function startRecording() {
        
    }

    function stopRecording() {
       
    }

    async function uploadVideo() {
       
    }

    startRecordingBtn.addEventListener('click', startRecording);
    stopRecordingBtn.addEventListener('click', stopRecording);
    uploadVideoBtn.addEventListener('click', uploadVideo);

    startWebcam();
});