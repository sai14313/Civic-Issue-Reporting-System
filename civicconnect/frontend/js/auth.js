// CivicConnect - Authentication
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const btn = loginForm.querySelector('button[type="submit"]');
            const originalText = btn.textContent;

            try {
                btn.textContent = 'Logging in...';
                btn.disabled = true;
                await login(email, password);
                const user = getCurrentUserData();
                if (user.role === 'admin') {
                    window.location.href = 'admin.html';
                } else {
                    window.location.href = 'dashboard.html';
                }
            } catch (error) {
                alert(error.message || 'Login failed');
                btn.textContent = originalText;
                btn.disabled = false;
            }
        });
    }

    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const userData = {
                name: document.getElementById('name').value,
                email: document.getElementById('email').value,
                password: document.getElementById('password').value,
                phone: document.getElementById('phone').value,
                address: document.getElementById('address').value
            };
            const btn = registerForm.querySelector('button[type="submit"]');
            const originalText = btn.textContent;

            try {
                btn.textContent = 'Creating account...';
                btn.disabled = true;
                await register(userData);
                alert('Registration successful! Please login.');
                window.location.href = 'login.html';
            } catch (error) {
                alert(error.message || 'Registration failed');
                btn.textContent = originalText;
                btn.disabled = false;
            }
        });
    }
});