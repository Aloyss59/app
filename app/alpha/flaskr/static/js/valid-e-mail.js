document.getElementById('emailForm').addEventListener('submit', function(event) {
    event.preventDefault();
    var email = document.getElementById('email').value;
    var message = document.getElementById('message');

    if (validateEmail(email)) {
        sendConfirmationEmail(email);
        message.textContent = 'Merci, vous êtes bien inscrit.';
        message.style.color = 'green';
    } else {
        message.textContent = 'Veuillez entrer une adresse e-mail valide.';
        message.style.color = 'red';
    }
});

function validateEmail(email) {
    // Simple regex for validating email format
    var emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailPattern.test(email);
}

function sendConfirmationEmail(email) {
    // Simuler l'envoi d'un e-mail de confirmation
    console.log('Confirmation envoyée à ' + email);
    // Vous pouvez utiliser une API d'envoi d'e-mails réelle ici.
}
