// Vérifie si l'utilisateur a donné la permission pour les notifications
function checkNotificationPermission() {
    if (Notification.permission !== "granted") {
        Notification.requestPermission().then(permission => {
            if (permission === "granted") {
                console.log("Notifications activées.");
            } else {
                console.log("Notifications désactivées.");
            }
        });
    }
}

// Affiche une notification pour un nouveau message
function showNewMessageNotification(senderId, messageText) {
    if (Notification.permission === "granted") {
        new Notification("Nouveau message de " + senderId, {
            body: messageText,
            icon: "/static/images/chat_icon.png"  // Chemin vers une icône de notification (facultatif)
        });
    }
}

// Initialisation des notifications
document.addEventListener("DOMContentLoaded", function() {
    checkNotificationPermission();
});
