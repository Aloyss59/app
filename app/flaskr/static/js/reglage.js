document.addEventListener('DOMContentLoaded', () => {
    const themeSelect = document.getElementById('color-page');
    const saveButton = document.getElementById('saveSettings');

    // Charger les réglages sauvegardés
    const savedTheme = localStorage.getItem('color-page');

    if (savedTheme) {
        document.body.classList.toggle('dark', savedTheme === 'dark');
        themeSelect.value = savedTheme;
    }

    // Sauvegarder les réglages quand le bouton est cliqué
    saveButton.addEventListener('click', () => {
        const selectedTheme = themeSelect.value;

        localStorage.setItem('color-page', selectedTheme);

        document.body.classList.toggle('dark', selectedTheme === 'dark');
    });

    // Appliquer les changements immédiatement quand l'utilisateur change les réglages
    themeSelect.addEventListener('change', () => {
        const selectedTheme = themeSelect.value;
        document.body.classList.toggle('dark', selectedTheme === 'dark');
    });
});