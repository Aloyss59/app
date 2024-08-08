document.addEventListener('DOMContentLoaded', function () {
    const photo = document.querySelector('header img.ta-pp');
    const popup = document.getElementById('account-info-popup');
    const closePopup = document.getElementById('close-popup');
    
    photo.addEventListener('click', function () {
        popup.classList.add('visible');
        popup.classList.remove('hidden');
        document.body.classList.add('popup-open');
        fetch('/get_user_info')
        .then(response => response.json())
        .then(data => {
            document.getElementById("username").textContent = data.username
            document.getElementById("userNom").textContent = "Nom : " + data.nom;
            document.getElementById("userPrenom").textContent = "Prénom : " + data.prenom;
            popup.classList.remove("hidden");
        });
    });

    closePopup.addEventListener('click', function () {
        popup.classList.remove('visible');
        popup.classList.add('hidden');
        document.body.classList.remove('popup-open');
    });

    document.addEventListener('click', function (event) {
        if (!popup.contains(event.target) && event.target !== photo) {
            popup.classList.remove('visible');
            popup.classList.add('hidden');
            document.body.classList.remove('popup-open');
        }
    });
});
