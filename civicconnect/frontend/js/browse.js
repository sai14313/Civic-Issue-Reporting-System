// CivicConnect - Browse Issues
document.addEventListener('DOMContentLoaded', async () => {
    const container = document.getElementById('issuesContainer');
    const loading = document.getElementById('loading');
    const statusFilter = document.getElementById('statusFilter');
    const categoryFilter = document.getElementById('categoryFilter');

    async function loadIssues() {
        loading.style.display = 'block';
        container.innerHTML = '';

        try {
            const params = {};
            if (statusFilter.value) params.status = statusFilter.value;
            if (categoryFilter.value) params.category = categoryFilter.value;

            const issues = await getIssues(params);
            loading.style.display = 'none';

            if (issues.length === 0) {
                container.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--secondary);">No issues found.</div>';
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
                            ${issue.is_duplicate ? '<span style="color: var(--danger); font-size: 0.75rem;">Duplicate</span>' : ''}
                        </div>
                        <h3 class="issue-title">${issue.title}</h3>
                        <span class="issue-category issue-category.${issue.category.toLowerCase().replace(/[^a-z0-9]/g, '')}">
                            ${issue.category}
                        </span>
                        <p class="issue-description">${issue.description}</p>
                        <div class="issue-meta">
                            <span><i class="fas fa-map-marker-alt"></i> ${issue.location_name}</span>
                            <span class="${issue.priority_level.toLowerCase()}"><i class="fas fa-exclamation-circle"></i> ${issue.priority_level}</span>
                        </div>
                        <div class="issue-actions">
                            <a href="issue.html?id=${issue.id}" class="btn btn-outline">View Details</a>
                        </div>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            loading.style.display = 'none';
            container.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--danger);">Error loading issues.</div>';
        }
    }

    statusFilter.addEventListener('change', loadIssues);
    categoryFilter.addEventListener('change', loadIssues);

    loadIssues();
});