document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const snapButton = document.getElementById('snap');
    const uploadButton = document.getElementById('upload');
    const uploadedImage = document.getElementById('uploadedImage');
    const constraints = {
        video: true
    };

    // Accéder à la caméra
    navigator.mediaDevices.getUserMedia(constraints)
        .then((stream) => {
            video.srcObject = stream;
        })
        .catch((err) => {
            console.error('Error accessing media devices.', err);
        });

    // Prendre une photo
    snapButton.addEventListener('click', () => {
        const context = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        // Afficher le canvas
        canvas.style.display = 'block';
        uploadButton.disabled = false; // Activer le bouton d'upload
    });

    // Uploader la photo
    uploadButton.addEventListener('click', () => {
        const dataUrl = canvas.toDataURL('image/png');
        fetch('/upload', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ image: dataUrl })
        })
        .then(response => response.json())
        .then(data => {
            if (data.url) {
                uploadedImage.src = data.url;
                uploadedImage.style.display = 'block';
                canvas.style.display = 'none'; // Masquer le canvas
            } else {
                console.error('Error uploading image:', data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});