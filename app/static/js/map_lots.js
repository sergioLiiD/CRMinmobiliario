document.addEventListener('DOMContentLoaded', function() {
    // Add marker styles dynamically
    const markerStyles = `
        .lot-marker {
            position: absolute;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            transform: translate(-50%, -50%);
            cursor: pointer;
            border: 2px solid white;
            box-shadow: 0 0 5px rgba(0,0,0,0.5);
        }
        .green-marker {
            background-color: green;
        }
        .yellow-marker {
            background-color: yellow;
        }
        .red-marker {
            background-color: red;
        }
        .gray-marker {
            background-color: gray;
        }
    `;
    
    const styleElement = document.createElement('style');
    styleElement.textContent = markerStyles;
    document.head.appendChild(styleElement);

    const mapContainer = document.getElementById('map-container');
    const mapImage = document.getElementById('active-map-image');
    const lotMarkers = document.getElementById('lot-markers');
    const lotPlacementForm = document.getElementById('map-location-form');

    // Extensive logging for form detection
    console.log('Map Container:', mapContainer);
    console.log('Map Image:', mapImage);
    console.log('Lot Markers:', lotMarkers);
    console.log('Lot Placement Form:', lotPlacementForm);

    if (!lotPlacementForm) {
        console.error('Form not found!');
        console.error('Document body:', document.body.innerHTML);
        return;
    }

    // Capture form inputs
    const fraccionamientoSelect = document.getElementById('fraccionamiento-select');
    const paqueteSelect = document.getElementById('paquete-select');
    const lotSelect = document.getElementById('lot-select');
    const xCoordinateInput = document.getElementById('x-coordinate');
    const yCoordinateInput = document.getElementById('y-coordinate');
    const statusSelect = document.getElementById('status-select'); 
    const submitButton = document.querySelector('input[type="submit"]');

    // Debug logging
    console.log('Fraccionamiento:', fraccionamientoSelect);
    console.log('Paquete:', paqueteSelect);
    console.log('Lot:', lotSelect);
    console.log('X Coordinate:', xCoordinateInput);
    console.log('Y Coordinate:', yCoordinateInput);
    console.log('Status:', statusSelect);

    // Disable Paquete and Lot selects initially
    paqueteSelect.disabled = true;
    lotSelect.disabled = true;

    // Function to normalize lot status
    function normalizeLotStatus(status) {
        // Normalize lot status to a consistent format
        const statusMapping = {
            'libre': 'Libre',
            'LIBRE': 'Libre',
            'Libre': 'Libre',
            'apartado': 'Apartado',
            'APARTADO': 'Apartado',
            'Apartado': 'Apartado',
            'titulado': 'Titulado',
            'TITULADO': 'Titulado',
            'Titulado': 'Titulado',
            
            // Additional mappings for variations
            'lib': 'Libre',
            'LIB': 'Libre',
            'Li': 'Libre',
            'disponible': 'Libre',
            'DISPONIBLE': 'Libre',
            'Disponible': 'Libre',
            
            'ap': 'Apartado',
            'AP': 'Apartado',
            'Ap': 'Apartado',
            'reservado': 'Apartado',
            'RESERVADO': 'Apartado',
            'Reservado': 'Apartado',
            
            'ti': 'Titulado',
            'TI': 'Titulado',
            'Ti': 'Titulado',
            'vendido': 'Titulado',
            'VENDIDO': 'Titulado',
            'Vendido': 'Titulado'
        };

        // Handle null or undefined
        if (!status) {
            return 'Libre';
        }

        // Convert to string and trim
        const statusStr = String(status).trim();

        // Return mapped status or default to Libre
        return statusMapping[statusStr] || 'Libre';
    }

    // Function to fetch lot statuses and create a mapping
    async function fetchLotStatuses() {
        try {
            const response = await fetch('/api/lot_statuses');
            const lotStatuses = await response.json();
            
            // Create a mapping of lot ID to normalized status
            const lotStatusMap = {};
            lotStatuses.forEach(lot => {
                lotStatusMap[lot.id] = {
                    originalStatus: lot.original_status,
                    normalizedStatus: normalizeLotStatus(lot.original_status)
                };
            });
            
            return lotStatusMap;
        } catch (error) {
            console.error('Error fetching lot statuses:', error);
            return {};
        }
    }

    // Function to fetch map location statuses
    async function fetchMapLocationStatuses() {
        try {
            const response = await fetch('/api/map_location_statuses');
            const mapLocationStatuses = await response.json();
            
            // Create a mapping of lot ID to map location status
            const mapLocationStatusMap = {};
            mapLocationStatuses.forEach(location => {
                mapLocationStatusMap[location.lot_id] = {
                    originalStatus: location.original_status,
                    normalizedStatus: normalizeLotStatus(location.original_status)
                };
            });
            
            return mapLocationStatusMap;
        } catch (error) {
            console.error('Error fetching map location statuses:', error);
            return {};
        }
    }

    // Populate status dropdown with UPPERCASE values
    statusSelect.innerHTML = `
        <option value="">Select Status</option>
        <option value="LIBRE">Libre</option>
        <option value="APARTADO">Apartado</option>
        <option value="TITULADO">Titulado</option>
    `;

    // Fraccionamiento change event
    fraccionamientoSelect.addEventListener('change', function() {
        // Reset paquete and lot selects
        paqueteSelect.innerHTML = '<option value="0">Select Paquete</option>';
        paqueteSelect.disabled = true;
        lotSelect.innerHTML = '<option value="0">Select Lot</option>';
        lotSelect.disabled = true;

        const fraccionamientoId = this.value;
        if (!fraccionamientoId || fraccionamientoId === '0') return;

        console.log(`Fetching paquetes for Fraccionamiento ID: ${fraccionamientoId}`);

        // Fetch paquetes for selected fraccionamiento
        fetch(`/api/paquetes/${fraccionamientoId}`)
            .then(response => {
                console.log('Response status:', response.status);
                return response.json();
            })
            .then(paquetes => {
                console.log('Paquetes received:', paquetes);
                
                if (paquetes.length === 0) {
                    console.warn('No paquetes found for this fraccionamiento');
                    paqueteSelect.innerHTML = '<option value="0">No paquetes available</option>';
                } else {
                    paqueteSelect.innerHTML = '<option value="0">Select Paquete</option>';
                    paquetes.forEach(paquete => {
                        const option = document.createElement('option');
                        option.value = paquete.id;
                        option.textContent = paquete.nombre;
                        paqueteSelect.appendChild(option);
                    });
                }
                paqueteSelect.disabled = false;
            })
            .catch(error => {
                console.error('Error fetching paquetes:', error);
                alert('Error fetching paquetes. Check browser console for details.');
                paqueteSelect.innerHTML = '<option value="0">Error loading paquetes</option>';
                paqueteSelect.disabled = false;
            });
    });

    // Paquete change event
    paqueteSelect.addEventListener('change', function() {
        // Reset lot select
        lotSelect.innerHTML = '<option value="0">Select Lot</option>';
        lotSelect.disabled = true;

        const paqueteId = this.value;
        if (!paqueteId || paqueteId === '0') return;

        // Fetch all lots for selected paquete initially
        fetch(`/api/lots/${paqueteId}`)
            .then(response => response.json())
            .then(lots => {
                console.log('All Lots received:', lots);
                
                if (lots.length === 0) {
                    console.warn('No lots found for this paquete');
                    lotSelect.innerHTML = '<option value="0">No lots available</option>';
                } else {
                    lotSelect.innerHTML = '<option value="0">Select Lot</option>';
                    lots.forEach(lot => {
                        const option = document.createElement('option');
                        option.value = lot.id;
                        option.textContent = `${lot.manzana} - ${lot.lote} (${normalizeLotStatus(lot.estado_del_inmueble)})`;
                        lotSelect.appendChild(option);
                    });
                }
                lotSelect.disabled = false;
            })
            .catch(error => {
                console.error('Error fetching lots:', error);
                alert('Error fetching lots. Check browser console for details.');
                lotSelect.innerHTML = '<option value="0">Error loading lots</option>';
                lotSelect.disabled = false;
            });
    });

    // Status change event
    statusSelect.addEventListener('change', function() {
        const selectedStatus = this.value;
        const paqueteId = paqueteSelect.value;

        console.log('Selected Status (Exact):', selectedStatus);
        console.log('Paquete ID:', paqueteId);

        // If no status or paquete selected, do nothing
        if (!selectedStatus || selectedStatus === '') {
            console.log('No status selected');
            lotSelect.innerHTML = '<option value="0">Select Lot</option>';
            lotSelect.disabled = true;
            return;
        }

        if (!paqueteId || paqueteId === '0') {
            console.log('No paquete selected');
            alert('Please select a Paquete first');
            this.selectedIndex = 0;
            return;
        }

        // Normalize status to title case
        const normalizedStatus = normalizeLotStatus(selectedStatus);

        // Fetch lots filtered by status
        fetch(`/api/lots/${paqueteId}/${normalizedStatus}`)
            .then(response => {
                console.log('Response Status:', response.status);
                return response.json();
            })
            .then(lots => {
                console.log(`Lots with status ${normalizedStatus}:`, lots);

                // Clear existing options
                lotSelect.innerHTML = '<option value="0">Select Lot</option>';

                if (lots.length === 0) {
                    console.log(`No lots found with status ${normalizedStatus}`);
                    lotSelect.innerHTML = `<option value="0">No ${normalizedStatus} lots available</option>`;
                    lotSelect.disabled = true;
                } else {
                    lots.forEach(lot => {
                        console.log('Processing lot:', lot);
                        const option = document.createElement('option');
                        option.value = lot.id;
                        option.textContent = `${lot.manzana} - ${lot.lote} (${normalizeLotStatus(lot.estado_del_inmueble)})`;
                        lotSelect.appendChild(option);
                    });
                    lotSelect.disabled = false;
                }
            })
            .catch(error => {
                console.error('Error fetching filtered lots:', error);
                alert('Error filtering lots. Check browser console for details.');
                lotSelect.innerHTML = '<option value="0">Error loading lots</option>';
                lotSelect.disabled = true;
            });
    });

    // Ensure status is uppercase for server-side processing
    const statusInput = document.getElementById('status');
    if (statusInput) {
        statusInput.value = statusInput.value.toUpperCase();
    }

    // Ensure status is always uppercase when submitting
    lotPlacementForm.addEventListener('submit', function(event) {
        event.preventDefault();

        // Validate form inputs
        const fraccionamientoSelect = document.getElementById('fraccionamiento-select');
        const paqueteSelect = document.getElementById('paquete-select');
        const lotSelect = document.getElementById('lot-select');
        const xCoordinateInput = document.getElementById('x-coordinate');
        const yCoordinateInput = document.getElementById('y-coordinate');
        const statusSelect = document.getElementById('status-select');

        // Normalize status
        const normalizedStatus = normalizeLotStatus(statusSelect.value);

        // Prepare form data
        const formData = new FormData();
        formData.append('fraccionamiento', fraccionamientoSelect.value);
        formData.append('paquete', paqueteSelect.value);
        formData.append('lot_id', lotSelect.value);
        formData.append('map_image_id', document.getElementById('map-image-id').value);
        formData.append('x_coordinate', xCoordinateInput.value);
        formData.append('y_coordinate', yCoordinateInput.value);
        formData.append('status', normalizedStatus);

        // Send request to server
        fetch('/api/map/location', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            // Always try to parse as JSON
            return response.json().then(data => {
                if (!response.ok) {
                    // If the response is not OK, throw an error with the data
                    throw new Error(data.message || 'An error occurred');
                }
                return data;
            });
        })
        .then(data => {
            // Check if location was successfully created
            if (data.id) {
                // Update existing lots list
                const existingLotsList = document.getElementById('existing-lots-list');
                const lotName = lotSelect.options[lotSelect.selectedIndex].text;
                const listItem = document.createElement('li');
                listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
                listItem.setAttribute('data-lot-id', data.lot_id);
                listItem.setAttribute('data-x-coordinate', data.x_coordinate);
                listItem.setAttribute('data-y-coordinate', data.y_coordinate);
                listItem.setAttribute('data-status', data.status);
                listItem.innerHTML = `
                    ${lotName}
                    <span class="badge bg-primary">${data.status}</span>
                `;
                existingLotsList.appendChild(listItem);

                // Remove lot from dropdown
                lotSelect.querySelector(`option[value="${data.lot_id}"]`).remove();

                // Reset form
                xCoordinateInput.value = '';
                yCoordinateInput.value = '';

                // Create marker for the new location
                createLotMarker(data.lot_id, data.x_coordinate, data.y_coordinate, data.status);

                // Show success message
                alert('Lot placed successfully!');
            } else {
                // Unexpected response
                throw new Error('Unexpected server response');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            
            // Check if error has a detailed message
            let errorMessage = 'An error occurred while placing the lot.';
            if (error.message) {
                errorMessage = error.message;
            }

            // Show error alert
            alert(errorMessage);
        });
    });

    // Function to get CSRF token
    async function getCsrfToken() {
        try {
            // First, check for existing meta tag
            const csrfTokenElement = document.querySelector('meta[name="csrf-token"]');
            if (csrfTokenElement) {
                return csrfTokenElement.getAttribute('content');
            }

            // If no meta tag, fetch from server
            const response = await fetch('/get-csrf-token', {
                method: 'GET',
                credentials: 'same-origin'
            });

            if (!response.ok) {
                console.error('Failed to fetch CSRF token');
                return null;
            }

            const data = await response.json();
            return data.csrf_token;
        } catch (error) {
            console.error('Error getting CSRF token:', error);
            return null;
        }
    }

    // Click event on map to place lot
    mapImage.addEventListener('click', async function(event) {
        console.log('Map clicked');
        console.log('Lot select value:', lotSelect.value);
        console.log('Status select value:', statusSelect.value);

        if (!lotSelect.value || lotSelect.value === '0') {
            console.warn('No lot selected');
            alert('Please select a lot first');
            return;
        }

        // Get click coordinates
        const rect = mapImage.getBoundingClientRect();
        const x = ((event.clientX - rect.left) / rect.width) * 100;
        const y = ((event.clientY - rect.top) / rect.height) * 100;

        // Get selected lot and status
        const lotId = lotSelect.value;
        const status = statusSelect.value || 'Libre';  // Default to 'Libre' if no status

        console.log(`Attempting to place marker for Lot ${lotId} at coordinates (${x}, ${y}) with status ${status}`);

        // Debug lot placement
        debugLotPlacement(lotId, x, y, status);

        try {
            // Create marker
            const marker = await createLotMarker(lotId, x, y, status);

            // Log marker creation
            console.log('Marker created:', marker);

            // Prepare data for server
            const mapLocationData = {
                lot_id: lotId,
                x_coordinate: x,
                y_coordinate: y,
                status: normalizeLotStatus(status)
            };

            console.log('Sending map location data:', mapLocationData);

            // Get CSRF token
            const csrfToken = await getCsrfToken();

            // Send marker location to server
            const response = await fetch('/api/map-location-api', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken || ''  // Include CSRF token if available
                },
                body: JSON.stringify(mapLocationData),
                credentials: 'same-origin'  // Ensure cookies are sent with the request
            });

            // Check content type before parsing
            const contentType = response.headers.get('content-type');
            console.log('Response content type:', contentType);

            if (!response.ok) {
                let errorData = {};
                try {
                    // Try to parse JSON if possible
                    if (contentType && contentType.includes('application/json')) {
                        errorData = await response.json();
                    } else {
                        // If not JSON, get text to log the full response
                        const responseText = await response.text();
                        console.error('Non-JSON error response:', responseText);
                        errorData = { 
                            message: 'Unexpected server response', 
                            responseText: responseText 
                        };
                    }
                } catch (parseError) {
                    console.error('Error parsing error response:', parseError);
                    errorData = { 
                        message: 'Failed to parse server error response',
                        status: response.status,
                        statusText: response.statusText
                    };
                }

                console.error('Failed to save map location:', errorData);
                
                // More detailed error alert
                const errorMessage = errorData.message || 'Unknown error occurred';
                
                // Specific handling for no active map
                if (errorMessage.includes('No active map image')) {
                    alert('Error: No active map image available. Please upload a map image first.');
                } else {
                    alert(`Error saving lot location: ${errorMessage}`);
                }
                
                // Remove marker if server save fails
                marker.remove();
                
                // Log additional details about the error
                console.error('Full error response:', {
                    status: response.status,
                    statusText: response.statusText,
                    errorDetails: errorData
                });
            } else {
                // Ensure response is JSON
                if (contentType && contentType.includes('application/json')) {
                    const responseData = await response.json();
                    console.log('Map location saved successfully:', responseData);
                } else {
                    const responseText = await response.text();
                    console.warn('Unexpected response type:', responseText);
                    alert('Received unexpected server response');
                }
            }
        } catch (error) {
            console.error('Comprehensive error placing lot marker:', error);
            
            // More informative error handling
            if (error.response) {
                // The request was made and the server responded with a status code
                console.error('Server responded with error:', error.response.data);
                alert(`Server error: ${error.response.data.message || 'Unknown server error'}`);
            } else if (error.request) {
                // The request was made but no response was received
                console.error('No response received:', error.request);
                alert('No response from server. Please check your network connection.');
            } else {
                // Something happened in setting up the request
                console.error('Error setting up request:', error.message);
                alert(`Error: ${error.message}`);
            }
        }
    });

    // Render existing lot markers
    const existingLocations = document.querySelectorAll('#existing-lots-list li');
    existingLocations.forEach(location => {
        const lotId = location.getAttribute('data-lot-id');
        const x = location.getAttribute('data-x-coordinate');
        const y = location.getAttribute('data-y-coordinate');
        const status = location.getAttribute('data-status') || 'Libre';
        
        if (lotId && x && y) {
            createLotMarker(lotId, parseFloat(x), parseFloat(y), status);
        }
    });

    // Function to get status color
    function getStatusColor(status) {
        // Normalize status before determining color
        const normalizedStatus = normalizeLotStatus(status);

        switch(normalizedStatus) {
            case 'Libre':
                return 'green';
            case 'Apartado':
                return 'yellow';
            case 'Titulado':
                return 'red';
            default:
                return 'gray';
        }
    }

    // Function to create lot marker
    async function createLotMarker(lotId, x, y, status) {
        try {
            // Normalize status
            const normalizedStatus = normalizeLotStatus(status || 'Libre');

            // Get lot details
            const lotDetailsResponse = await fetch(`/api/lot/${lotId}`);
            
            // Check if response is ok
            if (!lotDetailsResponse.ok) {
                console.error(`Failed to fetch lot details for lot ${lotId}. Status: ${lotDetailsResponse.status}`);
                
                // Try to parse error details
                try {
                    const errorData = await lotDetailsResponse.json();
                    console.error('Error details:', errorData);
                } catch (parseError) {
                    console.error('Could not parse error response:', parseError);
                }
                
                // Use fallback marker with default status
                return createFallbackMarker(lotId, x, y, 'Libre');
            }

            const lotDetails = await lotDetailsResponse.json();

            // Determine marker color based on status
            const markerColor = getStatusColor(normalizedStatus);

            // Create marker element
            const marker = document.createElement('div');
            marker.className = `lot-marker ${markerColor}-marker`;
            marker.setAttribute('data-lot-id', lotId);
            marker.style.left = `${x}%`;
            marker.style.top = `${y}%`;

            // Add lot number to the marker
            const lotNumberSpan = document.createElement('span');
            lotNumberSpan.textContent = lotDetails.lote_numero || lotId;
            lotNumberSpan.style.color = 'white';
            lotNumberSpan.style.fontWeight = 'bold';
            lotNumberSpan.style.fontSize = '10px';
            lotNumberSpan.style.position = 'absolute';
            lotNumberSpan.style.top = '50%';
            lotNumberSpan.style.left = '50%';
            lotNumberSpan.style.transform = 'translate(-50%, -50%)';
            marker.appendChild(lotNumberSpan);

            // Add tooltip with lot details
            marker.title = `Lot ${lotDetails.lote_numero || lotId} - Status: ${normalizedStatus}`;

            // Add click event to show lot details
            marker.addEventListener('click', () => {
                populateLotDetailsModal(lotId);
            });

            // Debug logging
            console.group('Marker Creation Debug');
            console.log('Marker Element:', marker);
            console.log('Parent Container:', document.getElementById('lot-markers'));
            console.log('Marker Styles:', window.getComputedStyle(marker));
            console.log('Parent Container Styles:', window.getComputedStyle(document.getElementById('lot-markers')));
            console.groupEnd();

            // Add marker to the map
            const lotMarkers = document.getElementById('lot-markers');
            lotMarkers.appendChild(marker);

            return marker;
        } catch (error) {
            console.error(`Comprehensive error creating lot marker for lot ${lotId}:`, error);
            
            // Fallback to a basic marker with default status
            return createFallbackMarker(lotId, x, y, 'Libre');
        }
    }

    // Fallback marker creation function
    function createFallbackMarker(lotId, x, y, status) {
        // Normalize status
        const normalizedStatus = normalizeLotStatus(status || 'Libre');

        // Determine marker color based on status
        const markerColor = getStatusColor(normalizedStatus);

        // Create marker element
        const marker = document.createElement('div');
        marker.className = `lot-marker ${markerColor}-marker`;
        marker.setAttribute('data-lot-id', lotId);
        marker.style.left = `${x}%`;
        marker.style.top = `${y}%`;

        // Add lot number to the marker
        const lotNumberSpan = document.createElement('span');
        lotNumberSpan.textContent = lotId;
        lotNumberSpan.style.color = 'white';
        lotNumberSpan.style.fontWeight = 'bold';
        lotNumberSpan.style.fontSize = '10px';
        lotNumberSpan.style.position = 'absolute';
        lotNumberSpan.style.top = '50%';
        lotNumberSpan.style.left = '50%';
        lotNumberSpan.style.transform = 'translate(-50%, -50%)';
        marker.appendChild(lotNumberSpan);

        // Add tooltip with basic information
        marker.title = `Lot ${lotId} - Status: ${normalizedStatus}`;

        // Add marker to the map
        const lotMarkers = document.getElementById('lot-markers');
        lotMarkers.appendChild(marker);

        return marker;
    }

    // Debug function to help troubleshoot lot placement
    function debugLotPlacement(lotId, x, y, status) {
        console.group(`Lot Placement Debug - Lot ${lotId}`);
        console.log('Lot ID:', lotId);
        console.log('X Coordinate:', x);
        console.log('Y Coordinate:', y);
        console.log('Original Status:', status);
        
        const normalizedStatus = normalizeLotStatus(status || 'Libre');
        console.log('Normalized Status:', normalizedStatus);
        
        const markerColor = getStatusColor(normalizedStatus);
        console.log('Marker Color:', markerColor);
        
        console.groupEnd();
    }

    // Function to populate lot details modal using APIs
    async function populateLotDetailsModal(lotId) {
        try {
            // Fetch lot statuses, map location statuses, and lot details
            const [lotStatusResponse, mapLocationStatusResponse, lotDetailsResponse] = await Promise.all([
                fetch('/api/lot_statuses'),
                fetch('/api/map_location_statuses'),
                fetch(`/api/lot/${lotId}`)
            ]);

            const lotStatuses = await lotStatusResponse.json();
            const mapLocationStatuses = await mapLocationStatusResponse.json();
            const lotDetails = await lotDetailsResponse.json();

            // Find specific lot and map location status
            const lotStatus = lotStatuses.find(status => status.id === parseInt(lotId));
            const mapLocationStatus = mapLocationStatuses.find(location => location.lot_id === parseInt(lotId));

            // Find the existing lot location (if placed on map)
            const existingLotLocation = document.querySelector(`#existing-lots-list li[data-lot-id="${lotId}"]`);

            // Populate modal fields
            document.getElementById('lotModalId').textContent = lotId;
            document.getElementById('lotModalManzana').textContent = lotDetails.manzana || 'N/A';
            document.getElementById('lotModalLote').textContent = lotDetails.lote || 'N/A';
            document.getElementById('lotModalFraccionamiento').textContent = lotDetails.fraccionamiento || 'N/A';
            document.getElementById('lotModalPaquete').textContent = lotDetails.paquete || 'N/A';

            // Status information
            document.getElementById('lotModalOriginalStatus').textContent = lotStatus ? lotStatus.original_status : 'Unknown';
            document.getElementById('lotModalNormalizedStatus').textContent = lotStatus ? normalizeLotStatus(lotStatus.original_status) : 'Unknown';
            
            // Price and surface
            document.getElementById('lotModalPrice').textContent = lotDetails.precio ? `$${lotDetails.precio.toLocaleString()}` : 'N/A';
            document.getElementById('lotModalSurface').textContent = lotDetails.superficie ? `${lotDetails.superficie} m²` : 'N/A';

            // Map location details (if placed on map)
            if (existingLotLocation) {
                document.getElementById('lotModalXCoordinate').textContent = existingLotLocation.dataset.xCoordinate || 'N/A';
                document.getElementById('lotModalYCoordinate').textContent = existingLotLocation.dataset.yCoordinate || 'N/A';
                document.getElementById('lotModalMapLocationStatus').textContent = existingLotLocation.dataset.status || 'N/A';
            } else {
                document.getElementById('lotModalXCoordinate').textContent = 'Not placed on map';
                document.getElementById('lotModalYCoordinate').textContent = 'Not placed on map';
                document.getElementById('lotModalMapLocationStatus').textContent = 'Not placed on map';
            }

            // Show the modal
            const lotDetailsModal = new bootstrap.Modal(document.getElementById('lotDetailsModal'));
            lotDetailsModal.show();

        } catch (error) {
            console.error('Error populating lot details modal:', error);
            alert('Could not retrieve lot details. Please try again.');
        }
    }

    // Function to remove a lot from the map
    async function removeLotFromMap(lotId) {
        try {
            // Send request to backend to remove map location
            const response = await fetch(`/api/map-location/delete/${lotId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': await getCsrfToken()
                }
            });

            if (!response.ok) {
                throw new Error('Failed to remove lot from map');
            }

            const result = await response.json();

            // Remove marker from the map
            const marker = document.querySelector(`.lot-marker[data-lot-id="${lotId}"]`);
            if (marker) {
                marker.remove();
            }

            // Remove from existing lots list
            const lotListItem = document.querySelector(`#existing-lots-list li[data-lot-id="${lotId}"]`);
            if (lotListItem) {
                lotListItem.remove();
            }

            // Close the modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('lotDetailsModal'));
            modal.hide();

            // Optional: Show success message
            alert(result.message || 'Lot removed from map successfully');

            return true;
        } catch (error) {
            console.error('Error removing lot from map:', error);
            alert('Failed to remove lot from map. Please try again.');
            return false;
        }
    }

    // Add event listener for remove from map button
    document.addEventListener('DOMContentLoaded', () => {
        const removeLotButton = document.getElementById('remove-lot-from-map');
        
        if (!removeLotButton) {
            console.error('Remove lot button not found!');
            return;
        }

        console.log('Remove lot button found:', removeLotButton);
        
        removeLotButton.addEventListener('click', async () => {
            // Get the current lot ID from the modal
            const lotIdElement = document.getElementById('lotModalId');
            
            if (!lotIdElement) {
                console.error('Lot ID element not found!');
                return;
            }

            const lotId = lotIdElement.textContent;
            
            console.log('Attempting to remove lot:', lotId);
            
            if (lotId && lotId !== '-') {
                // Confirm before removal
                const confirmRemoval = confirm(`Are you sure you want to remove Lot ${lotId} from the map?`);
                
                if (confirmRemoval) {
                    await removeLotFromMap(lotId);
                }
            }
        });
    });

    // Add event listeners to existing lot list items
    document.addEventListener('DOMContentLoaded', () => {
        const existingLotItems = document.querySelectorAll('#existing-lots-list li');
        existingLotItems.forEach(item => {
            item.addEventListener('click', () => {
                const lotId = item.dataset.lotId;
                populateLotDetailsModal(lotId);
            });
        });
    });
});
