const video = document.getElementById('camera');
const canvas = document.getElementById('photo');
const snapButton = document.getElementById('snap');
const uploadButton = document.getElementById('upload');
const uploadedImage = document.getElementById('uploadedImage');

navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
        video.play();
    })
    .catch(err => {
        console.error("Error accessing the camera: ", err);
    });

snapButton.addEventListener('click', () => {
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    uploadButton.disabled = false; // Enable the upload button after taking a photo
});

uploadButton.addEventListener('click', () => {
    canvas.toBlob(blob => {
        const formData = new FormData();
        formData.append('image', blob, 'snapshot.png');

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.url) {
                uploadedImage.src = data.url;
                uploadedImage.style.display = 'block';
                uploadButton.disabled = true; // Disable the upload button after uploading
            } else {
                console.error('Upload failed:', data.error);
            }
        })
        .catch(error => {
            console.error('Error uploading image:', error);
        });
    });
});