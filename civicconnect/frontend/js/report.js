// CivicConnect - Report Issue
document.addEventListener('DOMContentLoaded', async () => {
    // Initialize map
    const map = L.map('report-map').setView([40.7128, -74.0060], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    let marker = L.marker([40.7128, -74.0060]).addTo(map);

    map.on('click', (e) => {
        const { lat, lng } = e.latlng;
        marker.setLatLng([lat, lng]);
        document.getElementById('latitude').value = lat.toFixed(6);
        document.getElementById('longitude').value = lng.toFixed(6);
    });

    // AI Classification
    const photoInput = document.getElementById('photo');
    photoInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (file) {
            try {
                const result = await classifyImage(file);
                alert(`AI Suggestion: Category: ${result.predicted_category} (${Math.round(result.confidence * 100)}% confidence)\nSuggested Severity: ${result.suggested_severity}\n\nNote: This is a mock AI demo.`);

                // Auto-select category
                const categorySelect = document.getElementById('category');
                const categoryMap = {
                    'Road & Pothole': 'Road & Pothole',
                    'Streetlight': 'Streetlight',
                    'Garbage & Sanitation': 'Garbage & Sanitation',
                    'Water Supply': 'Water Supply',
                    'Drainage': 'Drainage',
                    'Public Safety': 'Public Safety'
                };
                if (categoryMap[result.predicted_category]) {
                    categorySelect.value = categoryMap[result.predicted_category];
                }

                // Auto-select severity
                const severitySelect = document.getElementById('severity');
                severitySelect.value = result.suggested_severity;
            } catch (error) {
                console.error('AI classification failed:', error);
            }
        }
    });

    // Handle form submission
    const form = document.getElementById('reportForm');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData();
        formData.append('title', document.getElementById('title').value);
        formData.append('category', document.getElementById('category').value);
        formData.append('description', document.getElementById('description').value);
        formData.append('latitude', document.getElementById('latitude').value);
        formData.append('longitude', document.getElementById('longitude').value);
        formData.append('location_name', document.getElementById('location_name').value);
        formData.append('severity', document.getElementById('severity').value);

        const photoFile = document.getElementById('photo').files[0];
        if (photoFile) {
            formData.append('photo', photoFile);
        }

        try {
            const btn = form.querySelector('button[type="submit"]');
            btn.textContent = 'Submitting...';
            btn.disabled = true;

            const result = await createIssue(formData);

            alert(`Issue reported successfully!\nComplaint ID: ${result.complaint_id}\n${result.is_duplicate ? '⚠️ Possible duplicate detected: ' + result.duplicate_suggestion : ''}`);

            window.location.href = `dashboard.html`;
        } catch (error) {
            alert(error.message || 'Failed to report issue');
            btn.textContent = 'Submit Report';
            btn.disabled = false;
        }
    });
});