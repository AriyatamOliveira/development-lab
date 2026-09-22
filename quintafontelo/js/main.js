document.addEventListener('DOMContentLoaded', () => {

  /* ── NAV SCROLL ── */
  const navbar = document.querySelector('.navbar');
  const onScroll = () => navbar.classList.toggle('scrolled', window.scrollY > 60);
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  /* ── ACTIVE NAV LINK ── */
  const currentPage = window.location.pathname.replace(/\/$/, '').split('/').pop() || 'index';
  document.querySelectorAll('.nav-links a, .mobile-nav a').forEach(link => {
    const href = (link.getAttribute('href') || '').replace('.html', '');
    const page = href.replace(/^\//, '') || 'index';
    if (page === currentPage || (currentPage === '' && page === 'index')) {
      link.classList.add('nav-active');
    }
  });

  /* ── MOBILE NAV ── */
  const hamburger       = document.querySelector('.hamburger');
  const mobileNav       = document.querySelector('.mobile-nav');
  const mobileOverlay   = document.querySelector('.mobile-nav-overlay');
  const mobileClose     = document.querySelector('.mobile-nav-close');

  const openNav  = () => { mobileNav.classList.add('active'); mobileOverlay.classList.add('active'); document.body.style.overflow = 'hidden'; };
  const closeNav = () => { mobileNav.classList.remove('active'); mobileOverlay.classList.remove('active'); document.body.style.overflow = ''; };

  hamburger?.addEventListener('click', openNav);
  mobileClose?.addEventListener('click', closeNav);
  mobileOverlay?.addEventListener('click', closeNav);
  document.querySelectorAll('.mobile-nav a').forEach(a => a.addEventListener('click', closeNav));

  /* ── SCROLL REVEAL ── */
  const revealEls = document.querySelectorAll('.reveal, .reveal-left, .reveal-right');
  const revealObs = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('visible');
      obs.unobserve(entry.target);
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });
  revealEls.forEach(el => revealObs.observe(el));

  /* ── HERO LOAD ── */
  const heroBg = document.querySelector('.hero-bg');
  if (heroBg) {
    setTimeout(() => heroBg.classList.add('loaded'), 100);
  }

  /* ── HERO TITLE STAGGER ── */
  document.querySelectorAll('.hero-animate-title').forEach(title => {
    const words = title.innerText.trim().split(' ');
    title.innerHTML = '';
    words.forEach((word, i) => {
      const span = document.createElement('span');
      span.textContent = word + '\u00A0';
      span.style.animationDelay = `${0.4 + i * 0.12}s`;
      title.appendChild(span);
    });
  });

  /* ── EMAIL COPY ── */
  document.querySelectorAll('.copy-email-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const email = btn.dataset.email;
      const confirm = btn.nextElementSibling;
      const show = () => { confirm.style.opacity = '1'; setTimeout(() => confirm.style.opacity = '0', 2000); };
      navigator.clipboard?.writeText(email).then(show).catch(() => {
        const ta = document.createElement('textarea');
        ta.value = email; ta.style.cssText = 'position:fixed;opacity:0;';
        document.body.appendChild(ta); ta.select(); document.execCommand('copy');
        document.body.removeChild(ta); show();
      });
    });
  });

  /* ── CONTACT FORM ── */
  const contactForm = document.getElementById('contact-form');
  if (contactForm) {
    contactForm.addEventListener('submit', e => {
      e.preventDefault();
      const btn = contactForm.querySelector('button[type="submit"]');
      btn.textContent = 'A enviar...';
      btn.disabled = true;
      setTimeout(() => {
        contactForm.style.transition = 'opacity 0.4s';
        contactForm.style.opacity = '0';
        setTimeout(() => {
          contactForm.innerHTML = `
            <div class="form-success">
              <i class="fa-solid fa-check"></i>
              <p class="form-success-title">Mensagem enviada!</p>
              <p class="form-success-sub">Em breve entraremos em contacto consigo.</p>
            </div>`;
          contactForm.style.opacity = '1';
        }, 400);
      }, 900);
    });
  }

});
