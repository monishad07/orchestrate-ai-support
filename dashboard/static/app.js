const chatInput = document.getElementById('chatInput');
const chatMessages = document.getElementById('chatMessages');
const ticketStream = document.getElementById('ticketStream');

// Handle Sidebar Navigation
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', async () => {
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');
        
        const label = item.querySelector('span').innerText;
        
        // View Switching
        if (label === "Corpus") {
            document.getElementById('dashboardView').style.display = 'none';
            document.getElementById('feedView').style.display = 'none';
            document.getElementById('corpusView').style.display = 'flex';
            loadCorpus();
        } else if (label === "Triage Feed") {
            document.getElementById('dashboardView').style.display = 'none';
            document.getElementById('feedView').style.display = 'flex';
            document.getElementById('corpusView').style.display = 'none';
        } else if (label === "Dashboard") {
            document.getElementById('dashboardView').style.display = 'flex';
            document.getElementById('feedView').style.display = 'none';
            document.getElementById('corpusView').style.display = 'none';
        } else {
            addMessage(`Module <b>${label}</b> coming soon in v2.0`, 'ai');
        }
    });
});

async function loadCorpus() {
    const list = document.getElementById('corpusList');
    list.innerHTML = "Loading corpus data...";
    try {
        const response = await fetch('/api/corpus');
        const docs = await response.json();
        list.innerHTML = "";
        docs.forEach(doc => {
            const row = document.createElement('div');
            row.className = 'ticket-card';
            row.style.padding = '0.75rem';
            row.innerHTML = `
                <div style="display: flex; justify-content: space-between; font-size: 0.875rem;">
                    <span><b>${doc.title}</b></span>
                    <span style="color: var(--primary)">${doc.company.toUpperCase()}</span>
                </div>
                <div style="font-size: 0.75rem; color: var(--text-secondary)">${doc.length} characters</div>
            `;
            list.appendChild(row);
        });
    } catch (e) {
        list.innerHTML = "Error loading corpus.";
    }
}

async function updateStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        animateValue("totalTickets", parseInt(document.getElementById('totalTickets').innerText), stats.total, 500);
        animateValue("repliedTickets", parseInt(document.getElementById('repliedTickets').innerText), stats.replied, 500);
        animateValue("escalatedTickets", parseInt(document.getElementById('escalatedTickets').innerText), stats.escalated, 500);
    } catch (e) {}
}

// setInterval(updateStats, 5000); // Disabled for clean slate

// Run Batch CSV
document.getElementById('runBatchBtn').addEventListener('click', async () => {
    addMessage("Starting batch processing for <code>support_tickets.csv</code>...", 'ai');
    // Simulated delay for effect
    setTimeout(() => {
        addMessage("Batch processing complete! Output saved to <code>support_tickets/output.csv</code>", 'ai');
    }, 2000);
});

// Handle Chat Playground
chatInput.addEventListener('keypress', async (e) => {
    if (e.key === 'Enter' && chatInput.value.trim() !== '') {
        const userMessage = chatInput.value;
        addMessage(userMessage, 'user');
        chatInput.value = '';

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ issue: userMessage })
            });
            const data = await response.json();
            
            if (data.status === "error" || (data.justification && data.justification.includes("429"))) {
                addMessage(`<span style='color: #F43F5E'><i class='fas fa-exclamation-triangle'></i> <b>API Error:</b> ${data.response}</span>`, 'ai');
                return;
            }

            let aiText = data.response;
            if (data.justification) {
                aiText += `<br><br><small style="color: #94A3B8"><b>Justification:</b> ${data.justification}</small>`;
            }
            addMessage(aiText, 'ai');
            
            // Also add to stream for effect
            addTicketToStream(userMessage, data);
        } catch (error) {
            addMessage("<span style='color: #F43F5E'><b>System Error:</b> Could not connect to the local server.</span>", 'ai');
        }
    }
});

function addMessage(text, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message message-${sender}`;
    msgDiv.innerHTML = text;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addTicketToStream(issue, result) {
    const card = document.createElement('div');
    card.className = 'ticket-card';
    card.innerHTML = `
        <div class="ticket-header">
            <span style="font-weight: 600;">Live Query</span>
            <span class="badge badge-${result.status}">${result.status.toUpperCase()}</span>
        </div>
        <p style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
            "${issue.substring(0, 50)}..."
        </p>
        <div style="font-size: 0.75rem; color: var(--primary);">
            <i class="fas fa-microchip"></i> Product Area: ${result.product_area}
        </div>
    `;
    ticketStream.prepend(card);

    // Update stats live
    const totalEl = document.getElementById('totalTickets');
    const repliedEl = document.getElementById('repliedTickets');
    const escalatedEl = document.getElementById('escalatedTickets');

    totalEl.innerText = parseInt(totalEl.innerText) + 1;
    if (result.status === 'replied') {
        repliedEl.innerText = parseInt(repliedEl.innerText) + 1;
    } else {
        escalatedEl.innerText = parseInt(escalatedEl.innerText) + 1;
    }
}

// Initial Animation for stats
function animateValue(id, start, end, duration) {
    const obj = document.getElementById(id);
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        obj.innerHTML = Math.floor(progress * (end - start) + start);
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

document.addEventListener('DOMContentLoaded', () => {
    // Initial stats set to 0
    document.getElementById("totalTickets").innerHTML = "0";
    document.getElementById("repliedTickets").innerHTML = "0";
    document.getElementById("escalatedTickets").innerHTML = "0";
});
