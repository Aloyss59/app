document.addEventListener('DOMContentLoaded', () => {
    const themeSelect = document.getElementById('color-page');
    const saveButton = document.getElementById('saveSettings');
    const localisation = document.getElementById('localisation');
    const friendRequests = document.getElementById('friends-requests');
    const notification = document.getElementById('notification');
    const doubleAuthentification = document.getElementById('authentification-double-facteur');
    const langue = document.getElementById('Langue');

    // Charger les réglages sauvegardés
    const savedTheme = localStorage.getItem('color-page');
    const savedLocalisation = localStorage.getItem('localisation');
    const savedFriendsRequests = localStorage.getItem('friends-requests');
    const savedNotification = localStorage.getItem('notification');
    const savedDoubleAuthentification = localStorage.getItem('authentification-double-facteur');
    const savedLangue = localStorage.getItem('Langue');

    if (savedTheme) {
        document.body.classList.toggle('dark', savedTheme === 'dark');
        themeSelect.value = savedTheme;
    }

    if (savedLocalisation !== null) {
        localisation.checked = savedLocalisation === 'true';
    }

    if (savedFriendsRequests !== null) {
        friendRequests.checked = savedFriendsRequests === 'true';
    }

    if (savedNotification !== null) {
        notification.checked = savedNotification === 'true';
    }

    if (savedDoubleAuthentification !== null) {
        doubleAuthentification.checked = savedDoubleAuthentification === 'true';
    }

    if (savedLangue) {
        langue.value = savedLangue;
    }

    // Appliquer les changements immédiatement quand l'utilisateur change les réglages
    themeSelect.addEventListener('change', () => {
        const selectedTheme = themeSelect.value;
        document.body.classList.toggle('dark', selectedTheme === 'dark');
    });

    localisation.addEventListener('change', () => {
    });

    friendRequests.addEventListener('change', () => {
    });

    notification.addEventListener('change', () => {
    });

    doubleAuthentification.addEventListener('change', () => {
    });

    langue.addEventListener('change', () => {
    });

    // Sauvegarder les réglages quand le bouton est cliqué
    saveButton.addEventListener('click', () => {
        const selectedTheme = themeSelect.value;
        const selectedLocalisation = localisation.checked;
        const selectedFriendRequests = friendRequests.checked;
        const selectedNotification = notification.checked;
        const selectedDoubleAuthentification = doubleAuthentification.checked;
        const selectedLangue = langue.value;

        localStorage.setItem('color-page', selectedTheme);
        localStorage.setItem('localisation', selectedLocalisation);
        localStorage.setItem('friends-requests', selectedFriendRequests);
        localStorage.setItem('notification', selectedNotification);
        localStorage.setItem('authentification-double-facteur', selectedDoubleAuthentification);
        localStorage.setItem('Langue', selectedLangue);

        document.body.classList.toggle('dark', selectedTheme === 'dark');

        document.body.classList.remove('fr', 'en', 'es', 'de');
        document.body.classList.add(selectedLangue);
    });
});