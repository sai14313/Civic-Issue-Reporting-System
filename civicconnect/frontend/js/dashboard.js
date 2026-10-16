// CivicConnect - Citizen Dashboard
document.addEventListener('DOMContentLoaded', async () => {
    const user = getCurrentUserData();
    if (!user) {
        window.location.href = 'login.html';
        return;
    }

    document.getElementById('welcomeName').textContent = `Welcome, ${user.name}!`;

    try {
        // Load user stats
        const issues = await getUserIssues();
        const notifications = await getNotifications();

        // Update stats
        document.getElementById('totalIssues').textContent = issues.length;
        document.getElementById('pendingIssues').textContent = issues.filter(i => i.status !== 'Resolved').length;
        document.getElementById('resolvedIssues').textContent = issues.filter(i => i.status === 'Resolved').length;

        // Total support
        let totalSupport = 0;
        for (const issue of issues) {
            const supports = await getSupports(issue.id);
            totalSupport += supports.total_support || 0;
        }
        document.getElementById('totalSupport').textContent = totalSupport;

        // Update notification badge
        const unread = notifications.filter(n => !n.is_read).length;
        const notifCount = document.getElementById('notifCount');
        if (unread > 0) {
            notifCount.textContent = unread;
            notifCount.style.display = 'block';
        }

        // Display issues
        const container = document.getElementById('userIssues');
        const noIssues = document.getElementById('noIssues');

        if (issues.length === 0) {
            container.style.display = 'none';
            noIssues.style.display = 'block';
            return;
        }

        container.innerHTML = issues.map(issue => `
            <div class="issue-card">
                <div class="issue-image">
                    ${issue.photo_path ? `<img src="${issue.photo_path}" alt="Issue">` : '<i class="fas fa-exclamation-triangle"></i>'}
                </div>
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
                        <span><i class="fas fa-map-marker-alt"></i> ${issue.location_name}</span>
                        <span><i class="fas fa-clock"></i> ${new Date(issue.created_at).toLocaleDateString()}</span>
                    </div>
                    <div class="issue-actions">
                        <a href="issue.html?id=${issue.id}" class="btn btn-outline">View Details</a>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
});