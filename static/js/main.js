let map = L.map('map').setView([38.8977, -77.0365], 14);
let currentInfrastructure = [];


L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

document.getElementById('searchForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);

            fetch('/search', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                        if (data.success) {

                            // Store the infrastructure data
                            currentInfrastructure = data.infrastructure;

                            // Clear existing markers
                            map.eachLayer((layer) => {
                                if (layer instanceof L.CircleMarker) {
                                    map.removeLayer(layer);
                                }
                            });

                            // Center map on city
                            map.setView(data.center, 14);

                            // Add markers for infrastructure
                            data.infrastructure.forEach(item => {
                                        const color = getRiskColor(item.risk_score);
                                        const marker = L.circleMarker([item.latitude, item.longitude], {
                                            radius: 8,
                                            fillColor: color,
                                            color: color,
                                            weight: 1,
                                            opacity: 1,
                                            fillOpacity: 0.8
                                        });

                                        marker.bindPopup(`
                    <h3>${item.name}</h3>
                    <p>Type: ${item.type}</p>
                    <p>Risk Score: ${item.risk_score.toFixed(2)}</p>
                    <p>Risk Factors:</p>
                    <ul>
                        ${Object.entries(item.risk_factors).map(([key, value]) => 
                            `<li>${key}: ${value.toFixed(2)}</li>`).join('')}
                    </ul>
                `);
                
                marker.addTo(map);
            });
            
            // Update results sidebar
            updateResults(data.infrastructure);
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => console.error('Error:', error));
});

function getRiskColor(score) {
    if (score >= 0.8) { return '#ff0000';}
    else if (score >= 0.6 && score < 0.8) {return '#ffa500';}
    else if (score >= 0.4 && score < 0.6) {return '#ffff00';}
    else return '#00ff00';
}

// function to determine risk class
function getRiskClass(score) {
    if (score >= 0.8) return 'risk-critical';
    else if (score >= 0.6 && score < 0.8) return 'risk-high';
    else if (score >= 0.4 && score < 0.6) return 'risk-moderate';
    else return 'risk-low';
}


// Update the updateResults function
// function updateResults(infrastructure) {
    // const resultsDiv = document.getElementById('results');
    // resultsDiv.innerHTML = `
    //     <h2><i class="fas fa-list"></i> Infrastructure Risk Levels</h2>
    // `;
    
    // infrastructure.forEach(item => {
    //     const riskClass = getRiskClass(item.risk_score);
    //     const itemDiv = document.createElement('div');
    //     itemDiv.className = 'infrastructure-item';
    //     itemDiv.innerHTML = `
    //         <h3><i class="fas fa-building"></i> ${item.name}</h3>
    //         <div class="type"><i class="fas fa-road"></i> ${item.type}</div>
    //         <div class="risk-score ${riskClass}">
    //             Risk Score: ${item.risk_score.toFixed(2)}
    //         </div>
    //         <div class="risk-factors">
    //             ${Object.entries(item.risk_factors).map(([key, value]) => `
    //                 <div class="risk-factor">
    //                     <span>${key.replace('_', ' ').toUpperCase()}</span>
    //                     <span>${value.toFixed(2)}</span>
    //                 </div>
    //             `).join('')}
    //         </div>
    //     `;
    //     resultsDiv.appendChild(itemDiv);
    // });
// }

function updateResults(infrastructure) {
    // Update total count
    document.getElementById('totalResults').textContent = infrastructure.length;
    
    // Get current sort and filter values
    const sortBy = document.getElementById('sortBy').value;
    const filterRisk = document.getElementById('filterRisk').value;
    
    // Filter infrastructure
    let filtered = infrastructure;
    if (filterRisk !== 'all') {
        filtered = infrastructure.filter(item => {
            switch(filterRisk) {
                case 'critical': return item.risk_score >= 0.8;
                case 'high': return item.risk_score >= 0.6 && item.risk_score < 0.8;
                case 'moderate': return item.risk_score >= 0.4 && item.risk_score < 0.6;
                case 'low': return item.risk_score < 0.4;
            }
        });
    }
    
    // Sort infrastructure
    filtered.sort((a, b) => {
        switch(sortBy) {
            case 'name': return a.name.localeCompare(b.name);
            case 'risk': return b.risk_score - a.risk_score;
            case 'type': return a.type.localeCompare(b.type);
            default: return 0;
        }
    });
    
    // Update results display
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';
    
    // Display filtered and sorted results
    filtered.forEach(item => {
        const riskClass = getRiskClass(item.risk_score);
        const itemDiv = document.createElement('div');
        itemDiv.className = 'infrastructure-item';
        itemDiv.innerHTML = `
            <h3><i class="fas fa-building"></i> ${item.name}</h3>
            <div class="type"><i class="fas fa-road"></i> ${item.type}</div>
            <div class="risk-score ${riskClass}">
                Risk Score: ${item.risk_score.toFixed(2)}
            </div>
            <div class="risk-factors">
                ${Object.entries(item.risk_factors).map(([key, value]) => `
                    <div class="risk-factor">
                        <span>${key.replace('_', ' ').toUpperCase()}</span>
                        <span>${value.toFixed(2)}</span>
                    </div>
                `).join('')}
            </div>
        `;
        resultsDiv.appendChild(itemDiv);
    });
}


// Add event listeners for controls
document.getElementById('sortBy').addEventListener('change', () => {
    updateResults(currentInfrastructure);
});

document.getElementById('filterRisk').addEventListener('change', () => {
    updateResults(currentInfrastructure);
});


// // Define base map layers
// let baseMapLayers = {
//     'OpenStreetMap': L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
//         attribution: '© OpenStreetMap contributors'
//     }),
//     'Satellite': L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
//         attribution: '© Esri'
//     }),
//     'Dark': L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png', {
//         attribution: '© Stadia Maps'
//     }),
//     'Terrain': L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
//         attribution: '© OpenTopoMap'
//     })
// };

// // Set default layer
// baseMapLayers['OpenStreetMap'].addTo(map);

// // Add layer control to map
// L.control.layers(baseMapLayers, null, {
//     position: 'bottomright',
//     collapsed: true
// }).addTo(map);



// Define custom control styles
const customControlStyle = `
    .leaflet-control-layers {
        border: none !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1) !important;
        background: #2563eb !important;
        padding: 10px !important;
    }
    .leaflet-control-layers-toggle {
        background-color: #2563eb !important;
        width: 40px !important;
        height: 40px !important;
        border-radius: 8px !important;
    }
    .leaflet-control-layers-expanded {
        padding: 15px !important;
        font-family: 'Inter', sans-serif !important;
        min-width: 200px !important;
    }
    .leaflet-control-layers-list {
        margin: 5px 0 !important;
    }
    .leaflet-control-layers-base label {
        margin: 5px 0 !important;
        padding: 8px 12px !important;
        border-radius: 6px !important;
        transition: background-color 0.3s !important;
        cursor: pointer !important;
    }
    .leaflet-control-layers-base label:hover {
        background-color: #1e40af !important;
    }
    .leaflet-control-layers-base input[type="radio"] {
        display: none !important;
    }
    .leaflet-control-layers-base span {
        font-weight: 500 !important;
        color: #ffffff !important;
    }
    .leaflet-control-layers-base label.active span {
        color: var(--primary-color) !important;
    }
`;

// Add styles to document
const styleSheet = document.createElement("style");
styleSheet.innerText = customControlStyle;
document.head.appendChild(styleSheet);

// Define base map layers
let baseMapLayers = {
    'Standard': L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap'
    }),
    'Satellite': L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: '© Esri'
    }),
    'Dark Mode': L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png', {
        attribution: '© Stadia Maps'
    }),
    'Terrain': L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenTopoMap'
    })
};

// Set default layer
baseMapLayers['Standard'].addTo(map);

// Add layer control
const layerControl = L.control.layers(baseMapLayers, null, {
    position: 'bottomright',
    collapsed: true
}).addTo(map);