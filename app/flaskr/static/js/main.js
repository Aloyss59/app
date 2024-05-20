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
    window.location.href = "/discussion";
}
function pageparametre() {
    window.location.href = "/discussion/parametre";
}
function redirectToChatPage() {
    document.body.classList.add('slide-out');
    setTimeout(function() {
        window.location.href = "../templates/pagediscussion.html";
    }, 500); // Attendre la fin de l'animation (0.5s)
}
