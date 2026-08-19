// XSS安全対策エスケープ関数
function escapeHTML(str) {
    if (typeof str !== 'string') return str;
    return str.replace(/[&<>'"]/g, 
        tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag));
}

let boatData = null;

async function loadBoatData() {
    try {
        const response = await fetch('./data.json?t=' + new Date().getTime());
        if (!response.ok) throw new Error('データ取得エラー');
        boatData = await response.json();
        initUI();
    } catch (error) {
        document.getElementById('race-container').innerHTML = 
            '<p style="color:red;">データの読み込みに失敗しました。</p>';
    }
}

function initUI() {
    document.getElementById('current-date').textContent = escapeHTML(boatData.date);
    document.getElementById('hit-rate').textContent = escapeHTML(boatData.stats.hit_rate);
    document.getElementById('recovery-rate').textContent = escapeHTML(boatData.stats.recovery_rate);

    const tabsContainer = document.getElementById('venue-tabs');
    tabsContainer.innerHTML = '';

    if (!boatData.venues || boatData.venues.length === 0) return;

    boatData.venues.forEach((venue, index) => {
        const btn = document.createElement('button');
        btn.className = `tab-btn ${index === 0 ? 'active' : ''}`;
        btn.textContent = escapeHTML(venue.name);
        btn.onclick = () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            renderRaces(venue);
        };
        tabsContainer.appendChild(btn);
    });

    renderRaces(boatData.venues[0]);
}

function renderRaces(venue) {
    const container = document.getElementById('race-container');
    container.innerHTML = '';

    venue.races.forEach(r => {
        const card = document.createElement('div');
        card.className = 'race-card';
        card.innerHTML = `
            <div class="race-header">
                <span>${escapeHTML(venue.name)} ${escapeHTML(String(r.race_no))}R</span>
                <span class="badge">${escapeHTML(r.status)}</span>
            </div>
            <div class="prediction-box">🎯 予想: ${escapeHTML(r.prediction)}</div>
            <div class="payout-box">💰 払戻: ${escapeHTML(r.payout)}</div>
        `;
        container.appendChild(card);
    });
}

// 選手名鑑モーダル制御
document.addEventListener('DOMContentLoaded', () => {
    loadBoatData();
    const modal = document.getElementById('modal');
    document.getElementById('open-directory-btn').onclick = () => modal.style.display = 'flex';
    document.querySelector('.close-btn').onclick = () => modal.style.display = 'none';
});