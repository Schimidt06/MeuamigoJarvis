const canvas = document.getElementById('neural-canvas');
const ctx = canvas.getContext('2d');

let width, height;
let nodes = [];
const nodeCount = 60;
const connectionDist = 180;
let audioLevel = 0;

function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
}

window.addEventListener('resize', resize);
resize();

class Node {
    constructor() {
        this.x = Math.random() * width;
        this.y = Math.random() * height;
        this.vx = (Math.random() - 0.5) * 1.5;
        this.vy = (Math.random() - 0.5) * 1.5;
        this.baseSize = Math.random() * 2 + 1;
    }

    update() {
        // Reage à voz
        const speedMultiplier = 1 + (audioLevel * 5);
        this.x += this.vx * speedMultiplier;
        this.y += this.vy * speedMultiplier;

        if (this.x < 0 || this.x > width) this.vx *= -1;
        if (this.y < 0 || this.y > height) this.vy *= -1;
    }

    draw() {
        const glow = audioLevel * 20;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.baseSize + (audioLevel * 5), 0, Math.PI * 2);
        ctx.fillStyle = `rgba(0, 242, 255, ${0.3 + (audioLevel * 0.7)})`;
        ctx.fill();
        if (audioLevel > 0.1) {
            ctx.shadowBlur = glow;
            ctx.shadowColor = '#00f2ff';
        } else {
            ctx.shadowBlur = 0;
        }
    }
}

function init() {
    nodes = [];
    for (let i = 0; i < nodeCount; i++) {
        nodes.push(new Node());
    }
}

function animate() {
    ctx.clearRect(0, 0, width, height);

    for (let i = 0; i < nodes.length; i++) {
        const n1 = nodes[i];
        n1.update();
        n1.draw();

        for (let j = i + 1; j < nodes.length; j++) {
            const n2 = nodes[j];
            const dx = n1.x - n2.x;
            const dy = n1.y - n2.y;
            const dist = Math.sqrt(dx * dx + dy * dy);

            if (dist < connectionDist) {
                ctx.beginPath();
                ctx.moveTo(n1.x, n1.y);
                ctx.lineTo(n2.x, n2.y);
                const opacity = (1 - dist / connectionDist) * (0.1 + audioLevel * 0.4);
                ctx.strokeStyle = `rgba(0, 242, 255, ${opacity})`;
                ctx.lineWidth = 1;
                ctx.stroke();
            }
        }
    }
    requestAnimationFrame(animate);
}

init();
animate();

// Polling do Backend para pegar nível de áudio e status do sistema
async function updateStats() {
    try {
        const res = await fetch('/status');
        const data = await res.json();
        
        // Atualiza nível de áudio para a animação
        audioLevel = data.audio_level; // Valor de 0 a 1
        
        // Atualiza UI
        document.getElementById('cpu-val').innerText = data.cpu + '%';
        document.getElementById('ram-val').innerText = data.ram + '%';
        document.getElementById('status-text').innerText = data.is_active ? 'PROCESSANDO...' : 'AGUARDANDO...';
        
    } catch (e) {
        console.error("Backend offline");
    }
}

setInterval(updateStats, 100);

// Controles
document.getElementById('btn-mute').addEventListener('click', async () => {
    const res = await fetch('/toggle_mute', { method: 'POST' });
    const data = await res.json();
    document.getElementById('btn-mute').classList.toggle('active', data.is_muted);
    document.getElementById('btn-mute').querySelector('.label').innerText = data.is_muted ? 'DESMUTAR' : 'MUTAR';
});

document.getElementById('btn-camera').addEventListener('click', async () => {
    const res = await fetch('/toggle_camera', { method: 'POST' });
    const data = await res.json();
    document.getElementById('btn-camera').classList.toggle('active', data.camera_on);
});
