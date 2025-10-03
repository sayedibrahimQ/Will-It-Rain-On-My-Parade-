document.addEventListener('DOMContentLoaded', function () {
    // Map functionality for the home page
    const mapContainer = document.getElementById('map-container');
    if (mapContainer) {
        const mapToggle = document.getElementById('mapToggle');
        const locationSearch = document.getElementById('location-search');
        const latLonInput = document.getElementById('lat-lon');
        let map = null;
        let marker = null;

        mapToggle.addEventListener('change', function () {
            if (this.checked) {
                locationSearch.style.display = 'none';
                mapContainer.style.display = 'block';
                if (!map) {
                    map = L.map('map-container').setView([30.0444, 31.2357], 10);
                    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    }).addTo(map);

                    map.on('click', function (e) {
                        if (marker) {
                            map.removeLayer(marker);
                        }
                        marker = L.marker(e.latlng).addTo(map);
                        latLonInput.value = e.latlng.lat + ',' + e.latlng.lng;
                    });
                }
            } else {
                locationSearch.style.display = 'block';
                mapContainer.style.display = 'none';
            }
        });
    }

    // Historical Data Chart
    const historicalChartCanvas = document.getElementById('historical-chart');
    if (historicalChartCanvas) {
        new Chart(historicalChartCanvas, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [{
                    label: 'Average Temperature (°C)',
                    data: [5, 6, 8, 12, 15, 18, 20, 19, 16, 12, 8, 6],
                    borderColor: '#007bff',
                    tension: 0.1
                }, {
                    label: 'Average Precipitation (mm)',
                    data: [50, 45, 55, 60, 65, 70, 75, 80, 70, 60, 55, 50],
                    borderColor: '#17a2b8',
                    tension: 0.1
                }]
            }
        });
    }

    // Probability Chart
    const probabilityChartCanvas = document.getElementById('probability-chart');
    if (probabilityChartCanvas) {
        new Chart(probabilityChartCanvas, {
            type: 'bar',
            data: {
                labels: ['🔥 Very Hot', '❄️ Very Cold', '🌧 Very Wet', '💨 Very Windy', '😓 Uncomfortable'],
                datasets: [{
                    label: 'Probability',
                    data: [35, 10, 60, 20, 45],
                    backgroundColor: [
                        'rgba(220, 53, 69, 0.7)',
                        'rgba(23, 162, 184, 0.7)',
                        'rgba(0, 123, 255, 0.7)',
                        'rgba(255, 193, 7, 0.7)',
                        'rgba(108, 117, 125, 0.7)'
                    ]
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
});
