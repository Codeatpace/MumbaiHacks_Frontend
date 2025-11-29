const API_URL = "http://127.0.0.1:8000/api";

// State
let isCallActive = false;
let currentTranscript = "";
let isCurrentCallSaved = false;
let callTimer = null;

// DOM Elements
const homeScreen = document.getElementById('homeScreen');
const callScreen = document.getElementById('callScreen');
const msgScreen = document.getElementById('msgScreen');
const msgList = document.getElementById('msgList');
const caregiverAlerts = document.getElementById('caregiverAlerts');
const threatCountEl = document.getElementById('threatCount');

// Navigation
function showScreen(screenId) {
    document.querySelectorAll('.screen-content').forEach(el => {
        el.classList.add('hidden');
        el.classList.remove('active');
    });
    const screen = document.getElementById(screenId);
    if (screen) {
        screen.classList.remove('hidden');
        screen.classList.add('active');
    }
}

function showHome() { showScreen('homeScreen'); }

function startApp() {
    showScreen('homeScreen');
}

// Simulation Triggers
async function simulateSafeSMS() {
    const text = "Hi Grandma, are you coming to dinner on Sunday? Love, Sarah.";
    await handleIncomingSMS(text);
}

async function simulateSpamSMS() {
    const text = "URGENT: Your bank account has been compromised. Click here to reset password: http://bit.ly/scam";
    await handleIncomingSMS(text);
}

async function simulateSafeCall() {
    // Saved contact, safe content
    startCall("Sarah (Granddaughter)", "Hey grandma, just checking in! Are we still on for lunch?", true);
}

async function simulateScamCall() {
    // Unknown number, scam content
    startCall("Unknown Number", "Grandma, I'm in jail! Please send money now! I was in an accident.", false);
}

async function analyzeCustomText() {
    const text = document.getElementById('customInput').value;
    if (text) await handleIncomingSMS(text);
}

async function analyzeCustomAudio() {
    const text = document.getElementById('customInput').value;
    if (text) startCall("Unknown Number", text, false);
}

// Logic
async function handleIncomingSMS(text) {
    showScreen('msgScreen');

    // Add bubble immediately
    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble';
    bubble.innerText = text;
    msgList.appendChild(bubble);

    // Analyze
    try {
        const response = await fetch(`${API_URL}/analyze/text`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });
        const result = await response.json();

        if (result.is_spam) {
            bubble.classList.add('scam');
            showMsgAlert(result.reason);
            updateDashboard();
        }
    } catch (e) {
        console.error("API Error", e);
    }
}

function showMsgAlert(reason) {
    const alertEl = document.getElementById('msgAlert');
    if (alertEl) {
        document.getElementById('msgReason').innerText = reason;
        alertEl.classList.remove('hidden');
    }
}

function dismissMsgAlert() {
    const alertEl = document.getElementById('msgAlert');
    if (alertEl) alertEl.classList.add('hidden');
}

// Call Logic
function startCall(caller, transcript, isSaved) {
    showScreen('callScreen');
    document.getElementById('callerName').innerText = caller;
    document.getElementById('callStatus').innerText = "Incoming Call...";

    // Reset UI elements
    document.getElementById('callAlert').classList.add('hidden');
    document.getElementById('callAnalysis').classList.add('hidden');
    document.querySelector('.call-actions').classList.remove('hidden');
    document.getElementById('btnEndCall').classList.add('hidden');

    currentTranscript = transcript;
    isCurrentCallSaved = isSaved;
}

function acceptCall() {
    document.getElementById('callStatus').innerText = "00:00";
    document.querySelector('.call-actions').classList.add('hidden');
    document.getElementById('btnEndCall').classList.remove('hidden');

    // Start Timer
    let seconds = 0;
    if (callTimer) clearInterval(callTimer);
    callTimer = setInterval(() => {
        seconds++;
        const mins = Math.floor(seconds / 60).toString().padStart(2, '0');
        const secs = (seconds % 60).toString().padStart(2, '0');
        const statusEl = document.getElementById('callStatus');
        if (statusEl) statusEl.innerText = `${mins}:${secs}`;
    }, 1000);

    // Play Audio (TTS)
    speak(currentTranscript, isCurrentCallSaved);

    // Trigger Analysis ONLY if not a saved contact
    if (!isCurrentCallSaved) {
        document.getElementById('callAnalysis').classList.remove('hidden');
        setTimeout(() => {
            analyzeCall(currentTranscript);
        }, 2000);
    }
}

function speak(text, isSaved) {
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        const voices = window.speechSynthesis.getVoices();

        if (isSaved) {
            utterance.pitch = 1.2;
            utterance.rate = 1.0;
            const femaleVoice = voices.find(v => v.name.includes('Female') || v.name.includes('Samantha'));
            if (femaleVoice) utterance.voice = femaleVoice;
        } else {
            utterance.pitch = 0.8;
            utterance.rate = 0.9;
            const maleVoice = voices.find(v => v.name.includes('Male') || v.name.includes('Daniel'));
            if (maleVoice) utterance.voice = maleVoice;
        }
        window.speechSynthesis.speak(utterance);
    }
}

async function analyzeCall(transcript) {
    try {
        const response = await fetch(`${API_URL}/analyze/audio`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ transcript: transcript })
        });
        const result = await response.json();

        if (result.is_scam || result.is_deepfake) {
            const alertBox = document.getElementById('callAlert');
            alertBox.classList.remove('hidden');
            document.getElementById('callReason').innerText = result.reason.join(" ");
            updateDashboard();
        }
    } catch (e) {
        console.error("API Error", e);
    }
}

function endCall() {
    if (callTimer) clearInterval(callTimer);
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    showHome();
}

// Dashboard Logic
async function updateDashboard() {
    try {
        const response = await fetch(`${API_URL}/alerts`);
        const alerts = await response.json();

        if (threatCountEl) threatCountEl.innerText = alerts.length;

        if (caregiverAlerts) {
            caregiverAlerts.innerHTML = '';
            if (alerts.length === 0) {
                caregiverAlerts.innerHTML = '<div class="empty-state">No active threats detected.</div>';
                return;
            }

            alerts.forEach(alert => {
                const div = document.createElement('div');
                div.className = `alert-item ${alert.type}`;
                div.innerHTML = `
                    <strong>${alert.type.toUpperCase()} THREAT</strong><br>
                    <small>${new Date(alert.timestamp).toLocaleTimeString()}</small><br>
                    ${alert.reason}
                `;
                caregiverAlerts.appendChild(div);
            });
        }
    } catch (e) {
        console.error("Dashboard Error", e);
    }
}

async function clearAlerts() {
    try {
        await fetch(`${API_URL}/alerts/clear`, { method: 'POST' });
        updateDashboard();
    } catch (e) {
        console.error("Clear Alerts Error", e);
    }
}

// Poll dashboard every 5 seconds
setInterval(updateDashboard, 5000);
updateDashboard();
