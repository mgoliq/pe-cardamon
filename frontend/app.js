document.addEventListener('DOMContentLoaded', function () {
    // Map setup
    const map = L.map('map').setView([51.1079, 17.0385], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'Map data © OpenStreetMap contributors'
    }).addTo(map);

    let startMarker = null;
    let destMarker = null;
    let selecting = 'start';

    const startInput = document.getElementById('start-point');
    const destInput = document.getElementById('destination-point');
    const depTimeInput = document.getElementById('departure-time');
    const limitInput = document.getElementById('limit');
    const btn = document.getElementById('call-api-btn');
    const statusDiv = document.getElementById('status-message');
    const resultsDiv = document.getElementById('results');

    // Set default departure time to now
    depTimeInput.value = new Date().toISOString().slice(0,16);

    // Map click handler
    map.on('click', function(e) {
        if (selecting === 'start') {
            if (startMarker) map.removeLayer(startMarker);
            startMarker = L.marker(e.latlng, { draggable: true }).addTo(map).bindPopup('Start').openPopup();
            startInput.value = `${e.latlng.lat.toFixed(6)},${e.latlng.lng.toFixed(6)}`;
            selecting = 'dest';
            statusDiv.textContent = 'Now select destination point on the map.';
            startMarker.on('dragend', function(ev) {
                const pos = ev.target.getLatLng();
                startInput.value = `${pos.lat.toFixed(6)},${pos.lng.toFixed(6)}`;
            });
        } else if (selecting === 'dest') {
            if (destMarker) map.removeLayer(destMarker);
            destMarker = L.marker(e.latlng, { draggable: true }).addTo(map).bindPopup('Destination').openPopup();
            destInput.value = `${e.latlng.lat.toFixed(6)},${e.latlng.lng.toFixed(6)}`;
            selecting = null;
            statusDiv.textContent = 'Ready. You can adjust markers or click "Find Routes".';
            destMarker.on('dragend', function(ev) {
                const pos = ev.target.getLatLng();
                destInput.value = `${pos.lat.toFixed(6)},${pos.lng.toFixed(6)}`;
            });
        }
    });

    // Allow user to reset selection by clicking on input fields
    startInput.addEventListener('click', function() {
        selecting = 'start';
        statusDiv.textContent = 'Select start point on the map.';
    });
    destInput.addEventListener('click', function() {
        selecting = 'dest';
        statusDiv.textContent = 'Select destination point on the map.';
    });

    // Button click handler
    btn.addEventListener('click', async function() {
        // Validate inputs
        const start = startInput.value.trim();
        const dest = destInput.value.trim();
        const depTime = depTimeInput.value;
        const limit = limitInput.value || 5;

        if (!start || !dest) {
            statusDiv.textContent = 'Please select both start and destination points.';
            return;
        }

        statusDiv.textContent = 'Searching...';
        resultsDiv.innerHTML = '';

        // Build API URL
        const params = new URLSearchParams({
            start_coordinates: start,
            end_coordinates: dest,
            start_time: depTime ? new Date(depTime).toISOString() : new Date().toISOString(),
            limit: limit
        });
        const url = `/public_transport/city/Wroclaw/closest_departures?${params.toString()}`;

        try {
            const resp = await fetch(url);
            if (!resp.ok) {
                statusDiv.textContent = `API error: ${resp.status}`;
                return;
            }
            const data = await resp.json();
            if (!data.departures || data.departures.length === 0) {
                resultsDiv.innerHTML = '<div>No departures found.</div>';
                statusDiv.textContent = 'No results.';
                return;
            }
            // Display results
            resultsDiv.innerHTML = '';
            data.departures.forEach(dep => {
                const div = document.createElement('div');
                div.className = 'mb-2 p-2 border-b';
                div.innerHTML = `<b>Stop:</b> ${dep.stop.name}<br>
                    <b>Line:</b> ${dep.route_id} <b>To:</b> ${dep.trip_headsign}<br>
                    <b>Departure:</b> ${dep.stop.departure_time}`;
                resultsDiv.appendChild(div);
            });
            statusDiv.textContent = 'Results loaded.';
        } catch (err) {
            statusDiv.textContent = 'Error fetching data.';
            resultsDiv.innerHTML = `<div>${err.message}</div>`;
        }
    });
});
