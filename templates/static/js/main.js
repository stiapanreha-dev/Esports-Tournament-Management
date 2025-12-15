// Main JavaScript file
document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    if (mobileMenuButton) {
        mobileMenuButton.addEventListener('click', function() {
            const menu = document.getElementById('mobile-menu');
            menu.classList.toggle('hidden');
        });
    }
    
    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(msg => {
        setTimeout(() => {
            msg.style.opacity = '0';
            setTimeout(() => msg.remove(), 300);
        }, 5000);
    });
    
    // Form validation
    const forms = document.querySelectorAll('[data-validate]');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Add form validation logic here
        });
    });
});
