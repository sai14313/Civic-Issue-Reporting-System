// CivicConnect - Issue Details
const issueId = new URLSearchParams(window.location.search).get('id');

document.addEventListener('DOMContentLoaded', async () => {
    if (!issueId) {
        window.location.href = 'browse.html';
        return;
    }

    try {
        const issue = await getIssue(issueId);
        const supports = await getSupports(issueId);

        document.getElementById('issueDetail').style.display = 'block';
        document.getElementById('loadingDetail').style.display = 'none';

        document.getElementById('detailComplaintId').textContent = issue.complaint_id;
        document.getElementById('detailTitle').textContent = issue.title;
        document.getElementById('detailDescription').textContent = issue.description;
        document.getElementById('detailCategory').textContent = issue.category;
        document.getElementById('detailLocation').textContent = issue.location_name;
        document.getElementById('detailDate').textContent = new Date(issue.created_at).toLocaleDateString();
        document.getElementById('detailSeverity').textContent = issue.priority_level;
        document.getElementById('detailSeverity').className = `priority-${issue.priority_level.toLowerCase()}`;

        const statusBadge = document.getElementById('detailStatus');
        statusBadge.textContent = issue.status;
        statusBadge.className = `status-badge status-${issue.status.toLowerCase().replace(' ', '-')}`;

        document.getElementById('supportCount').textContent = `${supports.total_support || 0} supports`;

        const photo = document.getElementById('detailPhoto');
        if (issue.photo_path) {
            photo.src = issue.photo_path;
            photo.style.display = 'block';
        }

        // Support button
        const supportBtn = document.getElementById('supportBtn');
        supportBtn.addEventListener('click', async () => {
            try {
                await supportIssue(issueId);
                supportBtn.disabled = true;
                supportBtn.textContent = 'Supported ✓';
                const newCount = (supports.total_support || 0) + 1;
                document.getElementById('supportCount').textContent = `${newCount} supports`;
            } catch (error) {
                alert(error.message || 'Failed to support issue');
            }
        });

        // Load updates
        const updatesContainer = document.getElementById('updatesList');
        updatesContainer.innerHTML = '<p>No updates yet.</p>';

    } catch (error) {
        document.getElementById('loadingDetail').innerHTML = `<p style="color: var(--danger);">Error loading issue: ${error.message}</p>`;
    }
});

window.submitFeedback = async (type) => {
    const comments = prompt(`Please provide your feedback about the resolution (${type}):`);
    if (comments === null) return;

    try {
        await submitFeedback(issueId, type, comments);
        document.getElementById('feedbackMsg').textContent = 'Thank you for your feedback!';
        setTimeout(() => {
            document.getElementById('feedbackMsg').textContent = '';
        }, 5000);
    } catch (error) {
        alert(error.message || 'Failed to submit feedback');
    }
};