document.addEventListener('DOMContentLoaded', function() {
    const video = document.getElementById('camera-stream');

    // Vérifiez si le navigateur prend en charge l'API de la caméra
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        console.log('getUserMedia est supporté par votre navigateur.');

        // Demande l'accès à la caméra
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(function(stream) {
                console.log('Accès à la caméra accordé.');
                // Affiche le flux de la caméra dans l'élément vidéo
                video.srcObject = stream;
            })
            .catch(function(error) {
                console.error('Erreur lors de l\'accès à la caméra :', error);
            });
    } else {
        console.error('Votre navigateur ne supporte pas l\'API getUserMedia');
    }
});

function handleReglageClick() {
    window.location.href = '/parametre';
}  

function redirectToChatPage() {
    window.location.href = "/";
}

function pagealbum() {
    window.location.href = "/album";
}

function pageamis() {
    window.location.href = "/amis";
}

function pagecam() {
    window.location.href = "/appareil-photo";
}

function pagechat() {
    window.location.href = "/";
}

function pageparametre() {
    window.location.href = "/discussion/parametre";
}
