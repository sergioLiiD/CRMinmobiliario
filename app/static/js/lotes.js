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
        this.initializeClientAssignmentListeners();
        this.initializeStatusChangeModal();
        
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
        
        this.initializeLotStatusChangeListeners();
        this.initializeClientAssignmentListeners();
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
                    'X-CSRFToken': this.getCsrfToken()
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
            const bsModal = window.bootstrap.Modal.getInstance(modal);
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
                    'X-CSRFToken': this.getCsrfToken()
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
            const bsModal = window.bootstrap.Modal.getInstance(modal);
            bsModal.hide();
            window.location.reload();
            
        } catch (error) {
            console.error('Error releasing lot:', error);
            this.showAlert('danger', 'Error al cancelar el apartado');
        }
    }

    initializeLotDetailsListeners() {
        console.group('🔍 Initializing Lot Details Listeners');
        console.log('Document Ready State:', document.readyState);
        
        // Comprehensive button detection and logging
        const detailsButtons = document.querySelectorAll('.lot-details-trigger, .details-btn');
        console.log('Details Buttons Found:', detailsButtons.length);
        
        detailsButtons.forEach((button, index) => {
            console.log(`Button ${index}:`, {
                classList: button.classList.toString(),
                dataLoteId: button.getAttribute('data-lote-id'),
                innerText: button.innerText.trim(),
                parentElement: button.parentElement ? button.parentElement.tagName : 'No Parent'
            });
            
            // Add direct click listener to each button
            button.addEventListener('click', (event) => {
                event.preventDefault();
                event.stopPropagation();
                
                console.log('🎯 Details Button Clicked', {
                    target: event.target,
                    currentTarget: event.currentTarget,
                    loteId: button.getAttribute('data-lote-id')
                });
                
                const loteId = button.getAttribute('data-lote-id');
                
                if (!loteId) {
                    console.error('❌ No Lote ID found on button');
                    this.showAlert('danger', 'Error: No se pudo identificar el lote');
                    return;
                }
                
                this.fetchLoteDetails({
                    loteId,
                    onSuccess: (data) => {
                        console.log('✅ Lot Details Received:', data);
                        
                        // Create modal HTML
                        const modalHtml = `
                        <div class="modal fade" id="lotDetailsModal" tabindex="-1" aria-labelledby="lotDetailsModalLabel" aria-hidden="true">
                            <div class="modal-dialog modal-lg">
                                <div class="modal-content">
                                    <div class="modal-header">
                                        <h5 class="modal-title" id="lotDetailsModalLabel">Detalles del Lote</h5>
                                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                    </div>
                                    <div class="modal-body">
                                        <div class="row">
                                            <div class="col-md-6">
                                                <h6>Información del Lote</h6>
                                                <p><strong>Fraccionamiento:</strong> ${data.fraccionamiento || 'N/A'}</p>
                                                <p><strong>Paquete:</strong> ${data.paquete || 'N/A'}</p>
                                                <p><strong>Lote:</strong> ${data.lote || 'N/A'}</p>
                                                <p><strong>Manzana:</strong> ${data.manzana || 'N/A'}</p>
                                                <p><strong>Calle:</strong> ${data.calle || 'N/A'}</p>
                                                <p><strong>Número Exterior:</strong> ${data.numero_exterior || 'N/A'}</p>
                                                <p><strong>Número Interior:</strong> ${data.numero_interior || 'N/A'}</p>
                                                <p><strong>Estado:</strong> ${data.estado || 'N/A'}</p>
                                            </div>
                                            <div class="col-md-6">
                                                <h6>Detalles Adicionales</h6>
                                                <p><strong>Prototipo:</strong> ${data.prototipo || 'N/A'}</p>
                                                <p><strong>Terreno:</strong> ${data.terreno ? data.terreno + ' m²' : 'N/A'}</p>
                                                <p><strong>Precio:</strong> $${data.precio ? data.precio.toLocaleString() : 'N/A'}</p>
                                                
                                                ${data.asignacion ? `
                                                    <h6>Información de Asignación</h6>
                                                    <p><strong>Cliente:</strong> ${data.asignacion.client.nombre_completo || 'N/A'}</p>
                                                    <p><strong>Email:</strong> ${data.asignacion.client.email || 'N/A'}</p>
                                                    <p><strong>Celular:</strong> ${data.asignacion.client.celular || 'N/A'}</p>
                                                    <p><strong>Estado de Asignación:</strong> ${data.asignacion.estado || 'N/A'}</p>
                                                    <p><strong>Fecha de Asignación:</strong> ${data.asignacion.fecha_asignacion ? 
                                                        new Date(data.asignacion.fecha_asignacion).toLocaleDateString() : 'N/A'}</p>
                                                ` : ''}
                                            </div>
                                        </div>
                                    </div>
                                    <div class="modal-footer">
                                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                                    </div>
                                </div>
                            </div>
                        </div>`;
                        
                        // Remove existing modal if it exists
                        const existingModal = document.getElementById('lotDetailsModal');
                        if (existingModal) {
                            existingModal.remove();
                        }
                        
                        // Insert modal HTML
                        document.body.insertAdjacentHTML('beforeend', modalHtml);
                        
                        // Get modal element
                        const lotDetailsModal = document.getElementById('lotDetailsModal');
                        
                        // Show modal with multiple initialization strategies
                        try {
                            // Ensure modal is fully in the DOM before initialization
                            setTimeout(() => {
                                console.log('🎬 Attempting to show modal');
                                this.showModalWithFallback(lotDetailsModal);
                            }, 50);
                        } catch (modalError) {
                            console.error('❌ Error showing modal:', modalError);
                            
                            // Fallback manual display method
                            lotDetailsModal.style.display = 'block';
                            lotDetailsModal.classList.add('show');
                            document.body.classList.add('modal-open');
                            
                            const backdrop = document.createElement('div');
                            backdrop.classList.add('modal-backdrop', 'fade', 'show');
                            document.body.appendChild(backdrop);
                        }
                        
                        console.log('Modal Shown Successfully');
                    },
                    onError: (error) => {
                        console.error('❌ Error fetching lot details:', error);
                        this.showAlert('danger', 'No se pudieron cargar los detalles del lote');
                    }
                });
            });
        });
        
        console.groupEnd();
    }

    initializeLotStatusChangeListeners() {
        document.addEventListener('click', (event) => {
            const statusChangeButton = event.target.closest('.lot-status-change-trigger');
            if (statusChangeButton) {
                const loteId = statusChangeButton.dataset.loteId;
                const currentStatus = statusChangeButton.dataset.currentStatus;
                
                console.group(' Lot Status Change Initialization');
                console.log('Button Details:', {
                    loteId, 
                    currentStatus, 
                    buttonElement: statusChangeButton
                });
                
                // Fetch lot details before opening the modal
                this.fetchLoteDetails({
                    loteId: loteId,
                    onSuccess: (data) => {
                        console.log('Lot Details Fetched:', data);
                        
                        // Create or get the status change modal
                        let statusChangeModal = document.getElementById('statusChangeModal');
                        if (!statusChangeModal) {
                            console.log('Creating new modal element');
                            const modalHtml = `
                            <div class="modal fade" id="statusChangeModal" tabindex="-1" role="dialog" aria-labelledby="statusChangeModalLabel" aria-hidden="true">
                                <div class="modal-dialog" role="document">
                                    <div class="modal-content">
                                        <div class="modal-header">
                                            <h5 class="modal-title" id="statusChangeModalLabel">Cambiar Estado del Lote</h5>
                                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                        </div>
                                        <div class="modal-body">
                                            <div class="mb-3">
                                                <label class="form-label">Estado Actual:</label>
                                                <p id="currentStatus" class="form-control-plaintext"></p>
                                            </div>
                                            <div id="clientInfoSection" class="mb-3" style="display:none;">
                                                <h6>Cliente Asignado</h6>
                                                <div id="clientInfoContent"></div>
                                            </div>
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
                            </div>`;
                            
                            document.body.insertAdjacentHTML('beforeend', modalHtml);
                            statusChangeModal = document.getElementById('statusChangeModal');
                        }
                        
                        // Store original trigger data on the modal
                        statusChangeModal.dataset.originalLoteId = loteId;
                        statusChangeModal.dataset.originalCurrentStatus = currentStatus;
                        
                        // Populate current status
                        const currentStatusElement = statusChangeModal.querySelector('#currentStatus');
                        if (currentStatusElement) {
                            currentStatusElement.textContent = currentStatus;
                        }
                        
                        // Populate client information if available
                        const clientInfoSection = statusChangeModal.querySelector('#clientInfoSection');
                        const clientInfoContent = statusChangeModal.querySelector('#clientInfoContent');
                        
                        if (clientInfoSection && clientInfoContent && data.asignacion?.client) {
                            const client = data.asignacion.client;
                            const assignmentEstado = data.asignacion.estado || 'N/A';
                            const assignmentFecha = data.asignacion.fecha_asignacion ? 
                                new Date(data.asignacion.fecha_asignacion).toLocaleDateString() : 'N/A';
                            
                            clientInfoContent.innerHTML = `
                                <p><strong>Nombre:</strong> ${client.nombre_completo || 'N/A'}</p>
                                <p><strong>Email:</strong> ${client.email || 'N/A'}</p>
                                <p><strong>Celular:</strong> ${client.celular || 'N/A'}</p>
                                <p><strong>Estado de Asignación:</strong> ${assignmentEstado}</p>
                                <p><strong>Fecha de Asignación:</strong> ${assignmentFecha}</p>
                            `;
                            clientInfoSection.style.display = 'block';
                        } else {
                            clientInfoSection.style.display = 'none';
                        }
                        
                        // Populate new status options
                        const newStatusSelect = statusChangeModal.querySelector('#newStatus');
                        if (newStatusSelect) {
                            newStatusSelect.innerHTML = this.getValidStatusOptions(currentStatus);
                        }
                        
                        // Add event listener for Confirmar button
                        const confirmButton = statusChangeModal.querySelector('#confirmStatusChange');
                        if (confirmButton) {
                            confirmButton.addEventListener('click', () => {
                                const newStatus = newStatusSelect.value;
                                const changeReason = statusChangeModal.querySelector('#changeReason')?.value || '';
                                
                                console.log('Status Change Confirmation:', {
                                    loteId,
                                    currentStatus,
                                    newStatus,
                                    changeReason
                                });
                                
                                // Call method to submit status change
                                this.submitStatusChange(loteId, newStatus, changeReason);
                            });
                        }
                        
                        // Detailed Modal Initialization Debugging
                        console.log('Modal Element:', statusChangeModal);
                        
                        // Fallback modal initialization
                        try {
                            // Ensure modal is fully in the DOM before initialization
                            setTimeout(() => {
                                console.log('🎬 Attempting to show modal');
                                this.showModalWithFallback(statusChangeModal);
                            }, 50);
                        } catch (modalError) {
                            console.error('❌ Error showing modal:', modalError);
                            
                            // Fallback manual display method
                            statusChangeModal.style.display = 'block';
                            statusChangeModal.classList.add('show');
                            document.body.classList.add('modal-open');
                            
                            const backdrop = document.createElement('div');
                            backdrop.classList.add('modal-backdrop', 'fade', 'show');
                            document.body.appendChild(backdrop);
                        }
                        
                        console.log('Modal Shown Successfully');
                    },
                    onError: (error) => {
                        console.error('Error fetching lot details:', error);
                        this.showAlert('danger', 'No se pudieron cargar los detalles del lote');
                    }
                });
            }
            
            console.groupEnd();
        });
    }

    initializeClientAssignmentListeners() {
        console.log('Initializing client assignment listeners');
        
        // Assign client button listeners for both index and public pages
        const assignClientButtons = document.querySelectorAll('.assign-client-btn');
        assignClientButtons.forEach(button => {
            button.addEventListener('click', (e) => this.prepareClientAssignment(e.currentTarget.getAttribute('data-lote-id')));
        });

        // Client search button listener
        const searchClientBtn = document.getElementById('searchClientBtn');
        if (searchClientBtn) {
            searchClientBtn.addEventListener('click', () => this.searchClients());
        }

        // Client search input listener for debounce
        const clientSearchInput = document.getElementById('clientSearch');
        if (clientSearchInput) {
            let searchTimeout;
            clientSearchInput.addEventListener('input', () => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => this.searchClients(), 300);
            });
        }

        // Confirm assignment button listener
        const confirmAssignmentBtn = document.getElementById('confirmAssignmentBtn');
        if (confirmAssignmentBtn) {
            confirmAssignmentBtn.addEventListener('click', () => this.submitClientAssignment());
        }
    }

    async searchClients() {
        const clientSearchInput = document.getElementById('clientSearch');
        const clientSearchResults = document.getElementById('clientSearchResults');
        const searchTerm = clientSearchInput.value.trim();

        console.group('Client Search Debug');
        console.log('Search Term:', searchTerm);
        console.log('CSRF Token:', this.getCsrfToken());

        // Clear previous results
        clientSearchResults.innerHTML = '';

        // Validate search term
        if (searchTerm.length < 2) {
            console.warn('Search term too short');
            clientSearchResults.innerHTML = '<div class="list-group-item">Ingrese al menos 2 caracteres</div>';
            console.groupEnd();
            return;
        }

        try {
            const response = await fetch(`/properties/clients/search?q=${encodeURIComponent(searchTerm)}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken(),
                    'Accept': 'application/json'
                },
                credentials: 'same-origin'  // Ensure cookies are sent
            });

            console.log('Fetch Response:', {
                status: response.status,
                statusText: response.statusText
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Search error response:', errorText);
                throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
            }

            const clients = await response.json();
            console.log('Clients Received:', clients);

            // Validate response
            if (!Array.isArray(clients)) {
                console.error('Invalid response format:', clients);
                clientSearchResults.innerHTML = '<div class="list-group-item text-danger">Error en el formato de respuesta</div>';
                console.groupEnd();
                return;
            }

            if (clients.length === 0) {
                console.warn('No clients found');
                clientSearchResults.innerHTML = '<div class="list-group-item">No se encontraron clientes</div>';
                console.groupEnd();
                return;
            }

            // Populate results
            clients.forEach(client => {
                const clientItem = document.createElement('div');
                clientItem.classList.add('list-group-item', 'list-group-item-action');
                clientItem.innerHTML = `
                    <div class="d-flex w-100 justify-content-between">
                        <h5 class="mb-1">${client.nombre_completo}</h5>
                    </div>
                    <p class="mb-1">
                        <small>
                            ${client.email ? `Email: ${client.email}<br>` : ''}
                            Celular: ${client.celular}
                        </small>
                    </p>
                `;
                clientItem.addEventListener('click', () => this.selectClient(client));
                clientSearchResults.appendChild(clientItem);
            });

            console.log('Search completed successfully');
            console.groupEnd();
        } catch (error) {
            // Catch any network or parsing errors
            console.error('Comprehensive Error:', {
                name: error.name,
                message: error.message,
                stack: error.stack
            });
            
            clientSearchResults.innerHTML = `<div class="list-group-item text-danger">Error: ${error.message}</div>`;
            console.groupEnd();
        }
    }

    selectClient(client) {
        const selectedClientInfo = document.getElementById('selectedClientInfo');
        const selectedClientDetails = document.getElementById('selectedClientDetails');
        const selectedClientId = document.getElementById('selectedClientId');

        // Update selected client details
        selectedClientDetails.innerHTML = `
            <strong>Nombre:</strong> ${client.nombre_completo}<br>
            ${client.email ? `<strong>Email:</strong> ${client.email}<br>` : ''}
            <strong>Celular:</strong> ${client.celular}
        `;

        // Set client ID
        selectedClientId.value = client.id;

        // Show selected client info
        selectedClientInfo.classList.remove('d-none');

        // Clear search results
        const clientSearchResults = document.getElementById('clientSearchResults');
        clientSearchResults.innerHTML = '';
    }

    async submitClientAssignment() {
        const assignLoteIdInput = document.getElementById('assignLoteId');
        const selectedClientId = document.getElementById('selectedClientId');
        const assignmentNotes = document.getElementById('assignmentNotes');

        // Validate inputs
        if (!assignLoteIdInput.value || !selectedClientId.value) {
            this.showAlert('danger', 'Por favor seleccione un cliente');
            return;
        }

        try {
            const response = await fetch(`/properties/lotes/${assignLoteIdInput.value}/assign-client`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    client_id: selectedClientId.value,
                    notes: assignmentNotes.value || ''
                })
            });

            // Check if response is not OK
            if (!response.ok) {
                // Try to parse error message from response
                let errorMessage = 'Error al asignar cliente';
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.error || errorMessage;
                } catch {
                    // If parsing fails, use default error or status text
                    errorMessage = `Error ${response.status}: ${response.statusText}`;
                }
                
                // Log the full error for debugging
                console.error('Assignment error:', {
                    status: response.status,
                    statusText: response.statusText,
                    errorMessage: errorMessage
                });

                // Show error to user
                this.showAlert('danger', errorMessage);
                return;
            }

            // Parse successful response
            const data = await response.json();
            
            // Show success message
            this.showAlert('success', data.message || 'Cliente asignado exitosamente');

            // Close the modal
            const assignClientModal = window.bootstrap.Modal.getInstance(document.getElementById('assignClientModal'));
            if (assignClientModal) {
                assignClientModal.hide();
            }

            // Optional: Refresh the page or update UI
            location.reload();

        } catch (error) {
            // Catch any network or parsing errors
            console.error('Comprehensive assignment error:', {
                name: error.name,
                message: error.message,
                stack: error.stack
            });
            
            this.showAlert('danger', 'Error de red o procesamiento. Intente nuevamente.');
        }
    }
    
    prepareClientAssignment(loteId) {
        console.log('Preparing client assignment for lote:', loteId);
        
        // Reset modal state
        const assignLoteIdInput = document.getElementById('assignLoteId');
        const clientSearchInput = document.getElementById('clientSearch');
        const clientSearchResults = document.getElementById('clientSearchResults');
        const selectedClientInfo = document.getElementById('selectedClientInfo');
        const selectedClientDetails = document.getElementById('selectedClientDetails');
        const selectedClientId = document.getElementById('selectedClientId');
        const assignmentNotes = document.getElementById('assignmentNotes');

        // Set lote ID
        assignLoteIdInput.value = loteId;

        // Clear previous results
        clientSearchInput.value = '';
        clientSearchResults.innerHTML = '';
        selectedClientInfo.classList.add('d-none');
        selectedClientDetails.innerHTML = '';
        selectedClientId.value = '';
        assignmentNotes.value = '';

        // Show the modal
        const assignClientModal = new window.bootstrap.Modal(document.getElementById('assignClientModal'));
        assignClientModal.show();
    }

    initializeStatusChangeModal() {
        console.log('Initializing status change modal...');
        
        // Ensure the modal exists in the DOM
        let statusChangeModal = document.getElementById('statusChangeModal');
        if (!statusChangeModal) {
            console.error('Status change modal not found in the DOM. Creating it...');
            
            // Create the modal HTML if it doesn't exist
            const modalHtml = `
            <div class="modal fade" id="statusChangeModal" tabindex="-1" aria-labelledby="statusChangeModalLabel" aria-hidden="true">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="statusChangeModalLabel">Cambiar Estado del Lote</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <div class="mb-3">
                                <label class="form-label">Estado Actual:</label>
                                <p id="currentStatus" class="form-control-plaintext"></p>
                            </div>
                            <div id="clientInfoSection" class="mb-3" style="display:none;">
                                <h6>Cliente Asignado</h6>
                                <div id="clientInfoContent"></div>
                            </div>
                            <div class="mb-3">
                                <label for="newStatus" class="form-label">Nuevo Estado</label>
                                <select id="newStatus" class="form-select">
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
            </div>`;
            
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            statusChangeModal = document.getElementById('statusChangeModal');
        }

        // Add event listener for modal show event
        statusChangeModal.addEventListener('show.bs.modal', (event) => {
            console.log('Status change modal show event triggered');
            
            // Get the triggering button
            const button = event.relatedTarget;
            if (!button) {
                console.error('No button found triggering the modal');
                return;
            }
            
            // Extract data attributes from the button
            const loteId = button.getAttribute('data-lote-id');
            const currentStatus = button.getAttribute('data-current-status');
            
            console.log('Modal triggered with:', {
                loteId: loteId,
                currentStatus: currentStatus
            });

            // Fetch lot details to populate modal
            this.fetchLoteDetails({
                loteId: loteId,
                onSuccess: (data) => {
                    console.log('Lot details received:', data);
                    
                    // Populate current status
                    const currentStatusElement = statusChangeModal.querySelector('#currentStatus');
                    if (currentStatusElement) {
                        currentStatusElement.textContent = currentStatus;
                    }

                    // Populate client information if available
                    const clientInfoSection = statusChangeModal.querySelector('#clientInfoSection');
                    const clientInfoContent = statusChangeModal.querySelector('#clientInfoContent');
                    
                    // Debug logging for client data
                    console.log('Asignacion data:', data.asignacion);
                    console.log('Client data:', data.asignacion?.client);
                    
                    if (clientInfoSection && clientInfoContent && data.asignacion?.client) {
                        const client = data.asignacion.client;
                        const assignmentEstado = data.asignacion.estado || 'N/A';
                        const assignmentFecha = data.asignacion.fecha_asignacion ? 
                            new Date(data.asignacion.fecha_asignacion).toLocaleDateString() : 'N/A';
                        
                        clientInfoContent.innerHTML = `
                            <p><strong>Nombre:</strong> ${client.nombre_completo || 'N/A'}</p>
                            <p><strong>Email:</strong> ${client.email || 'N/A'}</p>
                            <p><strong>Celular:</strong> ${client.celular || 'N/A'}</p>
                            <p><strong>Estado Asignación:</strong> ${assignmentEstado}</p>
                            <p><strong>Fecha Asignación:</strong> ${assignmentFecha}</p>
                        `;
                        clientInfoSection.style.display = 'block';
                    } else {
                        clientInfoSection.style.display = 'none';
                        console.log('No client information available');
                    }

                    // Populate new status options
                    const newStatusSelect = statusChangeModal.querySelector('#newStatus');
                    if (newStatusSelect) {
                        newStatusSelect.innerHTML = this.getValidStatusOptions(currentStatus);
                    }
                },
                onError: (error) => {
                    console.error('Error fetching lot details:', error);
                }
            });
        });
        
        // Add event listener to modal to reload page when closed
        statusChangeModal.addEventListener('hidden.bs.modal', () => {
            location.reload();
        });
    }

    showModalWithFallback(modalElement) {
        console.group('🚀 Modal Initialization Attempt');
        console.log('Modal Element:', modalElement);
        
        const modalInitializationMethods = [
            // Method 1: Modern Bootstrap 5 initialization
            () => {
                console.log('🔹 Attempting Bootstrap 5 Modal Initialization');
                if (window.bootstrap && window.bootstrap.Modal) {
                    const modalInstance = new window.bootstrap.Modal(modalElement);
                    modalInstance.show();
                    return true;
                }
                return false;
            },
            
            // Method 2: Alternative Bootstrap initialization
            () => {
                console.log('🔹 Attempting Alternative Bootstrap Modal Initialization');
                if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                    const modalInstance = new bootstrap.Modal(modalElement);
                    modalInstance.show();
                    return true;
                }
                return false;
            },
            
            // Method 3: Manual modal display
            () => {
                console.log('🔹 Attempting Manual Modal Display');
                // Manually show the modal
                modalElement.style.display = 'block';
                modalElement.classList.add('show');
                document.body.classList.add('modal-open');
                
                // Create backdrop
                const backdrop = document.createElement('div');
                backdrop.classList.add('modal-backdrop', 'fade', 'show');
                document.body.appendChild(backdrop);
                
                // Add close functionality
                const closeButtons = modalElement.querySelectorAll('[data-bs-dismiss="modal"]');
                closeButtons.forEach(button => {
                    button.addEventListener('click', () => {
                        modalElement.style.display = 'none';
                        modalElement.classList.remove('show');
                        document.body.classList.remove('modal-open');
                        backdrop.remove();
                    });
                });
                
                return true;
            }
        ];
        
        // Try each initialization method
        for (const method of modalInitializationMethods) {
            try {
                if (method()) {
                    console.log('✅ Modal Successfully Displayed');
                    console.groupEnd();
                    return true;
                }
            } catch (error) {
                console.warn('❌ Modal Initialization Method Failed:', error);
            }
        }
        
        console.error('❌ All Modal Initialization Methods Failed');
        console.groupEnd();
        return false;
    }

    initializeLotStatusChangeModal(modalElement) {
        console.group('🚀 Status Change Modal Initialization');
        console.log('Modal Element:', modalElement);
        
        const modalInitializationMethods = [
            // Method 1: Modern Bootstrap 5 initialization
            () => {
                console.log('🔹 Attempting Bootstrap 5 Modal Initialization');
                if (window.bootstrap && window.bootstrap.Modal) {
                    // Manually create and show the modal
                    const modalInstance = new window.bootstrap.Modal(modalElement, {
                        backdrop: true,
                        keyboard: true
                    });
                    
                    // Explicitly show the modal
                    modalElement.style.display = 'block';
                    modalElement.classList.add('show');
                    document.body.classList.add('modal-open');
                    
                    // Create backdrop
                    const backdrop = document.createElement('div');
                    backdrop.classList.add('modal-backdrop', 'fade', 'show');
                    document.body.appendChild(backdrop);
                    
                    console.groupEnd();
                    return true;
                }
                return false;
            },
            
            // Method 2: Alternative Bootstrap initialization
            () => {
                console.log('🔹 Attempting Alternative Bootstrap Modal Initialization');
                if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                    // Manually create and show the modal
                    const modalInstance = new bootstrap.Modal(modalElement, {
                        backdrop: true,
                        keyboard: true
                    });
                    
                    // Explicitly show the modal
                    modalElement.style.display = 'block';
                    modalElement.classList.add('show');
                    document.body.classList.add('modal-open');
                    
                    // Create backdrop
                    const backdrop = document.createElement('div');
                    backdrop.classList.add('modal-backdrop', 'fade', 'show');
                    document.body.appendChild(backdrop);
                    
                    console.groupEnd();
                    return true;
                }
                return false;
            },
            
            // Method 3: Manual modal display
            () => {
                console.log('🔹 Attempting Manual Modal Display');
                // Manually show the modal
                modalElement.style.display = 'block';
                modalElement.classList.add('show');
                document.body.classList.add('modal-open');
                
                // Create backdrop
                const backdrop = document.createElement('div');
                backdrop.classList.add('modal-backdrop', 'fade', 'show');
                document.body.appendChild(backdrop);
                
                // Add close functionality
                const closeButtons = modalElement.querySelectorAll('[data-bs-dismiss="modal"]');
                closeButtons.forEach(button => {
                    button.addEventListener('click', () => {
                        modalElement.style.display = 'none';
                        modalElement.classList.remove('show');
                        document.body.classList.remove('modal-open');
                        backdrop.remove();
                    });
                });
                
                console.groupEnd();
                return true;
            }
        ];
        
        // Try each initialization method
        for (const method of modalInitializationMethods) {
            try {
                if (method()) {
                    console.log('✅ Status Change Modal Successfully Displayed');
                    return true;
                }
            } catch (error) {
                console.warn('❌ Status Change Modal Initialization Method Failed:', error);
            }
        }
        
        console.error('❌ All Status Change Modal Initialization Methods Failed');
        console.groupEnd();
        return false;
    }

    fetchLoteDetails({ loteId, onSuccess, onError }) {
        console.log('🔍 Fetching lot details for lote ID:', loteId);
        
        const routes = [
            `/properties/properties/lotes/public/${loteId}/details`,
            `/properties/lotes/public/${loteId}/details`
        ];
        
        const fetchRoute = (routeIndex = 0) => {
            if (routeIndex >= routes.length) {
                console.error('❌ No valid route found for lot details');
                onError(new Error('No valid route found'));
                return;
            }
            
            console.log('🌐 Attempting route:', routes[routeIndex]);
            
            fetch(routes[routeIndex], {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json'
                },
                credentials: 'same-origin'
            })
            .then(response => {
                console.log('📡 Response received', {
                    url: response.url,
                    status: response.status,
                    ok: response.ok
                });
                
                // If response is not OK, try to get error text
                if (!response.ok) {
                    return response.text().then(errorText => {
                        console.error('❌ Error response text:', errorText);
                        
                        // Try next route if available
                        if (routeIndex < routes.length - 1) {
                            return fetchRoute(routeIndex + 1);
                        }
                        
                        throw new Error(`HTTP error! status: ${response.status}, text: ${errorText}`);
                    });
                }
                
                return response.json();
            })
            .then(data => {
                console.log('✅ Data received:', data);
                
                // Validate data before calling onSuccess
                if (!data || Object.keys(data).length === 0) {
                    console.error('❌ Received empty or invalid data');
                    if (routeIndex < routes.length - 1) {
                        return fetchRoute(routeIndex + 1);
                    }
                    onError(new Error('No data received'));
                    return;
                }
                
                onSuccess(data);
            })
            .catch(error => {
                console.error('❌ Fetch error:', error);
                
                // Try next route if available
                if (routeIndex < routes.length - 1) {
                    fetchRoute(routeIndex + 1);
                } else {
                    onError(error);
                }
            });
        };
        
        fetchRoute();
    }

    getValidStatusOptions(currentStatus) {
        console.log('Getting valid status options for current status:', currentStatus);
        
        const statusOptions = {
            'Libre': ['Apartado', 'Titulado'],
            'Apartado': ['Libre', 'Titulado'],
            'Titulado': ['Libre']
        };

        const validOptions = statusOptions[currentStatus] || [];
        
        console.log('Valid options:', validOptions);
        
        const optionsHtml = validOptions.map(status => 
            `<option value="${status}">${status}</option>`
        ).join('');
        
        console.log('Options HTML:', optionsHtml);
        
        return optionsHtml;
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
        const toast = new window.bootstrap.Toast(toastContainer.querySelector('.toast'));
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

    static async refreshLoteDetails(loteId) {
        // Fetch updated lot details and update the existing details row
        const routes = [
            `/properties/properties/lotes/public/${loteId}/details`,
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
                    statusText: response.statusText,
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
                    throw new Error('Network response was not ok');
                }

                return response.json();
            });
        };

        fetchLoteDetails([...routes])
            .then(data => {
                // Find the existing details row for this lot
                const existingDetailsRow = document.querySelector(`.lot-details-row[data-lote-id="${loteId}"]`);
                
                if (existingDetailsRow) {
                    // Prepare new details HTML
                    const detailsHTML = `
                        <td colspan="8">
                            <div class="container-fluid p-3">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6>Información del Lote</h6>
                                        <p><strong>ID:</strong> ${data.id}</p>
                                        <p><strong>Manzana:</strong> ${data.manzana || 'N/A'}</p>
                                        <p><strong>Lote:</strong> ${data.lote || 'N/A'}</p>
                                        <p><strong>Calle:</strong> ${data.calle || 'N/A'}</p>
                                        <p><strong>Número Exterior:</strong> ${data.numero_exterior || 'N/A'}</p>
                                        <p><strong>Número Interior:</strong> ${data.numero_interior || 'N/A'}</p>
                                        <p><strong>Superficie:</strong> ${data.terreno || 'N/A'} m²</p>
                                        <p><strong>Precio:</strong> $${data.precio.toLocaleString()}</p>
                                        <p><strong>Estado:</strong> ${data.estado || 'N/A'}</p>
                                        <p><strong>Tipo:</strong> ${data.tipo_de_lote || 'N/A'}</p>
                                    </div>
                                    <div class="col-md-6">
                                        ${data.asignacion ? `
                                        <h6>Información del Cliente</h6>
                                        <p><strong>Nombre:</strong> ${data.asignacion.client.nombre_completo}</p>
                                        <p><strong>Celular:</strong> ${data.asignacion.client.celular || 'N/A'}</p>
                                        <p><strong>Email:</strong> ${data.asignacion.client.email || 'N/A'}</p>
                                        <p><strong>Estado de Asignación:</strong> ${data.asignacion.estado || 'N/A'}</p>
                                        <p><strong>Fecha de Asignación:</strong> ${data.asignacion.fecha_asignacion ? 
                                            new Date(data.asignacion.fecha_asignacion).toLocaleDateString() : 'N/A'}</p>
                                        ` : ''}
                                    </div>
                                </div>
                            </div>
                        </td>
                    `;
                    
                    // Update the details row
                    existingDetailsRow.innerHTML = detailsHTML;
                }
            })
            .catch(error => {
                console.error('Error refreshing lot details:', error);
                CRMApi.showErrorToast('No se pudo actualizar los detalles del lote');
            });
    }

    unlinkClient(loteId) {
        console.group('🔗 Unlinking Client');
        console.log(`Unlinking client from lot ID: ${loteId}`);

        // Get CSRF token
        const csrfToken = this.getCsrfToken();

        // Send unlink request
        fetch(`/properties/lotes/${loteId}/unlink_client`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            credentials: 'same-origin'
        })
        .then(response => {
            console.log('Unlink Response:', response);
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(errorData.error || 'Error al desvincular cliente');
                });
            }
            return response.json();
        })
        .then(data => {
            console.log('Client Unlinked Successfully:', data);
            // Refresh lot details
            this.fetchLotDetails(loteId);
            
            // Show success notification
            this.showNotification('Cliente desvinculado exitosamente', 'success');
        })
        .catch(error => {
            console.error('Client Unlink Error:', error);
            this.showNotification(error.message, 'danger');
        })
        .finally(() => {
            console.groupEnd();
        });
    }

    submitStatusChange(loteId, newStatus, changeReason = '') {
        console.group('🔄 Submitting Lot Status Change');
        console.log('Lot Details:', { loteId, newStatus, changeReason });
        
        // Get CSRF token
        const csrfToken = this.getCsrfToken();
        
        // Prepare request payload
        const payload = {
            new_status: newStatus,
            reason: changeReason
        };
        
        // Close the modal
        const statusChangeModal = document.getElementById('statusChangeModal');
        if (statusChangeModal) {
            const modalInstance = bootstrap.Modal.getInstance(statusChangeModal);
            if (modalInstance) {
                modalInstance.hide();
            }
        }
        
        // Send status change request
        fetch(`/properties/lotes/${loteId}/change_status`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(payload)
        })
        .then(response => {
            console.log('Response Status:', response.status);
            
            // Log full response text for debugging
            return response.text().then(text => {
                console.log('Response Text:', text);
                
                // Try to parse JSON, if fails, throw an error
                try {
                    return JSON.parse(text);
                } catch (error) {
                    console.error('JSON Parsing Error:', error);
                    throw new Error(`Invalid JSON response: ${text}`);
                }
            });
        })
        .then(data => {
            console.log('Status Change Response:', data);
            
            if (data.new_status) {
                // Update UI to reflect new status
                this.showToast('Estado del lote actualizado exitosamente', 'success');
                
                // Update status badge in the UI
                const lotStatusElement = document.querySelector(`.lot-status-badge[data-lote-id="${loteId}"]`);
                if (lotStatusElement) {
                    lotStatusElement.textContent = data.new_status;
                    lotStatusElement.className = `lot-status-badge ${this.getStatusClass(data.new_status)}`;
                }
                
                // Optionally, refresh the lot details or update the status in the UI
                this.refreshLoteDetails(loteId);
            } else {
                // Handle error scenario
                this.showToast(data.message || 'No se pudo cambiar el estado del lote', 'danger');
            }
        })
        .catch(error => {
            console.error('❌ Error changing lot status:', error);
            this.showToast('Error al cambiar el estado del lote', 'danger');
        })
        .finally(() => {
            console.groupEnd();
        });
    }

    getCsrfToken() {
        // Try to get CSRF token from meta tag
        const csrfMetaTag = document.querySelector('meta[name="csrf-token"]');
        if (csrfMetaTag) {
            return csrfMetaTag.getAttribute('content');
        }
        
        // Try to get CSRF token from URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const csrfToken = urlParams.get('csrf_token');
        if (csrfToken) {
            return csrfToken;
        }
        
        // Try to get CSRF token from hidden input
        const csrfInput = document.querySelector('input[name="csrf_token"]');
        if (csrfInput) {
            return csrfInput.value;
        }
        
        // Fallback
        console.warn('CSRF token not found');
        return '';
    }
}

// Ensure LotesManager is globally accessible
window.LotesManager = new LotesManager();

document.addEventListener('DOMContentLoaded', () => {
    console.log(' Initializing LotesManager');
    window.LotesManager.initializeLotDetailsListeners();
    window.LotesManager.initializeLotStatusChangeListeners();
    
    // Global modal close handler
    document.addEventListener('click', (event) => {
        const closeButton = event.target.closest('.btn-close, [data-bs-dismiss="modal"]');
        if (closeButton) {
            const modal = closeButton.closest('.modal');
            if (modal) {
                try {
                    // Try Bootstrap modal hide method
                    const bootstrapModal = bootstrap.Modal.getInstance(modal);
                    if (bootstrapModal) {
                        bootstrapModal.hide();
                    }
                    
                    // Ensure backdrop and modal-open class are removed
                    modal.style.display = 'none';
                    modal.classList.remove('show');
                    document.body.classList.remove('modal-open');
                    
                    // Remove all modal backdrops
                    const backdrops = document.querySelectorAll('.modal-backdrop');
                    backdrops.forEach(backdrop => backdrop.remove());
                } catch (error) {
                    console.error('Error closing modal:', error);
                    
                    // Fallback manual close
                    modal.style.display = 'none';
                    modal.classList.remove('show');
                    document.body.classList.remove('modal-open');
                    
                    const backdrops = document.querySelectorAll('.modal-backdrop');
                    backdrops.forEach(backdrop => backdrop.remove());
                }
            }
        }
    });
});

// Update lot details modal to include client assignment section and use new updateLotDetailsModal method
LotesManager.prototype.initializeLotDetailsModal = function(data) {
    console.group('🏠 Initializing Lot Details Modal');
    console.log('Lot Details:', data);

    // Get modal element
    const lotDetailsModalElement = document.getElementById('lotDetailsModal');
    if (!lotDetailsModalElement) {
        console.error('Lot details modal element not found');
        return;
    }

    // Destroy any existing modal instances to prevent duplicates
    const existingModalInstance = bootstrap.Modal.getInstance(lotDetailsModalElement);
    if (existingModalInstance) {
        existingModalInstance.dispose();
    }

    // Create a new modal instance with explicit configuration
    const modalInstance = new bootstrap.Modal(lotDetailsModalElement, {
        backdrop: true,   // Allow closing by clicking outside
        keyboard: true    // Allow closing with ESC key
    });

    // Add event listeners to ensure clean modal behavior
    lotDetailsModalElement.addEventListener('hidden.bs.modal', () => {
        console.log('Modal fully hidden');
        // Remove any lingering backdrop manually
        const backdrop = document.querySelector('.modal-backdrop');
        if (backdrop) {
            backdrop.remove();
        }
        // Remove modal-open class from body if no other modals are open
        if (document.querySelectorAll('.modal.show').length === 0) {
            document.body.classList.remove('modal-open');
        }
    });

    // Populate lot details
    const lotDetailsModalBody = lotDetailsModalElement.querySelector('.modal-body');
    if (!lotDetailsModalBody) {
        console.error('Lot details modal body not found');
        return;
    }

    // Populate lot information
    lotDetailsModalBody.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <h6>Información del Lote</h6>
                <p><strong>Fraccionamiento:</strong> ${data.fraccionamiento || 'N/A'}</p>
                <p><strong>Manzana:</strong> ${data.manzana || 'N/A'}</p>
                <p><strong>Lote:</strong> ${data.lote || 'N/A'}</p>
                <p><strong>Calle:</strong> ${data.calle || 'N/A'}</p>
                <p><strong>Número Exterior:</strong> ${data.numero_exterior || 'N/A'}</p>
                <p><strong>Número Interior:</strong> ${data.numero_interior || 'N/A'}</p>
                <p><strong>Estado:</strong> ${data.estado || 'N/A'}</p>
                <p><strong>Terreno:</strong> ${data.terreno ? data.terreno + ' m²' : 'N/A'}</p>
                <p><strong>Precio:</strong> $${data.precio ? data.precio.toLocaleString() : 'N/A'}</p>
            </div>
            <div class="col-md-6">
                <h6>Detalles Adicionales</h6>
                <p><strong>Prototipo:</strong> ${data.prototipo || 'N/A'}</p>
                <p><strong>Estado del Inmueble:</strong> ${data.estado_del_inmueble || 'N/A'}</p>
                <p><strong>Tipo de Lote:</strong> ${data.tipo_de_lote || 'N/A'}</p>
                
                ${data.asignacion ? `
                    <h6>Información de Asignación</h6>
                    <p><strong>Cliente:</strong> ${data.asignacion.client.nombre_completo}</p>
                    <p><strong>Email:</strong> ${data.asignacion.client.email || 'N/A'}</p>
                    <p><strong>Celular:</strong> ${data.asignacion.client.celular || 'N/A'}</p>
                    <p><strong>Estado de Asignación:</strong> ${data.asignacion.estado || 'N/A'}</p>
                    <p><strong>Fecha de Asignación:</strong> ${data.asignacion.fecha_asignacion ? 
                        new Date(data.asignacion.fecha_asignacion).toLocaleDateString() : 'N/A'}</p>
                ` : ''}
            </div>
        </div>
        <div class="row">
            <div class="col-md-6" id="clientAssignmentSection">
                <div id="existingClientInfo" style="display: none;"></div>
                <button id="assignClientTrigger" class="btn btn-primary mt-3">
                    <i class="fas fa-user-plus"></i> Asignar Cliente
                </button>
                <button id="unlinkClientTrigger" class="btn btn-warning mt-2">
                    <i class="fas fa-unlink"></i> Desvincular Cliente
                </button>
            </div>
        </div>
    `;
    
    // Set data attributes for assignment and unlink buttons
    const assignClientButton = document.getElementById('assignClientTrigger');
    const unlinkClientButton = document.getElementById('unlinkClientTrigger');
    if (assignClientButton) {
        assignClientButton.setAttribute('data-lote-id', data.id);
    }
    if (unlinkClientButton) {
        unlinkClientButton.setAttribute('data-lote-id', data.id);
        unlinkClientButton.addEventListener('click', (event) => {
            const loteId = event.currentTarget.getAttribute('data-lote-id');
            this.unlinkClient(loteId);
        });
    }

    // Update modal with client assignment visibility
    this.updateLotDetailsModal(data);

    // Programmatically show the modal
    modalInstance.show();

    console.groupEnd();
}

LotesManager.prototype.updateLotDetailsModal = function(data) {
    console.group('🏠 Updating Lot Details Modal');
    console.log('Lot Data:', data);

    // Update basic lot information
    const lotDetailsModalBody = document.querySelector('#lotDetailsModal .modal-body');
    if (!lotDetailsModalBody) {
        console.error('Lot details modal body not found');
        return;
    }

    // Prepare client assignment button
    const assignClientButton = document.getElementById('assignClientTrigger');
    const unlinkClientButton = document.getElementById('unlinkClientTrigger');
    const clientAssignmentSection = document.getElementById('clientAssignmentSection');

    // Determine if lot has an existing assignment
    const hasExistingAssignment = data.asignacion && data.asignacion.client;
    console.log('Has Existing Assignment:', hasExistingAssignment);

    // Hide or show client assignment button based on assignment status
    if (assignClientButton && clientAssignmentSection && unlinkClientButton) {
        if (hasExistingAssignment) {
            // Hide assign client button
            assignClientButton.style.display = 'none';
            
            // Show unlink client button
            unlinkClientButton.style.display = 'block';
            
            // Populate existing client information
            const existingClientInfo = document.getElementById('existingClientInfo');
            if (existingClientInfo) {
                const client = data.asignacion.client;
                existingClientInfo.innerHTML = `
                    <h6>Cliente Asignado</h6>
                    <p><strong>Nombre:</strong> ${client.nombre_completo || 'N/A'}</p>
                    <p><strong>Email:</strong> ${client.email || 'N/A'}</p>
                    <p><strong>Celular:</strong> ${client.celular || 'N/A'}</p>
                    <p><strong>Estado de Asignación:</strong> ${data.asignacion.estado || 'N/A'}</p>
                    <p><strong>Fecha de Asignación:</strong> ${data.asignacion.fecha_asignacion ? 
                        new Date(data.asignacion.fecha_asignacion).toLocaleDateString() : 'N/A'}</p>
                `;
                existingClientInfo.style.display = 'block';
            }
            
            // Optionally, hide the entire client assignment section
            clientAssignmentSection.style.display = 'block';
        } else {
            // Show assign client button
            assignClientButton.style.display = 'block';
            
            // Show unlink client button
            unlinkClientButton.style.display = 'block';
            
            // Hide existing client info
            const existingClientInfo = document.getElementById('existingClientInfo');
            if (existingClientInfo) {
                existingClientInfo.style.display = 'none';
            }
            
            // Show client assignment section
            clientAssignmentSection.style.display = 'block';
        }
    }

    console.groupEnd();
}
