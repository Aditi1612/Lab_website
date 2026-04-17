import { animate, scroll, inView, stagger } from "https://cdn.jsdelivr.net/npm/motion@latest/+esm";

// ─── NAVBAR SCROLL EFFECT ───────────────────────────────────────────────────
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  if (window.scrollY > 40) navbar.classList.add('scrolled');
  else navbar.classList.remove('scrolled');
});

// ─── MOBILE MENU ────────────────────────────────────────────────────────────
const menuBtn = document.getElementById('menuBtn');
const mobileMenu = document.getElementById('mobileMenu');
menuBtn?.addEventListener('click', () => {
  mobileMenu.classList.toggle('hidden');
});

// ─── HERO ENTRANCE ANIMATIONS ───────────────────────────────────────────────
const heroEls = {
  badge: document.getElementById('hero-badge'),
  title: document.getElementById('hero-title'),
  sub:   document.getElementById('hero-sub'),
  cta:   document.getElementById('hero-cta'),
  stats: document.getElementById('hero-stats'),
};

// Stagger entrance
const heroItems = [heroEls.badge, heroEls.title, heroEls.sub, heroEls.cta, heroEls.stats].filter(Boolean);

heroItems.forEach((el, i) => {
  animate(el,
    { opacity: [0, 1], y: [30, 0] },
    { duration: 0.8, delay: 0.1 + i * 0.13, easing: [0.16, 1, 0.3, 1] }
  );
});

// ─── REVEAL ON SCROLL ───────────────────────────────────────────────────────
const reveals = document.querySelectorAll('.reveal');
reveals.forEach(el => {
  inView(el, () => {
    el.classList.add('visible');
  }, { margin: "-60px" });
});

// ─── PARTICLE CANVAS ────────────────────────────────────────────────────────
const canvas = document.getElementById('particleCanvas');
if (canvas) {
  const ctx = canvas.getContext('2d');
  let W, H, particles = [];

  function resize() {
    W = canvas.width  = canvas.offsetWidth;
    H = canvas.height = canvas.offsetHeight;
  }
  resize();
  window.addEventListener('resize', resize);

  // Molecular bond particle system
  const NUM = 60;
  for (let i = 0; i < NUM; i++) {
    particles.push({
      x: Math.random() * (typeof W !== 'undefined' ? W : 1200),
      y: Math.random() * (typeof H !== 'undefined' ? H : 800),
      r: Math.random() * 2 + 0.5,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3,
      opacity: Math.random() * 0.6 + 0.2,
    });
  }

  function drawParticles() {
    ctx.clearRect(0, 0, W, H);

    // Draw bonds (lines between nearby particles)
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 120) {
          ctx.beginPath();
          ctx.strokeStyle = `rgba(0, 212, 255, ${(1 - dist / 120) * 0.15})`;
          ctx.lineWidth = 0.5;
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.stroke();
        }
      }
    }

    // Draw nodes
    particles.forEach(p => {
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(0, 212, 255, ${p.opacity})`;
      ctx.fill();

      // Update position
      p.x += p.vx;
      p.y += p.vy;
      if (p.x < 0 || p.x > W) p.vx *= -1;
      if (p.y < 0 || p.y > H) p.vy *= -1;
    });
  }

  function loop() {
    drawParticles();
    requestAnimationFrame(loop);
  }
  loop();
}

// ─── STAT COUNTER ANIMATION ─────────────────────────────────────────────────
function animateCount(el, target, suffix = '+') {
  let start = 0;
  const step = target / 60;
  const timer = setInterval(() => {
    start = Math.min(start + step, target);
    el.textContent = Math.floor(start) + (start >= target ? suffix : '');
    if (start >= target) clearInterval(timer);
  }, 16);
}

const statsSection = document.getElementById('hero-stats');
if (statsSection) {
  let counted = false;
  inView(statsSection, () => {
    if (counted) return;
    counted = true;
    const numbers = statsSection.querySelectorAll('.text-4xl');
    const targets = [10, 4, 200, 15];
    const suffixes = ['+', '', '+', '+'];
    numbers.forEach((el, i) => animateCount(el, targets[i], suffixes[i]));
  });
}
