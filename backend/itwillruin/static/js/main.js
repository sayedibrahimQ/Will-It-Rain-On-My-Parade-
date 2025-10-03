document.addEventListener('DOMContentLoaded', function () {

    // --- General --- //
    const currentPath = window.location.pathname.split("/").pop();
    const navLinks = document.querySelectorAll('.nav-links a');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });

    // --- Prediction Page --- //
    const forecastCanvas = document.getElementById('forecast-chart');
    if (forecastCanvas) {
        new Chart(forecastCanvas, {
            type: 'line',
            data: {
                labels: ['Event -12h', 'Event -6h', 'Event', 'Event +6h', 'Event +12h', 'Event +18h', 'Event +24h'],
                datasets: [{
                    label: 'Precipitation (mm/hr)',
                    data: [0.1, 0.2, 0.5, 1, 0.8, 0.4, 0.2], // Placeholder data
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.2)',
                    tension: 0.3,
                    fill: true,
                    yAxisID: 'y-precipitation'
                }, {
                    label: 'Probability of Rain (%)',
                    data: [10, 20, 60, 80, 70, 50, 30], // Placeholder data
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.2)',
                    tension: 0.3,
                    fill: true,
                    yAxisID: 'y-probability'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Time Relative to Event',
                            color: '#ecf0f1'
                        },
                        ticks: {
                            color: '#bdc3c7'
                        },
                        grid: {
                            color: '#444'
                        }
                    },
                    'y-precipitation': {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Precipitation (mm/hr)',
                            color: '#ecf0f1'
                        },
                        ticks: {
                            color: '#bdc3c7'
                        },
                        grid: {
                            color: '#444'
                        }
                    },
                    'y-probability': {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Probability of Rain (%)',
                            color: '#ecf0f1'
                        },
                        ticks: {
                            color: '#bdc3c7'
                        },
                        grid: {
                            drawOnChartArea: false, // only draw grid for precipitation axis
                        }
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            color: '#ecf0f1'
                        }
                    }
                }
            }
        });

        const printBtn = document.getElementById('print-btn');
        if(printBtn) {
            printBtn.addEventListener('click', () => window.print());
        }

        const shareBtn = document.getElementById('share-btn');
        if(shareBtn) {
            shareBtn.addEventListener('click', () => {
                if (navigator.share) {
                    navigator.share({
                        title: 'EventWeather Forecast',
                        text: 'Check out this weather forecast for my event!',
                        url: window.location.href
                    }).catch(console.error);
                } else {
                    navigator.clipboard.writeText(window.location.href).then(() => {
                        alert('Link copied to clipboard!');
                    });
                }
            });
        }

        const scrollToTopBtn = document.getElementById('scroll-to-top');
        if(scrollToTopBtn) {
            window.addEventListener('scroll', () => {
                if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
                    scrollToTopBtn.style.display = 'block';
                } else {
                    scrollToTopBtn.style.display = 'none';
                }
            });

            scrollToTopBtn.addEventListener('click', () => {
                document.body.scrollTop = 0; // For Safari
                document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
            });
        }
    }

    // --- Interactive Map Page --- //
    if (document.getElementById('event-form')) {
        const map = L.map('map').setView([30.033333, 31.233334], 10);
        L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
            subdomains: 'abcd',
            maxZoom: 19
        }).addTo(map);

        let marker;
        map.getContainer().style.cursor = 'crosshair';

        const latInput = document.getElementById('latitude');
        const lonInput = document.getElementById('longitude');

        map.on('click', function(e) {
            if (marker) {
                map.removeLayer(marker);
            }
            marker = L.marker(e.latlng).addTo(map);
            latInput.value = e.latlng.lat.toFixed(5);
            lonInput.value = e.latlng.lng.toFixed(5);
        });
    }

    // --- Data Insights Page --- //
    if (document.getElementById('rainfall-chart')) {
        new Chart(document.getElementById('rainfall-chart'), {
            type: 'bar',
            data: {
                labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'],
                datasets: [{
                    label: 'Rainfall (mm)',
                    data: [10, 20, 5, 15, 10, 25, 8], // Placeholder
                    backgroundColor: 'rgba(52, 152, 219, 0.7)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

    if (document.getElementById('region-chart')) {
        new Chart(document.getElementById('region-chart'), {
            type: 'pie',
            data: {
                labels: ['Americas', 'Europe', 'Africa', 'Asia', 'Oceania'],
                datasets: [{
                    data: [30, 15, 25, 20, 10], // Placeholder
                    backgroundColor: ['#3498db', '#2ecc71', '#f1c40f', '#e74c3c', '#9b59b6']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

});