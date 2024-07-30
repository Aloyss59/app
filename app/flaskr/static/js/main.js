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
    window.location.href = "/parametre";
}
// Ajoutez ici le code pour le toggle switch
document.getElementById('toggle-switch').addEventListener('change', function() {
    if (this.checked) {
        console.log('Le switch est activé');
        // Ajouter ici ce qui doit se passer quand le switch est activé
    } else {
        console.log('Le switch est désactivé');
        // Ajouter ici ce qui doit se passer quand le switch est désactivé
    }
});
