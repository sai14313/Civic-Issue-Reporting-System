// CivicConnect - Track Complaint
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('trackForm');
    const result = document.getElementById('trackResult');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const complaintId = document.getElementById('complaintId').value;

        try {
            // Search all issues for matching complaint ID
            const issues = await getIssues();
            const issue = issues.find(i => i.complaint_id === complaintId);

            if (!issue) {
                alert('Complaint ID not found. Please check and try again.');
                return;
            }

            result.style.display = 'block';
            document.getElementById('trackTitle').textContent = `Complaint ${issue.complaint_id}`;
            document.getElementById('trackComplaintId').textContent = issue.complaint_id;
            document.getElementById('trackCategory').textContent = issue.category;
            document.getElementById('trackLocation').textContent = issue.location_name;
            document.getElementById('trackDate').textContent = new Date(issue.created_at).toLocaleDateString();
            document.getElementById('trackStatus').textContent = issue.status;
            document.getElementById('trackStatus').className = `status-badge status-${issue.status.toLowerCase().replace(' ', '-')}`;
            document.getElementById('trackDescription').textContent = issue.description;

            const viewLink = result.querySelector('a');
            viewLink.href = `issue.html?id=${issue.id}`;
        } catch (error) {
            alert(error.message || 'Failed to track complaint');
        }
    });
});