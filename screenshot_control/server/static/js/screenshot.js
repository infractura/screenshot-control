// Screenshot handling functionality
const screenshot = {
    // Configuration and state
    config: {
        apiEndpoint: '/api/screenshot',
        presets: {
            desktop: { width: 1920, height: 1080 },
            laptop: { width: 1366, height: 768 },
            tablet: { width: 768, height: 1024 },
            phone: { width: 390, height: 844 },
            'phone-ls': { width: 844, height: 390 },
            '4k': { width: 3840, height: 2160 }
        }
    },

    // Initialize screenshot functionality
    init() {
        console.log('Initializing screenshot module...');
        this.bindEvents();
        this.initializePresets();
        console.log('Screenshot module initialized');
    },

    // Bind event listeners
    bindEvents() {
        console.log('Binding events...');
        const form = document.getElementById('screenshotForm');
        const presetSelect = document.getElementById('preset');
        
        if (form) {
            console.log('Form found, binding submit event');
            form.addEventListener('submit', (e) => this.handleSubmit(e));
        } else {
            console.error('Form element not found!');
        }
        
        if (presetSelect) {
            console.log('Preset select found, binding change event');
            presetSelect.addEventListener('change', (e) => this.handlePresetChange(e));
        } else {
            console.error('Preset select element not found!');
        }
    },

    // Initialize preset dropdown
    initializePresets() {
        console.log('Initializing presets...');
        const presetSelect = document.getElementById('preset');
        if (!presetSelect) {
            console.error('Preset select element not found during initialization!');
            return;
        }

        // Clear existing options
        presetSelect.innerHTML = '';

        // Add presets
        Object.entries(this.config.presets).forEach(([key, value]) => {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = `${key} (${value.width}x${value.height})`;
            presetSelect.appendChild(option);
        });

        // Add custom option
        const customOption = document.createElement('option');
        customOption.value = 'custom';
        customOption.textContent = 'Custom Size';
        presetSelect.appendChild(customOption);
        console.log('Presets initialized');
    },

    // Handle form submission
    async handleSubmit(e) {
        console.log('Form submitted');
        e.preventDefault();
        
        const url = document.getElementById('url').value;
        if (!utils.isValidUrl(url)) {
            utils.showAlert('Please enter a valid URL');
            return;
        }

        utils.showLoading('result');
        
        const formData = this.getFormData();
        console.log('Submitting with data:', formData);
        
        try {
            const response = await this.takeScreenshot(formData);
            this.handleResponse(response);
        } catch (error) {
            console.error('Screenshot error:', error);
            utils.showAlert(error.message);
            document.getElementById('result').innerHTML = '';
        }
    },

    // Handle preset change
    handlePresetChange(e) {
        console.log('Preset changed to:', e.target.value);
        const customSize = document.querySelector('.custom-size');
        if (e.target.value === 'custom') {
            customSize.classList.add('show');
        } else {
            customSize.classList.remove('show');
        }
    },

    // Get form data
    getFormData() {
        const preset = document.getElementById('preset').value;
        const formData = {
            url: document.getElementById('url').value,
            full_page: document.getElementById('fullPage').checked
        };

        if (preset === 'custom') {
            formData.width = parseInt(document.getElementById('width').value);
            formData.height = parseInt(document.getElementById('height').value);
        } else {
            formData.preset = preset;
        }

        return formData;
    },

    // Take screenshot API call
    async takeScreenshot(data) {
        console.log('Making API request to:', this.config.apiEndpoint);
        const response = await fetch(this.config.apiEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`Screenshot failed: ${response.statusText}`);
        }

        return response.json();
    },

    // Handle API response
    handleResponse(data) {
        console.log('Handling API response');
        const resultDiv = document.getElementById('result');
        
        if (data.success) {
            resultDiv.innerHTML = `
                <div class="preview-container">
                    <h3>Screenshot Result:</h3>
                    <img src="data:image/png;base64,${data.image}" 
                         alt="Screenshot" 
                         title="Click to open in new tab"
                         onclick="window.open(this.src, '_blank')"
                         style="cursor: pointer;">
                </div>
            `;
        } else {
            utils.showAlert(data.error || 'Screenshot failed');
            resultDiv.innerHTML = '';
        }
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing screenshot module');
    screenshot.init();
});
