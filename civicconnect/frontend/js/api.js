// CivicConnect - API Helper
const API_BASE = window.location.origin;

async function apiRequest(endpoint, options = {}) {
    const token = localStorage.getItem('civicconnect_token');
    const config = {
        headers: {},
        ...options
    };
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    const response = await fetch(`${API_BASE}${endpoint}`, config);
    if (response.status === 401) {
        localStorage.removeItem('civicconnect_token');
        localStorage.removeItem('civicconnect_user');
        window.location.href = 'login.html';
        throw new Error('Unauthorized');
    }
    return response.json();
}

async function getIssues(params = {}) {
    const query = new URLSearchParams(params).toString();
    return apiRequest(`/api/issues?${query}`);
}

async function getIssue(id) {
    return apiRequest(`/api/issues/${id}`);
}

async function createIssue(data) {
    return apiRequest('/api/issues', {
        method: 'POST',
        body: data
    });
}

async function updateIssue(id, data) {
    return apiRequest(`/api/issues/${id}`, {
        method: 'PUT',
        body: data
    });
}

async function deleteIssue(id) {
    return apiRequest(`/api/issues/${id}`, { method: 'DELETE' });
}

async function supportIssue(id) {
    return apiRequest(`/api/issues/${id}/support`, { method: 'POST' });
}

async function getSupports(id) {
    return apiRequest(`/api/issues/${id}/supports`);
}

async function classifyImage(file) {
    const formData = new FormData();
    formData.append('photo', file);
    return apiRequest('/api/ai/classify', {
        method: 'POST',
        body: formData
    });
}

async function getStats() {
    return apiRequest('/api/admin/stats');
}

async function getAdminIssues() {
    return apiRequest('/api/admin/issues');
}

async function assignIssue(id, departmentId) {
    const formData = new FormData();
    formData.append('department_id', departmentId);
    return apiRequest(`/api/admin/issues/${id}/assign`, { method: 'PUT', body: formData });
}

async function resolveIssue(id, notes) {
    const formData = new FormData();
    formData.append('resolution_notes', notes);
    return apiRequest(`/api/admin/issues/${id}/resolve`, { method: 'PUT', body: formData });
}

async function getNotifications() {
    return apiRequest('/api/notifications');
}

async function markNotificationRead(id) {
    return apiRequest(`/api/notifications/${id}/read`, { method: 'PUT' });
}

async function submitFeedback(issueId, type, comments) {
    const formData = new FormData();
    formData.append('feedback_type', type);
    formData.append('comments', comments);
    return apiRequest(`/api/issues/${issueId}/feedback`, { method: 'POST', body: formData });
}

async function getUserIssues() {
    return apiRequest('/api/user/issues');
}

async function getCurrentUser() {
    return apiRequest('/api/user/me');
}

async function login(email, password) {
    const formData = new FormData();
    formData.append('email', email);
    formData.append('password', password);
    const result = await apiRequest('/api/auth/login', {
        method: 'POST',
        body: formData
    });
    localStorage.setItem('civicconnect_token', result.access_token);
    localStorage.setItem('civicconnect_user', JSON.stringify(result.user));
    return result;
}

async function register(userData) {
    const formData = new FormData();
    for (const [key, value] of Object.entries(userData)) {
        formData.append(key, value);
    }
    return apiRequest('/api/auth/register', { method: 'POST', body: formData });
}

function getAuthHeaders() {
    const token = localStorage.getItem('civicconnect_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
}

function isLoggedIn() {
    return !!localStorage.getItem('civicconnect_token');
}

function logout() {
    localStorage.removeItem('civicconnect_token');
    localStorage.removeItem('civicconnect_user');
    window.location.href = 'index.html';
}

function getCurrentUserData() {
    const user = localStorage.getItem('civicconnect_user');
    return user ? JSON.parse(user) : null;
}