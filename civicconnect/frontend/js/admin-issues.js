// CivicConnect - Admin Issue Management
document.addEventListener('DOMContentLoaded', async () => {
    const user = getCurrentUserData();
    if (!user || user.role !== 'admin') {
        window.location.href = 'login.html';
        return;
    }

    const tableBody = document.getElementById('adminIssuesTable');

    try {
        const issues = await getAdminIssues();

        tableBody.innerHTML = issues.map(issue => `
            <tr>
                <td><strong>${issue.complaint_id}</strong></td>
                <td>${issue.title}</td>
                <td>${issue.category}</td>
                <td><span class="status-badge status-${issue.status.toLowerCase().replace(' ', '-')}">
                    ${issue.status}
                </span></td>
                <td><span class="priority-${issue.priority_level.toLowerCase()}">${issue.priority_level}</span></td>
                <td>User ${issue.user_id}</td>
                <td>
                    <div style="display: flex; gap: 5px;">
                        <button class="btn btn-outline" style="padding: 5px 10px; font-size: 12px;" onclick="assignIssue(${issue.id})">
                            Assign
                        </button>
                        <button class="btn btn-outline" style="padding: 5px 10px; font-size: 12px; background: var(--success); color: white;" onclick="resolveIssue(${issue.id})">
                            Resolve
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading admin issues:', error);
        tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: var(--danger);">Error loading issues</td></tr>';
    }
});

window.assignIssue = async (id) => {
    const deptId = prompt('Enter Department ID (1-6):');
    if (!deptId) return;
    try {
        await assignIssue(id, deptId);
        alert('Issue assigned successfully!');
        window.location.reload();
    } catch (error) {
        alert(error.message || 'Failed to assign issue');
    }
};

window.resolveIssue = async (id) => {
    const notes = prompt('Enter resolution notes:');
    if (!notes) return;
    try {
        await resolveIssue(id, notes);
        alert('Issue resolved successfully!');
        window.location.reload();
    } catch (error) {
        alert(error.message || 'Failed to resolve issue');
    }
};