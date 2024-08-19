document.addEventListener('DOMContentLoaded', () => {
    // Assurez-vous que la connexion est établie avec la bonne URL
    const socket = io.connect('http://localhost:5000', {
        query: { user_id: current_user.id }
    });

    socket.on('user_status', function(data) {
        if (data.status === 'online') {;
        } else if (data.status === 'offline') {;
        }
    });
});
