document.addEventListener('DOMContentLoaded', () => {
    const themeSelect = document.getElementById('color-page');
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
        localStorage.setItem('color-page', selectedTheme);
    });

    localisation.addEventListener('change', () => {
        const selectedLocalisation = localisation.checked;
        localStorage.setItem('localisation', selectedLocalisation);
    });

    friendRequests.addEventListener('change', () => {
        const selectedFriendRequests = friendRequests.checked;
        localStorage.setItem('friends-requests', selectedFriendRequests);
    });

    notification.addEventListener('change', () => {
        const selectedNotification = notification.checked;
        localStorage.setItem('notification', selectedNotification);
    });

    doubleAuthentification.addEventListener('change', () => {
        const selectedDoubleAuthentification = doubleAuthentification.checked;
        localStorage.setItem('authentification-double-facteur', selectedDoubleAuthentification);
    });

    langue.addEventListener('change', () => {
        const selectedLangue = langue.value;
        localStorage.setItem('Langue', selectedLangue);
        document.body.classList.remove('fr', 'en', 'es', 'de');
        document.body.classList.add(selectedLangue);
    });
});