const ctx = document.getElementById('myChart').getContext('2d');

// Optionnel : définir également la taille du canevas en JavaScript si nécessaire
ctx.canvas.width = 600;  // Largeur en pixels
ctx.canvas.height = 300; // Hauteur en pixels

const myChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['CPU Usage', 'Memory Usage', 'Disk Usage'],
        datasets: [{
            label: '% Usage',
            data: [0, 0, 0],
            backgroundColor: [
                'rgba(255, 99, 132, 0.2)',
                'rgba(54, 162, 235, 0.2)',
                'rgba(255, 206, 86, 0.2)'
            ],
            borderColor: [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)'
            ],
            borderWidth: 1
        }]
    },
    options: {
        maintainAspectRatio: false,  // Permet de gérer le ratio de l'aspect
        scales: {
            y: {
                beginAtZero: true,
                max: 100
            }
        }
    }
});

function updateChart() {
    fetch('/data')
    .then(response => response.json())
    .then(data => {
        myChart.data.datasets[0].data = [data.cpu_percent, data.memory_percent, data.disk_percent];
        myChart.update();
    });
}

setInterval(updateChart, 5000);

// Appel initial pour charger les données lors du premier chargement de la page
updateChart();