// ===== Blood Donor Finder — interactions =====
document.addEventListener('DOMContentLoaded', () => {

  // Mobile nav toggle
  const toggle = document.querySelector('.nav-toggle');
  const links = document.querySelector('.nav-links');
  if (toggle && links) toggle.addEventListener('click', () => links.classList.toggle('open'));

  // Notification dropdown
  const notiBtn = document.querySelector('.noti-btn');
  const notiPanel = document.querySelector('.noti-panel');
  if (notiBtn && notiPanel) {
    notiBtn.addEventListener('click', (e) => { e.stopPropagation(); notiPanel.classList.toggle('open'); });
    document.addEventListener('click', () => notiPanel.classList.remove('open'));
    notiPanel.addEventListener('click', (e) => e.stopPropagation());
  }

  // Scroll reveal
  const io = new IntersectionObserver((entries) => {
    entries.forEach(en => { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
  }, { threshold: 0.12 });
  document.querySelectorAll('.reveal').forEach(el => io.observe(el));

  // Count-up stats
  const countEls = document.querySelectorAll('[data-count]');
  const cio = new IntersectionObserver((entries) => {
    entries.forEach(en => {
      if (!en.isIntersecting) return;
      const el = en.target; const target = +el.dataset.count; let cur = 0;
      const step = Math.max(1, Math.ceil(target / 45));
      const tick = () => { cur += step; if (cur >= target) { el.textContent = target; }
        else { el.textContent = cur; requestAnimationFrame(tick); } };
      tick(); cio.unobserve(el);
    });
  }, { threshold: 0.5 });
  countEls.forEach(el => cio.observe(el));

  // Animate bar fills
  const bio = new IntersectionObserver((entries) => {
    entries.forEach(en => { if (en.isIntersecting) { en.target.style.width = en.target.dataset.w + '%'; bio.unobserve(en.target); } });
  }, { threshold: 0.3 });
  document.querySelectorAll('.bar-fill').forEach(el => bio.observe(el));

  // Auto-dismiss toasts
  document.querySelectorAll('.toast').forEach(t => {
    setTimeout(() => { t.style.transition = '.4s'; t.style.opacity = '0'; t.style.transform = 'translateX(30px)';
      setTimeout(() => t.remove(), 400); }, 4500);
  });
});
