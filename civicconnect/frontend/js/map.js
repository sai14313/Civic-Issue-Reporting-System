// CivicConnect - Map View
document.addEventListener('DOMContentLoaded', async () => {
    const map = L.map('map').setView([40.7128, -74.0060], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    const categoryIcons = {
        'Road & Pothole': '#ef4444',
        'Streetlight': '#3b82f6',
        'Garbage & Sanitation': '#10b981',
        'Water Supply': '#8b5cf6',
        'Drainage': '#f59e0b',
        'Public Safety': '#ec4899'
    };

    try {
        const issues = await getIssues();
        issues.forEach(issue => {
            const marker = L.marker([issue.latitude, issue.longitude]).addTo(map);
            const color = categoryIcons[issue.category] || '#64748b';
            marker.bindPopup(`
                <div style="font-family: Arial, sans-serif;">
                    <strong>${issue.complaint_id}</strong><br>
                    ${issue.title}<br>
                    <span style="color: ${color}; font-weight: bold;">${issue.category}</span><br>
                    Status: ${issue.status}<br>
                    <a href="issue.html?id=${issue.id}" target="_blank">View Details</a>
                </div>
            `);
        });
    } catch (error) {
        console.error('Error loading map issues:', error);
    }
});