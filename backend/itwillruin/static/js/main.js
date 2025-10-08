document.addEventListener('DOMContentLoaded', function () {
    // --- Elements ---
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    
    let chartInstances = {};
    let map = null;
    let marker = null;

    // --- Active Nav Link Logic ---
    const currentPagePath = window.location.pathname;
    const navLinks = document.querySelectorAll('#desktop-nav a, #mobile-menu a');

    navLinks.forEach(link => {
        const linkPath = new URL(link.href).pathname;
        if (linkPath === currentPagePath) {
            link.classList.add('active');
        }
    });

    // --- Mobile Menu Toggle ---
    if (mobileMenuButton) {
        mobileMenuButton.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
            mobileMenuButton.querySelector('[data-lucide="menu"]').classList.toggle('hidden');
            mobileMenuButton.querySelector('[data-lucide="x"]').classList.toggle('hidden');
        });
    }
    
    // --- Icon Rendering ---
    lucide.createIcons();
    
    // --- Page-specific Initializers ---
    if (document.getElementById('temperature-chart')) {
        initializeDashboardCharts();
    }
    if (document.getElementById('map')) {
        initializePredictionForm();
    }

    // --- Charting Logic ---
    function initializeDashboardCharts() {
        const chartOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { labels: { color: '#94a3b8' } } },
            scales: {
                y: { beginAtZero: true, grid: { color: 'rgba(255, 255, 255, 0.1)' }, ticks: { color: '#94a3b8' } },
                x: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } }
            }
        };
        
        const tempCtx = document.getElementById('temperature-chart');
        if (tempCtx && !chartInstances.temp) {
            chartInstances.temp = new Chart(tempCtx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
                    datasets: [{
                        label: 'Temperature (°C)',
                        data: [10, 12, 15, 18, 22, 25, 28],
                        borderColor: '#38bdf8',
                        backgroundColor: 'rgba(56, 189, 248, 0.1)',
                        tension: 0.3, fill: true, pointBackgroundColor: '#38bdf8', pointBorderColor: '#0f172a'
                    }]
                },
                options: chartOptions
            });
        }

        const precipCtx = document.getElementById('precipitation-chart');
        if (precipCtx && !chartInstances.precip) {
            chartInstances.precip = new Chart(precipCtx, {
                type: 'bar',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
                    datasets: [{
                        label: 'Precipitation (mm)',
                        data: [50, 40, 60, 20, 10, 5, 2],
                        backgroundColor: 'rgba(56, 189, 248, 0.6)',
                        borderColor: '#38bdf8', borderWidth: 1
                    }]
                },
                options: chartOptions
            });
        }
    }

    // --- Prediction Form and Map Logic ---
    function initializePredictionForm() {
        const form = document.getElementById('prediction-form');
        const latitudeInput = document.getElementById('latitude');
        const longitudeInput = document.getElementById('longitude');
        const coordsDisplay = document.getElementById('coords-display');
        
        const initialLatLng = [30.0444, 31.2357]; // Default to Cairo

        // Initialize Map
        map = L.map('map').setView(initialLatLng, 6);
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
            subdomains: 'abcd',
            maxZoom: 20
        }).addTo(map);

        // Initialize Marker
        marker = L.marker(initialLatLng, { draggable: true }).addTo(map)
            .bindPopup('Your event location').openPopup();

        function updateCoordinates(lat, lng) {
            latitudeInput.value = lat.toFixed(4);
            longitudeInput.value = lng.toFixed(4);
            coordsDisplay.textContent = `Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)}`;
        }

        updateCoordinates(initialLatLng[0], initialLatLng[1]);
        
        // Map Event Listeners
        map.on('click', function(e) {
            marker.setLatLng(e.latlng);
            updateCoordinates(e.latlng.lat, e.latlng.lng);
        });
        
        marker.on('dragend', function(e) {
            const latLng = e.target.getLatLng();
            updateCoordinates(latLng.lat, latLng.lng);
        });

        // Form submission logic
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const results = document.getElementById('prediction-results');
            results.classList.remove('hidden');

            document.getElementById('rain-chance').innerText = '78% 🌧️';
            document.getElementById('temperature').innerText = '27°C';
            document.getElementById('wind-speed').innerText = '5.4 m/s';
            document.getElementById('ai-summary').innerText = 'It’s likely to be warm and humid with a high chance of rain in the afternoon.';
            document.getElementById('ai-outlook').innerText = 'Risky';
            document.getElementById('ai-clothing').innerText = 'Light, waterproof jacket and comfortable shoes.';
            document.getElementById('ai-contingency').innerText = 'Have a backup indoor location or tents available.';
            document.getElementById('ai-fun-fact').innerText = 'NASA\'s Earth-observing satellites help us understand our planet\'s climate and weather patterns.';
            
            lucide.createIcons({ nodes: [results] });
        });
    }
});
