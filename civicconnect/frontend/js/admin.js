// CivicConnect - Admin Dashboard
document.addEventListener('DOMContentLoaded', async () => {
    const user = getCurrentUserData();
    if (!user || user.role !== 'admin') {
        window.location.href = 'login.html';
        return;
    }

    try {
        const stats = await getStats();
        document.getElementById('adminTotalIssues').textContent = stats.total_issues;
        document.getElementById('adminTotalUsers').textContent = stats.total_users;
        document.getElementById('adminResolvedIssues').textContent = stats.resolved_issues;
        document.getElementById('adminInProgress').textContent = stats.in_progress;

        // Load recent issues
        const issues = await getAdminIssues();
        const container = document.getElementById('adminIssuesContainer');

        container.innerHTML = issues.slice(0, 8).map(issue => `
            <div class="issue-card">
                <div class="issue-content">
                    <div class="issue-header">
                        <span class="issue-complaint-id">${issue.complaint_id}</span>
                        <span class="status-badge status-${issue.status.toLowerCase().replace(' ', '-')}">
                            ${issue.status}
                        </span>
                    </div>
                    <h3 class="issue-title">${issue.title}</h3>
                    <span class="issue-category issue-category.${issue.category.toLowerCase().replace(/[^a-z0-9]/g, '')}">
                        ${issue.category}
                    </span>
                    <p class="issue-description">${issue.description}</p>
                    <div class="issue-meta">
                        <span><i class="fas fa-user"></i> User ID: ${issue.user_id}</span>
                        <span><i class="fas fa-map-marker-alt"></i> ${issue.location_name}</span>
                        <span class="${issue.priority_level.toLowerCase()}">${issue.priority_level}</span>
                    </div>
                    <div class="issue-actions">
                        <a href="admin-issues.html" class="btn btn-outline">Manage</a>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading admin dashboard:', error);
    }
});