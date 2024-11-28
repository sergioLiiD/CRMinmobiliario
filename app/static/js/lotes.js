/**
 * Lotes management class
 * Handles all lot-related frontend functionality
 */
class LotesManager {
    constructor() {
        console.log('Initializing LotesManager');
        // Initialize state object first
        this.lastKnownState = {
            fraccionamiento: '',
            paquete: '',
            estado: ''
        };
        
        this.initializeElements();
        this.initializeEventListeners();
        this.initializeState();
        this.initializeLotDetailsListeners();
        this.initializeLotStatusChangeListeners();
        
        // Update state from URL parameters if they exist
        const urlParams = new URLSearchParams(window.location.search);
        this.lastKnownState.fraccionamiento = urlParams.get('fraccionamiento') || '';
        this.lastKnownState.paquete = urlParams.get('paquete') || '';
        this.lastKnownState.estado = urlParams.get('estado') || '';
    }

    /**
     * Initialize DOM elements
     */
    initializeElements() {
        console.log('Initializing elements');
        this.form = document.getElementById('filterForm');
        this.fraccionamientoSelect = document.getElementById('fraccionamiento');
        this.paqueteSelect = document.getElementById('paquete');
        this.estadoSelect = document.getElementById('estado');
        this.csrfToken = document.getElementById('csrf_token')?.value;

        if (!this.form) console.error('Form not found');
        if (!this.fraccionamientoSelect) console.error('Fraccionamiento select not found');
        if (!this.paqueteSelect) console.error('Paquete select not found');
        if (!this.estadoSelect) console.error('Estado select not found');
        if (!this.csrfToken) console.error('CSRF token not found');
    }

    /**
     * Initialize event listeners
     */
    initializeEventListeners() {
        console.log('Initializing event listeners');
        
        const fraccionamientoSelect = document.getElementById('fraccionamiento');
        if (fraccionamientoSelect) {
            fraccionamientoSelect.addEventListener('change', () => this.handleFraccionamientoChange());
        }
        
        const paqueteSelect = document.getElementById('paquete');
        if (paqueteSelect) {
            paqueteSelect.addEventListener('change', () => {
                document.getElementById('filterForm').submit();
            });
        }
        
        const estadoSelect = document.getElementById('estado');
        if (estadoSelect) {
            estadoSelect.addEventListener('change', () => {
                document.getElementById('filterForm').submit();
            });
        }
        
        // Event listeners for modal submit buttons
        const assignmentSubmitBtn = document.getElementById('submitAssignment');
        if (assignmentSubmitBtn) {
            assignmentSubmitBtn.addEventListener('click', () => this.submitAssignment());
        }
        
        const releaseSubmitBtn = document.getElementById('submitRelease');
        if (releaseSubmitBtn) {
            releaseSubmitBtn.addEventListener('click', () => this.submitRelease());
        }
    }

    /**
     * Initialize initial state
     */
    initializeState() {
        console.log('Initializing state');
        const fraccionamientoValue = this.fraccionamientoSelect?.value;
        console.log('Initial fraccionamiento value:', fraccionamientoValue);
        
        // Restore any saved state from URL parameters
        if (this.lastKnownState.fraccionamiento) {
            this.fraccionamientoSelect.value = this.lastKnownState.fraccionamiento;
        }
        
        if (fraccionamientoValue && fraccionamientoValue !== '0') {
            this.updatePaquetes(fraccionamientoValue, false).then(() => {
                // After paquetes are loaded, restore paquete selection if it exists
                if (this.lastKnownState.paquete) {
                    this.paqueteSelect.value = this.lastKnownState.paquete;
                }
            });
        } else {
            this.clearPaquetes();
        }
    }

    saveFormState() {
        this.lastKnownState = {
            fraccionamiento: this.fraccionamientoSelect?.value || '',
            paquete: this.paqueteSelect?.value || '',
            estado: this.estadoSelect?.value || ''
        };
        console.log('Saved form state:', this.lastKnownState);
    }

    restoreFormState() {
        if (this.fraccionamientoSelect && this.lastKnownState.fraccionamiento) {
            this.fraccionamientoSelect.value = this.lastKnownState.fraccionamiento;
        }
        if (this.paqueteSelect && this.lastKnownState.paquete) {
            this.paqueteSelect.value = this.lastKnownState.paquete;
        }
        if (this.estadoSelect && this.lastKnownState.estado) {
            this.estadoSelect.value = this.lastKnownState.estado;
        }
        console.log('Restored form state:', this.lastKnownState);
    }

    /**
     * Handle fraccionamiento change
     */
    async handleFraccionamientoChange() {
        const value = this.fraccionamientoSelect.value;
        console.log('Handling fraccionamiento change:', value);
        
        // Clear paquetes first
        this.clearPaquetes();
        
        if (value && value !== '0') {
            try {
                await this.updatePaquetes(value, false); // Changed to false to prevent auto-submission
            } catch (error) {
                console.error('Error updating paquetes:', error);
                this.showAlert('danger', 'Error al cargar los paquetes');
            }
        }
    }

    /**
     * Clear paquetes dropdown
     */
    clearPaquetes() {
        console.log('Clearing paquetes');
        if (this.paqueteSelect) {
            this.paqueteSelect.innerHTML = '<option value="0">Seleccione un paquete</option>';
            this.lastKnownState.paquete = '0';
        }
    }

    /**
     * Update paquetes based on selected fraccionamiento
     * @param {string} fraccionamientoId - Selected fraccionamiento ID
     * @param {boolean} submitForm - Whether to submit form after updating
     */
    async updatePaquetes(fraccionamientoId, submitForm = true) {
        if (!fraccionamientoId || fraccionamientoId === '0') {
            console.log('No valid fraccionamiento selected');
            this.clearPaquetes();
            return;
        }

        try {
            console.log('Fetching paquetes for fraccionamiento:', fraccionamientoId);
            const response = await fetch(`/properties/lotes/public?fraccionamiento_id=${fraccionamientoId}`);
            if (!response.ok) throw new Error('Failed to fetch paquetes');
            
            const data = await response.json();
            console.log('Received paquetes data:', data);
            
            if (this.paqueteSelect) {
                // Store current selection
                const currentPaquete = this.paqueteSelect.value;
                console.log('Current paquete selection:', currentPaquete);
                
                // Update options
                this.paqueteSelect.innerHTML = '<option value="0">Seleccione un paquete</option>';
                if (!data.paquetes) {
                    console.error('No paquetes array in response:', data);
                    return;
                }
                data.paquetes.forEach(paquete => {
                    console.log('Adding paquete option:', paquete);
                    const option = document.createElement('option');
                    option.value = paquete.id;
                    option.textContent = paquete.nombre;
                    this.paqueteSelect.appendChild(option);
                });
                
                // Restore previous selection if it exists in new options
                if (currentPaquete && currentPaquete !== '0' && 
                    Array.from(this.paqueteSelect.options).some(opt => opt.value === currentPaquete)) {
                    this.paqueteSelect.value = currentPaquete;
                }
                
                if (submitForm && this.paqueteSelect.value !== '0') {
                    this.form.submit();
                }
            }
        } catch (error) {
            console.error('Error updating paquetes:', error);
        }
    }

    /**
     * Update paquetes dropdown with new options
     * @param {Array} paquetes - Array of paquete options
     */
    updatePaquetesDropdown(paquetes) {
        if (!this.paqueteSelect) {
            console.error('Paquete select not found');
            return;
        }

        console.log('Updating paquetes dropdown with:', paquetes);
        this.paqueteSelect.innerHTML = '<option value="0">Todos los paquetes</option>';
        
        paquetes.forEach(([id, nombre]) => {
            const option = document.createElement('option');
            option.value = id;
            option.textContent = nombre;
            this.paqueteSelect.appendChild(option);
        });

        console.log('Updated paquetes dropdown HTML:', this.paqueteSelect.innerHTML);
    }

    /**
     * Show alert message
     * @param {string} type - Alert type (success, danger, etc.)
     * @param {string} message - Alert message
     */
    showAlert(type, message) {
        console.log('Showing alert:', type, message);
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;

        const container = document.querySelector('.container');
        if (container) {
            container.insertBefore(alertDiv, container.firstChild);
        } else {
            console.error('Container not found for alert');
        }

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }

    /**
     * Submit lot assignment
     */
    async submitAssignment() {
        console.log('Submitting assignment');
        const modal = document.getElementById('assignmentModal');
        if (!modal) return;
        
        const loteId = modal.querySelector('#assignmentLoteId').value;
        const clientId = modal.querySelector('#clientSelect').value;
        const notas = modal.querySelector('#assignmentNotas').value;
        
        if (!clientId) {
            this.showAlert('danger', 'Por favor seleccione un cliente');
            return;
        }
        
        try {
            const response = await fetch(`/properties/api/lotes/${loteId}/assign`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({
                    client_id: clientId,
                    notas: notas
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to assign lot');
            }
            
            // Hide modal and reload page
            const bsModal = bootstrap.Modal.getInstance(modal);
            bsModal.hide();
            window.location.reload();
            
        } catch (error) {
            console.error('Error assigning lot:', error);
            this.showAlert('danger', 'Error al apartar el lote');
        }
    }
    
    /**
     * Submit lot release
     */
    async submitRelease() {
        console.log('Submitting release');
        const modal = document.getElementById('releaseModal');
        if (!modal) return;
        
        const loteId = modal.querySelector('#releaseLoteId').value;
        const motivo = modal.querySelector('#releaseMotivo').value;
        const notas = modal.querySelector('#releaseNotas').value;
        
        if (!motivo) {
            this.showAlert('danger', 'Por favor indique el motivo de la cancelación');
            return;
        }
        
        try {
            const response = await fetch(`/properties/api/lotes/${loteId}/release`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({
                    motivo: motivo,
                    notas: notas
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to release lot');
            }
            
            // Hide modal and reload page
            const bsModal = bootstrap.Modal.getInstance(modal);
            bsModal.hide();
            window.location.reload();
            
        } catch (error) {
            console.error('Error releasing lot:', error);
            this.showAlert('danger', 'Error al cancelar el apartado');
        }
    }

    /**
     * Initialize lot details event listeners
     */
    initializeLotDetailsListeners() {
        const tableBody = document.querySelector('.table tbody');
        if (tableBody) {
            tableBody.addEventListener('click', (event) => {
                const detailsButton = event.target.closest('.lot-details-trigger');
                if (detailsButton) {
                    const loteRow = detailsButton.closest('tr');
                    const loteId = detailsButton.getAttribute('data-lote-id');
                    const existingDetailsRow = loteRow.nextElementSibling;

                    // If details row already exists, toggle its visibility
                    if (existingDetailsRow && existingDetailsRow.classList.contains('lot-details-row')) {
                        existingDetailsRow.remove();
                        return;
                    }

                    // Try multiple routes
                    const routes = [
                        `/lotes/${loteId}/details`,
                        `/properties/lotes/${loteId}/details`,
                        `/properties/lotes/public/${loteId}/details`
                    ];

                    const fetchLoteDetails = (routes) => {
                        if (routes.length === 0) {
                            throw new Error('No valid routes found');
                        }

                        const route = routes.shift();
                        console.log(`Attempting to fetch details from route: ${route}`);

                        return fetch(route, {
                            method: 'GET',
                            headers: {
                                'Content-Type': 'application/json',
                                'Accept': 'application/json',
                                'X-Requested-With': 'XMLHttpRequest'  // Add this for CSRF protection
                            },
                            credentials: 'same-origin'
                        })
                        .then(response => {
                            console.log('Full response:', {
                                status: response.status,
                                headers: Object.fromEntries(response.headers.entries()),
                                ok: response.ok,
                                type: response.type,
                                url: response.url
                            });

                            if (response.status === 401) {
                                window.location.href = '/auth/login';
                                throw new Error('Unauthorized');
                            }

                            if (!response.ok) {
                                if (routes.length > 0) {
                                    // Try next route if available
                                    return fetchLoteDetails(routes);
                                }
                                throw new Error('Network response was not ok');
                            }

                            return response.json();
                        });
                    };

                    fetchLoteDetails([...routes])
                        .then(data => {
                            console.log('Lot details received:', data);

                            // Create details row
                            const detailsRow = document.createElement('tr');
                            detailsRow.classList.add('lot-details-row', 'bg-light');
                            
                            // Prepare details HTML
                            const detailsHTML = `
                                <td colspan="8">
                                    <div class="container-fluid p-3">
                                        <div class="row">
                                            <div class="col-md-6">
                                                <h6>Información del Lote</h6>
                                                <p><strong>Manzana:</strong> ${data.manzana || 'N/A'}</p>
                                                <p><strong>Lote:</strong> ${data.lote || 'N/A'}</p>
                                                <p><strong>Superficie:</strong> ${data.terreno || 'N/A'} m²</p>
                                                <p><strong>Precio:</strong> $${data.precio ? data.precio.toLocaleString() : 'N/A'}</p>
                                                <p><strong>Estado:</strong> ${data.estado_del_inmueble || data.estado || 'N/A'}</p>
                                                <p><strong>Tipo:</strong> ${data.tipo_de_lote || 'N/A'}</p>
                                            </div>
                                            <div class="col-md-6">
                                                ${data.prototipo ? `
                                                    <h6>Información del Prototipo</h6>
                                                    <p><strong>Nombre:</strong> ${data.prototipo.nombre_prototipo || data.prototipo || 'N/A'}</p>
                                                    <p><strong>Superficie de Construcción:</strong> ${data.prototipo.superficie_construccion || 'N/A'} m²</p>
                                                ` : ''}
                                                
                                                ${data.asignacion && data.asignacion.client ? `
                                                    <h6>Información del Cliente</h6>
                                                    <p><strong>Nombre:</strong> ${data.asignacion.client.nombre_completo || 'N/A'}</p>
                                                    <p><strong>Celular:</strong> ${data.asignacion.client.celular || 'N/A'}</p>
                                                    <p><strong>Email:</strong> ${data.asignacion.client.email || 'N/A'}</p>
                                                ` : ''}
                                            </div>
                                        </div>
                                    </div>
                                </td>
                            `;
                            
                            detailsRow.innerHTML = detailsHTML;
                            
                            // Insert the details row after the current row
                            loteRow.insertAdjacentElement('afterend', detailsRow);
                        })
                        .catch(error => {
                            console.error('Error fetching lot details:', error);
                            console.error('Full error object:', error);
                            
                            if (error.message !== 'Unauthorized') {
                                alert(`No se pudieron cargar los detalles del lote: ${error.message}`);
                            }
                        });
                }
            });
        }
    }

    initializeLotStatusChangeListeners() {
        const tableBody = document.querySelector('.table tbody');
        if (tableBody) {
            tableBody.addEventListener('click', (event) => {
                const statusChangeButton = event.target.closest('.lot-status-change-trigger');
                if (statusChangeButton) {
                    const loteRow = statusChangeButton.closest('tr');
                    const loteId = statusChangeButton.getAttribute('data-lote-id');
                    const currentStatus = statusChangeButton.getAttribute('data-current-status');

                    // Create modal dynamically
                    const modalHtml = `
                        <div class="modal fade" id="lotStatusChangeModal" tabindex="-1">
                            <div class="modal-dialog">
                                <div class="modal-content">
                                    <div class="modal-header">
                                        <h5 class="modal-title">Cambiar Estado del Lote</h5>
                                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                                    </div>
                                    <div class="modal-body">
                                        <p>Estado actual: <strong>${currentStatus}</strong></p>
                                        <div class="mb-3">
                                            <label for="newStatus" class="form-label">Nuevo Estado</label>
                                            <select id="newStatus" class="form-select">
                                                ${this.getValidStatusOptions(currentStatus)}
                                            </select>
                                        </div>
                                        <div id="reasonSection" class="mb-3" style="display:none;">
                                            <label for="changeReason" class="form-label">Motivo del Cambio</label>
                                            <textarea id="changeReason" class="form-control" rows="3" placeholder="Explique el motivo del cambio de estado"></textarea>
                                        </div>
                                    </div>
                                    <div class="modal-footer">
                                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                                        <button type="button" class="btn btn-primary" id="confirmStatusChange">Confirmar</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;

                    // Remove any existing modal
                    const existingModal = document.getElementById('lotStatusChangeModal');
                    if (existingModal) existingModal.remove();

                    // Add modal to body
                    document.body.insertAdjacentHTML('beforeend', modalHtml);

                    // Initialize Bootstrap modal
                    const statusChangeModal = new bootstrap.Modal(document.getElementById('lotStatusChangeModal'));
                    statusChangeModal.show();

                    // New status select listener
                    const newStatusSelect = document.getElementById('newStatus');
                    const reasonSection = document.getElementById('reasonSection');
                    const changeReasonTextarea = document.getElementById('changeReason');

                    newStatusSelect.addEventListener('change', () => {
                        const selectedStatus = newStatusSelect.value;
                        
                        // Show reason section only when changing from Titulado to Apartado
                        if (currentStatus === 'Titulado' && selectedStatus === 'Apartado') {
                            reasonSection.style.display = 'block';
                            changeReasonTextarea.required = true;
                        } else {
                            reasonSection.style.display = 'none';
                            changeReasonTextarea.required = false;
                        }
                    });

                    // Confirm status change
                    const confirmButton = document.getElementById('confirmStatusChange');
                    confirmButton.addEventListener('click', () => {
                        const newStatus = newStatusSelect.value;
                        const reason = changeReasonTextarea.value || '';

                        // Validate reason for certain status changes
                        if ((currentStatus === 'Titulado' && newStatus === 'Apartado') && 
                            (!reason || reason.trim() === '')) {
                            alert('Por favor, proporcione un motivo para cambiar de Titulado a Apartado.');
                            return;
                        }

                        // Get CSRF token
                        const csrfToken = document.querySelector('meta[name="csrf-token"]');
                        
                        // Prepare headers
                        const headers = {
                            'Content-Type': 'application/json',
                            'X-Requested-With': 'XMLHttpRequest'
                        };
                        
                        // Add CSRF token if available
                        if (csrfToken) {
                            headers['X-CSRFToken'] = csrfToken.getAttribute('content');
                        }

                        // Send status change request
                        fetch(`/properties/lotes/${loteId}/change_status`, {
                            method: 'POST',
                            headers: headers,
                            credentials: 'same-origin',
                            body: JSON.stringify({
                                new_status: newStatus,
                                reason: reason
                            })
                        })
                        .then(response => {
                            console.log('Response status:', response.status);
                            console.log('Response headers:', response.headers);
                            
                            // Check if response is a redirect (login page)
                            if (response.redirected) {
                                console.error('Redirected to login page');
                                throw new Error('No estás autenticado. Por favor, inicia sesión.');
                            }
                            
                            // Check response content type
                            const contentType = response.headers.get('content-type');
                            if (!contentType || !contentType.includes('application/json')) {
                                return response.text().then(text => {
                                    console.error('Non-JSON response:', text);
                                    throw new Error('Respuesta del servidor no es JSON');
                                });
                            }
                            
                            return response.json();
                        })
                        .then(data => {
                            // Check for error in the response
                            if (data.error) {
                                throw new Error(data.error);
                            }

                            // Update status in the table
                            const statusCell = loteRow.querySelector('.lot-status');
                            if (statusCell) {
                                statusCell.textContent = newStatus;
                                statusCell.className = `lot-status ${this.getStatusClass(newStatus)}`;
                            }

                            // Update status change button
                            const statusChangeButton = loteRow.querySelector('.lot-status-change-trigger');
                            if (statusChangeButton) {
                                statusChangeButton.setAttribute('data-current-status', newStatus);
                            }

                            // Close modal
                            statusChangeModal.hide();
                            
                            // Show success message
                            this.showToast('Estado del lote actualizado', 'success');
                        })
                        .catch(error => {
                            console.error('Error details:', error);
                            console.error('Full error object:', error);
                            let errorMessage = 'No se pudo cambiar el estado del lote';
                            if (error.message) {
                                errorMessage = error.message;
                            }
                            if (error.response) {
                                console.error('Error response:', error.response);
                                if (error.response.status === 400) {
                                    errorMessage = 'Error en la solicitud';
                                } else if (error.response.status === 401) {
                                    errorMessage = 'No estás autenticado';
                                } else if (error.response.status === 403) {
                                    errorMessage = 'No tienes permiso para realizar esta acción';
                                } else if (error.response.status === 500) {
                                    errorMessage = 'Error en el servidor';
                                }
                            }
                            this.showToast(errorMessage, 'danger');
                        });
                    });
                }
            });
        }
    }

    getValidStatusOptions(currentStatus) {
        const statusOptions = {
            'Libre': ['Apartado'],
            'Apartado': ['Libre', 'Titulado'],
            'Titulado': ['Libre', 'Apartado']
        };

        return statusOptions[currentStatus]
            .map(status => `<option value="${status}">${status}</option>`)
            .join('');
    }

    getStatusClass(status) {
        switch(status) {
            case 'Libre':
                return 'badge bg-success';
            case 'Apartado':
                return 'badge bg-warning';
            case 'Titulado':
                return 'badge bg-danger';  // Changed to red
            default:
                return 'badge bg-secondary';
        }
    }

    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toastContainer') || this.createToastContainer();
        const toastHtml = `
            <div class="toast align-items-center text-bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">${message}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;
        toastContainer.innerHTML = toastHtml;
        const toast = new bootstrap.Toast(toastContainer.querySelector('.toast'));
        toast.show();
    }

    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(container);
        return container;
    }

    /**
     * Initialize on page load
     */
    init() {
        console.log('DOM loaded, initializing LotesManager');
        this.restoreFormState();
    }
}

// Create a global instance of LotesManager
document.addEventListener('DOMContentLoaded', function() {
    try {
        window.lotesManager = new LotesManager();
        console.log('LotesManager initialized successfully');
    } catch (error) {
        console.error('Failed to initialize LotesManager:', error);
    }
});
