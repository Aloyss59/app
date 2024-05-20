function handleReglageClick() {
    window.location.href = '../templates/reglage.html';
}  
function redirectToChatPage() {
    window.location.href = "../templates/discussion.html";
}
function pagealbum() {
    window.location.href = "../templates/album.html";
}
function pageamis() {
    window.location.href = "../templates/amis.html";
}
function pagecam() {
    window.location.href = "../templates/photo.html";
}
function pagechat() {
    window.location.href = "../templates/chat.html";
}
function pageparametre() {
    window.location.href = "../templates/parametres.html";
}
function redirectToChatPage() {
    document.body.classList.add('slide-out');
    setTimeout(function() {
        window.location.href = "../templates/pagediscussion.html";
    }, 500); // Attendre la fin de l'animation (0.5s)
}
