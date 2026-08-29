// ── NAV SCROLL ──────────────────────────────────────────
window.addEventListener('scroll', () => {
  document.getElementById('navbar')?.classList.toggle('scrolled', window.scrollY > 40);
});

function toggleNav() {
  document.getElementById('navLinks')?.classList.toggle('open');
}

// ── SCROLL REVEAL ────────────────────────────────────────
const observer = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.style.animation = 'fadeUp 0.6s ease forwards';
      observer.unobserve(e.target);
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.solution-card, .scale-item, .tech-item, .team-card, .kpi-card, .arch-layer, .tech-stack-card').forEach(el => {
  el.style.opacity = '0';
  observer.observe(el);
});

// ── COUNTER ANIMATION ─────────────────────────────────────
function animateCounter(el, target, suffix = '') {
  let start = 0;
  const duration = 1800;
  const step = timestamp => {
    if (!start) start = timestamp;
    const progress = Math.min((timestamp - start) / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 3);
    el.textContent = (Number.isInteger(target)
      ? Math.floor(ease * target)
      : (ease * target).toFixed(1)) + suffix;
    if (progress < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

const counterObserver = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      const el = e.target;
      const raw = el.dataset.count;
      const suffix = el.dataset.suffix || '';
      const val = parseFloat(raw);
      animateCounter(el, val, suffix);
      counterObserver.unobserve(el);
    }
  });
}, { threshold: 0.5 });

document.querySelectorAll('[data-count]').forEach(el => counterObserver.observe(el));

// ── SENSOR DATA GENERATION ────────────────────────────────
function rnd(min, max, dec = 2) {
  return parseFloat((Math.random() * (max - min) + min).toFixed(dec));
}

function generateSensorData() {
  const stations = {
    'ellis_bridge':  'Ellis Bridge',
    'gandhi_bridge': 'Gandhi Bridge',
    'nehru_bridge':  'Nehru Bridge',
    'sardar_bridge': 'Sardar Bridge',
    'vasna_barrage': 'Vasna Barrage',
  };
  return Object.entries(stations).map(([key, label]) => ({
    station: key, label,
    ph:   rnd(6.8, 8.4),
    do:   rnd(4.5, 9.0, 1),
    turb: rnd(5, 80, 1),
    temp: rnd(24, 34, 1),
    wl:   rnd(1.5, 4.5),
  }));
}

function phStatus(v)   { return v >= 6.5 && v <= 8.5 ? 's-good' : v >= 5.5 && v <= 9.5 ? 's-warn' : 's-bad'; }
function doStatus(v)   { return v >= 6 ? 's-good' : v >= 4 ? 's-warn' : 's-bad'; }
function turbStatus(v) { return v <= 25 ? 's-good' : v <= 50 ? 's-warn' : 's-bad'; }

// ── LIVE SENSOR UPDATES ───────────────────────────────────
function fetchLiveSensors() {
  const data = generateSensorData();
  const now = new Date().toLocaleTimeString('en-IN');

  data.forEach(s => {
    // Home page sensor cards
    const card = document.querySelector(`[data-station="${s.station}"]`);
    if (card) {
      const set = (p, val, cls) => {
        const el = card.querySelector(`[data-param="${p}"]`);
        if (el) { el.textContent = val; el.className = `sensor-val ${cls}`; }
      };
      set('ph',   s.ph,            phStatus(s.ph));
      set('do',   s.do + ' mg/L',  doStatus(s.do));
      set('turb', s.turb + ' NTU', turbStatus(s.turb));
      set('temp', s.temp + '°C',   '');
      set('wl',   s.wl + ' m',     '');
    }

    // Dashboard mini sensor rows
    const mini = document.querySelector(`[data-mini-station="${s.station}"]`);
    if (mini) {
      const phM   = mini.querySelector('[data-mini="ph"]');
      const doM   = mini.querySelector('[data-mini="do"]');
      const turbM = mini.querySelector('[data-mini="turb"]');
      if (phM)   { phM.textContent   = s.ph;   phM.className   = phStatus(s.ph).replace('s-',''); }
      if (doM)   { doM.textContent   = s.do;   doM.className   = doStatus(s.do).replace('s-',''); }
      if (turbM) { turbM.textContent = s.turb; turbM.className = turbStatus(s.turb).replace('s-',''); }
    }
  });

  // Update timestamps
  document.querySelectorAll('.updated-at').forEach(el => {
    el.textContent = 'Updated: ' + now;
  });
}

// ── RESOLVE DETECTION ─────────────────────────────────────
async function resolveDetection(id, btn) {
  try {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || getCookie('csrftoken');
    const res = await fetch(`/api/resolve/${id}/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrfToken }
    });
    if (res.ok) {
      const row = btn.closest('tr');
      if (row) { row.style.opacity = '0.4'; btn.textContent = 'Resolved'; btn.disabled = true; }
    }
  } catch(e) { console.log('Resolve error:', e); }
}

function getCookie(name) {
  const cookies = document.cookie.split(';');
  for (let c of cookies) {
    const [k, v] = c.trim().split('=');
    if (k === name) return decodeURIComponent(v);
  }
  return null;
}

// ── INITIALISE ─────────────────────────────────────────────
// Run immediately on page load so sensors show numbers right away
document.addEventListener('DOMContentLoaded', () => {
  fetchLiveSensors();
  setInterval(fetchLiveSensors, 5000);
});
