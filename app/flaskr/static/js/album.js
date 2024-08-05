// Select the elements
const calendar = document.querySelector('.calendar');
const weeks = document.querySelectorAll('.weeks span');
const showCalendarButton = document.querySelector('.show-calendar-button');

// Add event listeners to the span elements
weeks.forEach((week) => {
  week.addEventListener('click', () => {
    // Fade out the calendar
    calendar.classList.add('fade-out');
    setTimeout(() => {
      // Hide the calendar
      calendar.style.display = 'none';
      // Show the button
      showCalendarButton.style.display = 'block';
      showCalendarButton.classList.add('fade-in');
    }, 500);
  });
});

// Add an event listener to the button
showCalendarButton.addEventListener('click', () => {
  // Fade out the button
  showCalendarButton.classList.add('fade-out');
  setTimeout(() => {
    // Hide the button
    showCalendarButton.style.display = 'none';
    // Show the calendar
    calendar.style.display = 'block';
    calendar.classList.add('fade-in');
  }, 500);
});

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