// CivicConnect - Analytics
document.addEventListener('DOMContentLoaded', async () => {
    const user = getCurrentUserData();
    if (!user || user.role !== 'admin') {
        window.location.href = 'login.html';
        return;
    }

    try {
        const stats = await getStats();
        document.getElementById('analyticsTotalIssues').textContent = stats.total_issues;
        document.getElementById('analyticsResolvedRate').textContent = `${stats.resolution_rate}%`;
        document.getElementById('analyticsAvgDays').textContent = '7';
        document.getElementById('analyticsDuplicates').textContent = stats.duplicates;

        // Category chart
        const categoryContainer = document.getElementById('categoryChart');
        categoryContainer.innerHTML = stats.category_stats.map(cat => `
            <div style="margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span>${cat.category}</span>
                    <span>${cat.count}</span>
                </div>
                <div style="background: #e2e8f0; height: 20px; border-radius: 10px;">
                    <div style="background: var(--primary); height: 100%; width: ${(cat.count / Math.max(...stats.category_stats.map(c => c.count))) * 100}%; border-radius: 10px;"></div>
                </div>
            </div>
        `).join('');

        // Department chart
        const deptContainer = document.getElementById('departmentChart');
        deptContainer.innerHTML = stats.department_stats.map(dept => `
            <div style="margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span>${dept.department}</span>
                    <span>${dept.count}</span>
                </div>
                <div style="background: #e2e8f0; height: 20px; border-radius: 10px;">
                    <div style="background: var(--success); height: 100%; width: ${(dept.count / Math.max(...stats.department_stats.map(d => d.count))) * 100}%; border-radius: 10px;"></div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
});