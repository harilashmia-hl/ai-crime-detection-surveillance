async function loadAlerts() {
    const response = await fetch('/api/alerts');
    const data = await response.json();
    const list = document.getElementById('alertsList');
    list.innerHTML = '';

    if (!data.alerts || data.alerts.length === 0) {
        list.innerHTML = '<div class="alert-card"><div class="alert-type">No active alerts</div><div class="alert-message">Monitoring is idle.</div></div>';
        return;
    }

    data.alerts.forEach((alert) => {
        const card = document.createElement('div');
        card.className = `alert-card ${alert.alert_type === 'loitering' ? 'critical' : ''}`;
        card.innerHTML = `
            <div class="alert-type">${alert.alert_type}</div>
            <div class="alert-time">${alert.timestamp}</div>
            <div class="alert-message">${alert.message}</div>
        `;
        list.appendChild(card);
    });
}

setInterval(loadAlerts, 3000);
loadAlerts();
