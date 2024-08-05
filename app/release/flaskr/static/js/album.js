// Sélectionnez les éléments
const calendar = document.querySelector('.container');
const showCalendarButton = document.createElement('button');
showCalendarButton.textContent = 'Afficher le calendrier';
showCalendarButton.classList.add('show-calendar-button');

// Ajoutez le bouton à la page
document.body.appendChild(showCalendarButton);

// Ajoutez un événement de clic sur le bouton
showCalendarButton.addEventListener('click', () => {
  // Faites apparaitre le calendrier
  calendar.style.opacity = 1;
});

// Fonctions pour les boutons de pied de page
function pageamis() {
  // Code pour la page des amis
  console.log('Page des amis');
}

function pagecam() {
  // Code pour la page de la caméra
  console.log('Page de la caméra');
}

function pagechat() {
  // Code pour la page du chat
  console.log('Page du chat');
}

function pagealbum() {
  // Code pour la page de l'album
  console.log('Page de l\'album');
}

function pageparametre() {
  // Code pour la page des paramètres
  console.log('Page des paramètres');
}

// Ajoutez des événements