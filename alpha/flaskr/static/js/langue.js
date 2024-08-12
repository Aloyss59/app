const languageSelect = document.getElementById('Langue');

const translations = {
  'fr': {
    'applicationParametre': 'Paramètres de l\'application',
    'apparence': 'Apparence',
    // ... autres éléments de texte ...
  },
  'en': {
    'applicationParametre': 'Application Settings',
    'apparence': 'Appearance',
    // ... autres éléments de texte ...
  },
  'es': {
    'applicationParametre': 'Configuración de la aplicación',
    'apparence': 'Apariencia',
    // ... autres éléments de texte ...
  },
  'de': {
    'applicationParametre': 'Anwendungs-Einstellungen',
    'apparence': 'Erscheinungsbild',
    // ... autres éléments de texte ...
  }
};

function updateTranslations(language) {
  const elementsToTranslate = document.querySelectorAll('[data-translate]');
  
  elementsToTranslate.forEach((element) => {
    const key = element.getAttribute('data-translate');
    element.textContent = translations[language][key];
  });
}

languageSelect.addEventListener('change', (e) => {
  const selectedLanguage = e.target.value;
  
  localStorage.setItem('language', selectedLanguage);
  
  updateTranslations(selectedLanguage);
});

document.addEventListener('DOMContentLoaded', () => {
  const storedLanguage = localStorage.getItem('language');
  
  if (storedLanguage) {
    languageSelect.value = storedLanguage;
    updateTranslations(storedLanguage);
  }
});