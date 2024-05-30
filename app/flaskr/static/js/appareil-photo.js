document.addEventListener('DOMContentLoaded', function() {
    const video = document.getElementById('video');

    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(function(stream) {
                video.srcObject = stream;
                video.play();
            })
            .catch(function(err) {
                console.error("Error accessing the camera: " + err);
            });
    } else {
        alert('getUserMedia is not supported in this browser.');
    }
});

function pageamis() {
    // Code pour changer de page vers la section amis
}

function pagecam() {
    // Code pour changer de page vers la section caméra
}

function pagechat() {
    // Code pour changer de page vers la section chat
}

function pagealbum() {
    // Code pour changer de page vers la section album
}

function pageparametre() {
    // Code pour changer de page vers la s
}