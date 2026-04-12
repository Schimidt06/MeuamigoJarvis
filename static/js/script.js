const socket = io();

// Stats Update
socket.on('stats_update', (data) => {
    // CPU
    document.getElementById('cpu-bar').style.width = data.cpu + '%';
    document.getElementById('cpu-val').innerText = data.cpu + '%';
    
    // RAM
    document.getElementById('ram-bar').style.width = data.ram + '%';
    document.getElementById('ram-val').innerText = data.ram + '%';
    
    // Battery
    document.getElementById('bat-bar').style.width = data.battery + '%';
    document.getElementById('bat-val').innerText = data.battery + '%';
});

// Mocking some visual activity for audio bars when "voice" is detected
// In a full implementation, we'd pipe real mic energy here
function animateBars() {
    const bars = document.querySelectorAll('.bars span');
    bars.forEach(bar => {
        let height = Math.random() * 100;
        bar.style.height = height + '%';
    });
}

// We can trigger animation based on a hypothetical 'voice_active' event
// socket.on('voice_active', (data) => { ... });
setInterval(animateBars, 150);

console.log("JARVIS HUD initialized.");
