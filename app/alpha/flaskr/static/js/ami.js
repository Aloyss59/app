function trierAmis() {
    // Collecter tous les éléments LI dans un tableau
    const amis = Array.from(document.querySelectorAll('.listeamis > .ami'));
  
    // Trier les éléments LI dans l'ordre alphabétique en fonction de l'élément SPAN avec la classe amisname
    amis.sort((a, b) => {
      const aname = a.querySelector('.amisname').textContent.trim().toLowerCase();
      const bname = b.querySelector('.amisname').textContent.trim().toLowerCase();
  
      if (aname < bname) {
        return -1;
      } else if (aname > bname) {
        return 1;
      } else {
        return 0;
      }
    });
  
    // Réinjecter les éléments LI triés dans les éléments UL
    const listeAmis = document.querySelectorAll('.listeamis');
    listeAmis.forEach((ul) => {
      ul.innerHTML = '';
      amis.forEach((li) => {
        ul.appendChild(li);
      });
    });
  }
  
  // Exécuter la fonction trierAmis() une fois que le contenu de la page est chargé
  document.addEventListener('DOMContentLoaded', trierAmis);