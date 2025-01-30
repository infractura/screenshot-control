// Main application initialization and global handlers
console.log('Loading main application module...');

const app = {
    // Application state
    state: {
        initialized: false,
        darkMode: false
    },

    // Initialize application
    init() {
        console.log('Initializing main application...');
        if (this.state.initialized) {
            console.log('Application already initialized');
            return;
        }
        
        this.initializeTheme();
        this.bindGlobalEvents();
        
        this.state.initialized = true;
        console.log('Application initialization complete');
    },

    // Initialize theme based on user preference
    initializeTheme() {
        console.log('Initializing theme...');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        this.state.darkMode = localStorage.getItem('darkMode') === 'true' || prefersDark;
        this.updateTheme();
    },

    // Bind global event listeners
    bindGlobalEvents() {
        console.log('Binding global events...');
        
        // Handle global errors
        window.addEventListener('error', (e) => {
            console.error('Global error:', e);
            utils.showAlert(`An error occurred: ${e.message}`);
        });

        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', (e) => {
            console.error('Unhandled rejection:', e);
            utils.showAlert(`Request failed: ${e.reason}`);
        });

        // Handle theme toggle if present
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            console.log('Theme toggle found, binding click event');
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }

        // Handle network status
        window.addEventListener('online', () => {
            console.log('Network connection restored');
            utils.showAlert('Connection restored', 'success');
        });

        window.addEventListener('offline', () => {
            console.log('Network connection lost');
            utils.showAlert('No internet connection');
        });

        console.log('Global events bound');
    },

    // Toggle dark/light theme
    toggleTheme() {
        console.log('Toggling theme');
        this.state.darkMode = !this.state.darkMode;
        localStorage.setItem('darkMode', this.state.darkMode);
        this.updateTheme();
    },

    // Update theme classes and styles
    updateTheme() {
        console.log('Updating theme:', this.state.darkMode ? 'dark' : 'light');
        document.body.classList.toggle('dark-mode', this.state.darkMode);
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing main application');
    app.init();
});

console.log('Main application module loaded');
