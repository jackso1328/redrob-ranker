let allCandidates = [];
let filteredCandidates = [];

// 1. Fetch Data on Load
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('data/sample_output.json');
        const data = await response.json();
        
        allCandidates = data.candidates;
        filteredCandidates = [...allCandidates];
        
        updateStats(data.metadata);
        renderHero(allCandidates[0]);
        renderTable(filteredCandidates);
        initCharts(allCandidates);
        
    } catch (error) {
        console.error("Failed to load dashboard data:", error);
        document.querySelector('.hero-content h2').innerText = "Error loading data. Run rank.py first!";
    }
});

// 2. Update Header Stats
function updateStats(metadata) {
    document.getElementById('stat-runtime').innerText = `${metadata.runtime_seconds}s`;
    document.getElementById('stat-viable').innerText = metadata.viable_candidates.toLocaleString();
}

// 3. Render Hero Section
function renderHero(topCandidate) {
    if(!topCandidate) return;
    document.getElementById('hero-name').innerText = topCandidate.candidate_id; // Using ID as name placeholder if name isn't in CSV
    document.getElementById('hero-title').innerText = topCandidate.reasoning;
}

// 4. Render Table
function renderTable(candidates) {
    const tbody = document.getElementById('table-body');
    tbody.innerHTML = '';
    
    document.getElementById('result-count').innerText = `Showing ${candidates.length} candidates`;

    candidates.forEach((cand, index) => {
        const tr = document.createElement('tr');
        tr.className = 'animate-row';
        tr.style.animationDelay = `${index * 0.05}s`;
        tr.onclick = () => openModal(cand);
        
        // Determine match badge color
        let badgeClass = 'match-fair';
        if(cand.score > 0.8) badgeClass = 'match-strong';
        else if(cand.score > 0.5) badgeClass = 'match-good';

        tr.innerHTML = `
            <td><strong>#${cand.rank}</strong></td>
            <td>${cand.candidate_id}</td>
            <td>AI Engineer</td>
            <td>--</td>
            <td>${cand.score.toFixed(4)}</td>
            <td><span class="match-badge ${badgeClass}">${cand.score > 0.8 ? 'Strong' : cand.score > 0.5 ? 'Good' : 'Fair'}</span></td>
        `;
        tbody.appendChild(tr);
    });
}

// 5. Initialize Charts
function initCharts(candidates) {
    // Score Distribution Chart
    const scores = candidates.map(c => c.score);
    new Chart(document.getElementById('scoreChart'), {
        type: 'bar',
        data: {
            labels: ['0.0-0.2', '0.2-0.4', '0.4-0.6', '0.6-0.8', '0.8-1.0'],
            datasets: [{
                label: 'Candidates',
                data: [
                    scores.filter(s => s < 0.2).length,
                    scores.filter(s => s >= 0.2 && s < 0.4).length,
                    scores.filter(s => s >= 0.4 && s < 0.6).length,
                    scores.filter(s => s >= 0.6 && s < 0.8).length,
                    scores.filter(s => s >= 0.8).length
                ],
                backgroundColor: '#3b82f6',
                borderRadius: 4
            }]
        },
        options: { responsive: true, plugins: { legend: { display: false } } }
    });

    // Trap Detection Chart (Hardcoded for demo based on our Python output)
    new Chart(document.getElementById('trapChart'), {
        type: 'doughnut',
        data: {
            labels: ['IT Lifers', 'Keyword Stuffers', 'Honeypots', 'Clean'],
            datasets: [{
                data: [40000, 15000, 80, 44920],
                backgroundColor: ['#ef4444', '#f59e0b', '#8b5cf6', '#10b981'],
                borderWidth: 0
            }]
        },
        options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
    });
}

// 6. Modal Logic
const modal = document.getElementById('candidate-modal');
document.querySelector('.close-modal').onclick = () => modal.classList.remove('active');
window.onclick = (e) => { if (e.target == modal) modal.classList.remove('active'); }

function openModal(cand) {
    document.getElementById('modal-name').innerText = cand.candidate_id;
    document.getElementById('modal-rank').innerText = `Rank #${cand.rank}`;
    document.getElementById('modal-reasoning').innerText = cand.reasoning;
    modal.classList.add('active');
    
    // Fill progress bars dynamically
    const pBars = document.querySelectorAll('.progress-bar .fill');
    setTimeout(() => {
        pBars[0].style.width = `${(cand.score * 100).toFixed(0)}%`;
        pBars[1].style.width = '85%'; // Hardcoded for demo
    }, 100);
}

function scrollToTable() {
    document.getElementById('table-section').scrollIntoView({ behavior: 'smooth' });
}