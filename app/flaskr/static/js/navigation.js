document.addEventListener('keydown', function(event) {
    const page = window.location.pathname.split('/').pop();

    if (page === 'album.html') {
        if (event.key === 'ArrowLeft') {
            window.location.href = 'chat.html';
        } else if (event.key === 'ArrowRight') {
            window.location.href = 'parametres.html';
        }
    } else if (page === 'photo.html') {
        if (event.key === 'ArrowLeft') {
            window.location.href = 'amis.html';
        } else if (event.key === 'ArrowRight') {
            window.location.href = 'chat.html';
        }
    } else if (page === 'chat.html') {
        if (event.key === 'ArrowLeft') {
            window.location.href = 'photo.html';
        } else if (event.key === 'ArrowRight') {
            window.location.href = 'album.html';
        }
    } else if (page === 'parametres.html') {
        if (event.key === 'ArrowLeft') {
            window.location.href = 'album.html';
        }
    } else if (page === 'amis.html') {
        if (event.key === 'ArrowRight') {
            window.location.href = 'photo.html';
        }
    }
});