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
function getRandomColor() {
    var letters = '0123456789ABCDEF';
    var color = '#';
    for (var i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

window.onload = function() {
    var buttons = document.querySelectorAll('.bonhomme-button');
    buttons.forEach(function(button) {
        var color = getRandomColor();
        button.style.backgroundColor = color;
        button.style.position = 'relative'; // Assure que le pseudo-élément est positionné par rapport à ce conteneur
        var beforeElement = document.createElement('div'); // Crée un nouvel élément pour le pseudo-élément
        beforeElement.classList.add('bonhomme-button-before'); // Ajoute la classe au nouvel élément
        beforeElement.style.backgroundColor = color; // Applique la couleur aléatoire au pseudo-élément
        button.appendChild(beforeElement); // Ajoute le pseudo-élément en tant qu'enfant du bouton
    });
};
