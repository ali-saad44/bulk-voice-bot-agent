// ============================================
// VOICEBOT - Main Application Logic
// ============================================

const API_BASE = 'http://localhost:5000/api';

// State
let currentFilePath = null;
let currentCampaignId = null;
let pollInterval = null;

// DOM Elements
const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileCount = document.getElementById('fileCount');
const campaignName = document.getElementById('campaignName');
const campaignMessage = document.getElementById('campaignMessage');
const charCount = document.getElementById('charCount');
const startCampaignBtn = document.getElementById('startCampaignBtn');
const progressSection = document.getElementById('progressSection');
const progressFill = document.getElementById('progressFill');
const progressPercent = document.getElementById('progressPercent');
const progressText = document.getElementById('progressText');
const resultsBody = document.getElementById('resultsBody');
const exportBtn = document.getElementById('exportBtn');
const toast = document.getElementById('toast');
const toastMessage = document.getElementById('toastMessage');

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    updateCharCount();
    loadStats();
});

// ============================================
// FILE UPLOAD
// ============================================

uploadZone.addEventListener('click', () => fileInput.click());

uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('dragover');
});

uploadZone.addEventListener('dragleave', () => {
    uploadZone.classList.remove('dragover');
});

uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length) handleFile(files[0]);
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) handleFile(e.target.files[0]);
});

async function handleFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    showToast('Uploading file...');

    try {
        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            currentFilePath = data.filepath;
            fileName.textContent = data.filename;
            fileCount.textContent = `${data.total_numbers} numbers found`;
            fileInfo.classList.remove('hidden');
            startCampaignBtn.disabled = false;
            showToast(`Found ${data.total_numbers} phone numbers`);
        } else {
            showToast(data.error || 'Upload failed', true);
        }
    } catch (error) {
        showToast('Network error. Is the server running?', true);
    }
}

// ============================================
// MESSAGE CHARACTER COUNT
// ============================================

campaignMessage.addEventListener('input', updateCharCount);

function updateCharCount() {
    const len = campaignMessage.value.length;
    charCount.textContent = len;
    if (len > 450) {
        charCount.style.color = '#ef4444';
    } else {
        charCount.style.color = '#64748b';
    }
}

// ============================================
// START CAMPAIGN
// ============================================

startCampaignBtn.addEventListener('click', async () => {
    if (!currentFilePath) {
        showToast('Please upload a file first', true);
        return;
    }

    const message = campaignMessage.value.trim();
    if (!message) {
        showToast('Please enter a message', true);
        return;
    }

    startCampaignBtn.disabled = true;
    startCampaignBtn.innerHTML = `<span class="pulse-indicator">Creating...</span>`;

    try {
        // Step 1: Create campaign
        const createRes = await fetch(`${API_BASE}/campaign/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: campaignName.value || 'Untitled Campaign',
                message: message,
                filepath: currentFilePath
            })
        });

        const createData = await createRes.json();

        if (!createData.success) {
            showToast(createData.error || 'Failed to create campaign', true);
            startCampaignBtn.disabled = false;
            startCampaignBtn.innerHTML = `
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polygon points="5 3 19 12 5 21 5 3"/>
                </svg>
                Start Campaign
            `;
            return;
        }

        currentCampaignId = createData.campaign_id;
        showToast(`Campaign created with ${createData.total_numbers} numbers`);

        // Step 2: Start calling
        const startRes = await fetch(`${API_BASE}/campaign/${currentCampaignId}/start`, {
            method: 'POST'
        });

        const startData = await startRes.json();

        if (startData.success) {
            showToast('Campaign started! Calls are being made...');
            progressSection.classList.remove('hidden');
            startPolling();
        } else {
            showToast(startData.error || 'Failed to start campaign', true);
        }

    } catch (error) {
        showToast('Server error. Check console.', true);
        console.error(error);
    }
});

// ============================================
// POLLING FOR PROGRESS
// ============================================

function startPolling() {
    if (pollInterval) clearInterval(pollInterval);
    
    pollInterval = setInterval(async () => {
        if (!currentCampaignId) return;

        try {
            const res = await fetch(`${API_BASE}/campaign/${currentCampaignId}/status`);
            const data = await res.json();

            updateProgress(data.progress);
            updateResultsTable(data.calls);

            // Stop polling if complete
            if (data.progress.percentage >= 100) {
                clearInterval(pollInterval);
                showToast('Campaign completed!');
                exportBtn.disabled = false;
                loadStats();
            }

        } catch (error) {
            console.error('Polling error:', error);
        }
    }, 3000); // Poll every 3 seconds
}

function updateProgress(progress) {
    progressFill.style.width = `${progress.percentage}%`;
    progressPercent.textContent = `${progress.percentage}%`;
    progressText.textContent = `${progress.completed} of ${progress.total} calls completed`;
}

function updateResultsTable(calls) {
    if (!calls || calls.length === 0) return;

    const html = calls.map(call => {
        const statusClass = `status-${call.status}`;
        const statusText = call.status.replace('-', ' ').toUpperCase();
        const duration = call.duration ? `${call.duration}s` : '-';
        const time = call.completed_at 
            ? new Date(call.completed_at).toLocaleTimeString() 
            : '-';

        return `
            <tr>
                <td>${call.phone_number}</td>
                <td><span class="status-badge ${statusClass}">${statusText}</span></td>
                <td>${duration}</td>
                <td>${time}</td>
            </tr>
        `;
    }).join('');

    resultsBody.innerHTML = html;
}

// ============================================
// STATS
// ============================================

async function loadStats() {
    try {
        const res = await fetch(`${API_BASE}/campaigns`);
        const data = await res.json();
        
        // Calculate totals from all campaigns
        let total = 0, answered = 0, failed = 0;
        
        for (const campaign of data.campaigns) {
            const statusRes = await fetch(`${API_BASE}/campaign/${campaign.id}/status`);
            const statusData = await statusRes.json();
            const s = statusData.stats;
            
            total += s.total || 0;
            answered += (s.answered || 0);
            failed += (s.no_answer || 0) + (s.failed || 0) + (s.busy || 0);
        }

        document.getElementById('totalCalls').textContent = total;
        document.getElementById('answeredCalls').textContent = answered;
        document.getElementById('failedCalls').textContent = failed;
        
        const rate = total > 0 ? Math.round((answered / total) * 100) : 0;
        document.getElementById('successRate').textContent = `${rate}%`;

    } catch (error) {
        console.error('Stats error:', error);
    }
}

// ============================================
// EXPORT RESULTS
// ============================================

exportBtn.addEventListener('click', async () => {
    if (!currentCampaignId) return;
    
    try {
        const res = await fetch(`${API_BASE}/campaign/${currentCampaignId}/results`);
        const data = await res.json();
        
        if (data.result_files && data.result_files.length > 0) {
            const filename = data.result_files[0];
            window.open(`${API_BASE.replace('/api', '')}/download/${filename}`, '_blank');
            showToast('Results downloaded!');
        } else {
            showToast('No results file available yet', true);
        }
    } catch (error) {
        showToast('Download failed', true);
    }
});

// ============================================
// REFRESH
// ============================================

document.getElementById('refreshBtn').addEventListener('click', () => {
    loadStats();
    showToast('Refreshed');
});

// ============================================
// TOAST NOTIFICATIONS
// ============================================

function showToast(message, isError = false) {
    toastMessage.textContent = message;
    toast.style.background = isError ? '#ef4444' : '#1e293b';
    toast.classList.remove('hidden');
    
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}