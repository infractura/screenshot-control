// Utility functions
console.log('Loading utils module...');

const utils = {
    // Show an alert message
    showAlert: function(message, type = 'error') {
        console.log('Showing alert:', message, 'type:', type);
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.textContent = message;
        
        // Remove any existing alerts
        document.querySelectorAll('.alert').forEach(alert => alert.remove());
        
        // Add new alert before the form
        const form = document.querySelector('form');
        if (form) {
            form.parentNode.insertBefore(alertDiv, form);
        } else {
            console.error('Form not found for alert placement');
            document.body.insertBefore(alertDiv, document.body.firstChild);
        }
        
        // Auto-remove after 5 seconds
        setTimeout(() => alertDiv.remove(), 5000);
    },

    // Show loading indicator
    showLoading: function(elementId) {
        console.log('Showing loading indicator in:', elementId);
        const element = document.getElementById(elementId);
        if (element) {
            const loader = document.createElement('div');
            loader.className = 'loading';
            element.innerHTML = '';
            element.appendChild(loader);
        } else {
            console.error('Loading element not found:', elementId);
        }
    },

    // Validate URL
    isValidUrl: function(string) {
        console.log('Validating URL:', string);
        try {
            new URL(string);
            return true;
        } catch (_) {
            return false;
        }
    },

    // Format bytes to human readable size
    formatBytes: function(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    // Debounce function for input handlers
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

console.log('Utils module loaded');
