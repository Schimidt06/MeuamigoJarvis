const socket = io();

const STATE_LABELS = {
    idle:       "IDLE",
    listening:  "LISTENING...",
    processing: "PROCESSING...",
    speaking:   "SPEAKING...",
};

const STATE_COLORS = {
    idle:       "#555",
    listening:  "#00ff88",
    processing: "#f0a500",
    speaking:   "#00d2ff",
};

// Stats update
socket.on("stats_update", (data) => {
    document.getElementById("cpu-bar").style.width = data.cpu + "%";
    document.getElementById("cpu-val").innerText = data.cpu + "%";
    document.getElementById("ram-bar").style.width = data.ram + "%";
    document.getElementById("ram-val").innerText = data.ram + "%";
    document.getElementById("bat-bar").style.width = data.battery + "%";
    document.getElementById("bat-val").innerText = data.battery + "%";
});

// State feedback
socket.on("state_update", (data) => {
    const el = document.getElementById("voice-status");
    const bars = document.querySelectorAll(".bars span");
    const state = data.state;

    el.innerText = STATE_LABELS[state] || state.toUpperCase();
    el.style.color = STATE_COLORS[state] || "#fff";
    bars.forEach(b => b.style.background = STATE_COLORS[state] || "#00d2ff");
});

// Response display with typewriter effect
socket.on("response_text", (data) => {
    const el = document.getElementById("last-response");
    el.innerText = "";
    let i = 0;
    const type = () => {
        if (i < data.text.length) {
            el.innerText += data.text[i++];
            setTimeout(type, 22);
        }
    };
    type();
});

// Animate bars while listening/speaking
function animateBars() {
    const statusEl = document.getElementById("voice-status");
    const isActive = statusEl && (
        statusEl.innerText === "LISTENING..." ||
        statusEl.innerText === "SPEAKING..."
    );
    const bars = document.querySelectorAll(".bars span");
    bars.forEach(bar => {
        bar.style.height = isActive
            ? (Math.random() * 90 + 10) + "%"
            : "10%";
    });
}

setInterval(animateBars, 150);
