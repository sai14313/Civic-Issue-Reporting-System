// CivicConnect - Global Navigation & Auth State
document.addEventListener('DOMContentLoaded', () => {
    const navUser = document.getElementById('navUser');
    const navLogout = document.getElementById('navLogout');
    const user = getCurrentUserData();

    // Update nav based on auth state
    if (user) {
        if (navUser) navUser.textContent = user.name;
        if (navLogout) {
            navLogout.style.display = 'inline-block';
            navLogout.addEventListener('click', (e) => {
                e.preventDefault();
                logout();
            });
        }
    }

    // Nav toggle for mobile
    const navToggle = document.getElementById('nav-toggle');
    const navLinks = document.querySelector('.nav-links');
    if (navToggle && navLinks) {
        navToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });
    }

    // Auto-redirect if already logged in on auth pages
    const currentPage = window.location.pathname.split('/').pop();
    const authPages = ['login.html', 'register.html'];
    if (user && authPages.includes(currentPage)) {
        if (user.role === 'admin') {
            window.location.href = 'admin.html';
        } else {
            window.location.href = 'dashboard.html';
        }
    }
});