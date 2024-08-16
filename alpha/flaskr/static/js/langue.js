const translations = {
  fr: {
      applicationParametre: "Application",
      apparence: "Apparence",
      geolocalisation: "Géolocalisation",
      notification: "Notification",
      autres: "Autres",
      demandeAmis: "Demande d'Amis",
      authentificationDoubleFacteur: "Authentification à 2 Facteurs",
      langue: "Langue",
      informationPersonnel: "Information Personnel",
      dateNaissance: "Date de Naissance",
      numeroTelephone: "Numéro de Téléphone",
      email: "E-Mail",
      motDePasse: "Mot de Passe",
      easterEgg: "Easter EGG ???"
  },
  en: {
      applicationParametre: "Application",
      apparence: "Appearance",
      geolocalisation: "Geolocation",
      notification: "Notification",
      autres: "Others",
      demandeAmis: "Friend Requests",
      authentificationDoubleFacteur: "Two-Factor Authentication",
      langue: "Language",
      informationPersonnel: "Personal Information",
      dateNaissance: "Date of Birth",
      numeroTelephone: "Phone Number",
      email: "E-Mail",
      motDePasse: "Password",
      easterEgg: "Easter EGG ???"
  },
  es: {
      applicationParametre: "Aplicación",
      apparence: "Apariencia",
      geolocalisation: "Geolocalización",
      notification: "Notificación",
      autres: "Otros",
      demandeAmis: "Solicitud de Amistad",
      authentificationDoubleFacteur: "Autenticación de Dos Factores",
      langue: "Idioma",
      informationPersonnel: "Información Personal",
      dateNaissance: "Fecha de Nacimiento",
      numeroTelephone: "Número de Teléfono",
      email: "Correo Electrónico",
      motDePasse: "Contraseña",
      easterEgg: "¿Huevo de Pascua???"
  },
  de: {
      applicationParametre: "Anwendung",
      apparence: "Aussehen",
      geolocalisation: "Geolokalisierung",
      notification: "Benachrichtigung",
      autres: "Andere",
      demandeAmis: "Freundschaftsanfragen",
      authentificationDoubleFacteur: "Zwei-Faktor-Authentifizierung",
      langue: "Sprache",
      informationPersonnel: "Persönliche Informationen",
      dateNaissance: "Geburtsdatum",
      numeroTelephone: "Telefonnummer",
      email: "E-Mail",
      motDePasse: "Passwort",
      easterEgg: "Osterei ???"
  }
};

function changeLanguage() {
  const selectedLanguage = document.getElementById('Langue').value;
  document.querySelectorAll('[data-translate]').forEach(element => {
      const key = element.getAttribute('data-translate');
      element.textContent = translations[selectedLanguage][key];
  });
}

document.getElementById('Langue').addEventListener('change', changeLanguage);
