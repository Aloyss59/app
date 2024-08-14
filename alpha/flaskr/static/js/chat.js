var socket = io();
var user_id = "{{ current_user.id }}";  // Récupérer l'ID utilisateur depuis le serveur Flask

var form = document.getElementById("form");
var input = document.getElementById("message_input");

form.addEventListener("submit", function (e) {
    e.preventDefault();
    if (input.value.trim() !== "") {
        socket.emit("message", {
            text: input.value,
            sender_id: user_id,
            receiver_id: "{{ user_id }}"  // L'ID de l'utilisateur avec qui vous discutez
        });
        input.value = "";
    }
});

socket.on("message", function (data) {
    var item = document.createElement("li");
    var currentTime = formatDateToLocalTime(data.created_at);

    if (data.sender_id === user_id) {
        item.classList.add("message", "sent");
        item.innerHTML = "<small>" + currentTime + "</small> (You) " + data.text + "<br>";
    } else {
        item.classList.add("message", "received");
        item.innerHTML = "<small>" + currentTime + "</small>" + data.text + "<br>";

        // Affiche une notification si le message est d'un autre utilisateur
        showNewMessageNotification(data.sender_id, data.text);
    }

    document.getElementById("messages").appendChild(item);
    window.scrollTo(0, document.body.scrollHeight);
});

function formatDateToLocalTime(utcDateString) {
    var localDate = new Date(utcDateString);
    return localDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}
