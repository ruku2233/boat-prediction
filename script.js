function escapeHTML(str) {
    if (typeof str !== 'string') return str;
    return str.replace(/[&<>'"]/g, 
        tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag));
}

async function loadBoatData() {
    try {
        const response = await fetch('./data.json?t=' + new Date().getTime());
        if (!response.ok) throw new Error('データ取得エラー');
        const boatData = await response.json();
        
        document.getElementById('current-date').textContent = escapeHTML(boatData.date);
        renderVenueTabs(boatData.venues);
    } catch (error) {
        document.getElementById('race-container').innerHTML = 
            '<p style="color:red;">データの読み込みに失敗しました。</p>';
    }
}

function renderVenueTabs(venues) {
    const tabsContainer = document.getElementById('venue-tabs');
    tabsContainer.innerHTML = '';
    if (!venues || venues.length === 0) return;

    venues.forEach((venue, index) => {
        const btn = document.createElement('button');
        btn.className = `tab-btn ${index === 0 ? 'active' : ''}`;
        btn.textContent = escapeHTML(venue.venue_name || venue.name);
        btn.onclick = () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            renderRaces(venue);
        };
        tabsContainer.appendChild(btn);
    });

    renderRaces(venues[0]);
}

function renderRaces(venue) {
    const container = document.getElementById('race-container');
    container.innerHTML = '';

    venue.races.forEach(r => {
        const card = document.createElement('div');
        card.className = 'race-card';
        
        let recs = '解析中';
        if (r.prediction) {
            if (typeof r.prediction === 'object' && Array.isArray(r.prediction.recommendations)) {
                recs = r.prediction.recommendations.join(', ');
            } else {
                recs = r.prediction;
            }
        }

        card.innerHTML = `
            <div class="race-header">
                <span>${escapeHTML(venue.venue_name || venue.name)} ${escapeHTML(String(r.race_no))}R</span>
                <span class="badge">${escapeHTML(r.status)}</span>
            </div>
            <div class="prediction-box">🎯 AI推奨買い目: ${escapeHTML(recs)}</div>
        `;
        container.appendChild(card);
    });
}

document.addEventListener('DOMContentLoaded', loadBoatData);
