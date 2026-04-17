import { animate, inView } from "https://cdn.jsdelivr.net/npm/motion@latest/+esm";

// ─── NAVBAR ──────────────────────────────────────────────────────────────────
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  navbar?.classList.toggle('scrolled', window.scrollY > 30);
});

// ─── MOBILE MENU ─────────────────────────────────────────────────────────────
document.getElementById('menuBtn')?.addEventListener('click', () => {
  document.getElementById('mobileMenu')?.classList.toggle('hidden');
});

// ─── HERO ENTRANCE ───────────────────────────────────────────────────────────
const heroEls = ['hero-badge','hero-title','hero-sub','hero-cta','hero-stats'].map(id => document.getElementById(id)).filter(Boolean);
heroEls.forEach((el, i) => {
  animate(el, { opacity: [0,1], y: [28,0] }, { duration: 0.7, delay: 0.1 + i * 0.12, easing: [0.16,1,0.3,1] });
});

// ─── REVEAL ON SCROLL ────────────────────────────────────────────────────────
document.querySelectorAll('.reveal').forEach(el => {
  inView(el, () => el.classList.add('visible'), { margin: '-50px' });
});

// ─── PARTICLE CANVAS (light version — dots on navy bg) ───────────────────────
const canvas = document.getElementById('particleCanvas');
if (canvas) {
  const ctx = canvas.getContext('2d');
  let W, H;

  function resize() {
    W = canvas.width  = canvas.offsetWidth;
    H = canvas.height = canvas.offsetHeight;
  }
  resize();
  window.addEventListener('resize', resize);

  const NUM = 50;
  const particles = Array.from({ length: NUM }, () => ({
    x: Math.random() * 1400, y: Math.random() * 800,
    r: Math.random() * 2 + 0.5,
    vx: (Math.random() - 0.5) * 0.25,
    vy: (Math.random() - 0.5) * 0.25,
    opacity: Math.random() * 0.5 + 0.2,
  }));

  function draw() {
    ctx.clearRect(0, 0, W, H);
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const d = Math.sqrt(dx*dx + dy*dy);
        if (d < 110) {
          ctx.beginPath();
          ctx.strokeStyle = `rgba(255,255,255,${(1 - d/110) * 0.12})`;
          ctx.lineWidth = 0.6;
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.stroke();
        }
      }
    }
    particles.forEach(p => {
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(255,255,255,${p.opacity})`;
      ctx.fill();
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0 || p.x > W) p.vx *= -1;
      if (p.y < 0 || p.y > H) p.vy *= -1;
    });
    requestAnimationFrame(draw);
  }
  draw();
}
