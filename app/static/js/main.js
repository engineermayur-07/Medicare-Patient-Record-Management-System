/* MediCare Hospital — main.js */

// ─── Mobile hamburger ───
const hamburger = document.getElementById('hamburger');
const navLinks  = document.getElementById('nav-links');
const navAuth   = document.getElementById('nav-auth');

if (hamburger) {
  hamburger.addEventListener('click', () => {
    navLinks.classList.toggle('open');
    navAuth.classList.toggle('open');
    // Animate hamburger bars
    hamburger.classList.toggle('is-open');
  });

  // Close menu on outside click
  document.addEventListener('click', e => {
    if (!hamburger.contains(e.target) &&
        !navLinks.contains(e.target) &&
        !navAuth.contains(e.target)) {
      navLinks.classList.remove('open');
      navAuth.classList.remove('open');
      hamburger.classList.remove('is-open');
    }
  });
}

// ─── Flash auto-dismiss after 5 s ───
document.querySelectorAll('.flash').forEach(el => {
  setTimeout(() => {
    el.style.transition = 'opacity .4s';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 400);
  }, 5000);
});

// ─── Password eye toggle ───
function toggleEye(inputId, btn) {
  const input = document.getElementById(inputId);
  if (!input) return;
  if (input.type === 'password') {
    input.type = 'text';
    btn.textContent = '🙈';
  } else {
    input.type = 'password';
    btn.textContent = '👁';
  }
}

// ─── Active nav link highlight (fallback for non-Flask pages) ───
document.querySelectorAll('.nav-link').forEach(link => {
  if (link.href === window.location.href) link.classList.add('active');
});

// ─── Inject today's date as minimum on date inputs ───
document.querySelectorAll('input[type="date"]').forEach(input => {
  if (!input.min) {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    input.min = tomorrow.toISOString().split('T')[0];
  }
});
