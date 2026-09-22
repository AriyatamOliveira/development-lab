import re
import os

css_path = 'css/style.css'
with open(css_path, 'r') as f:
    css = f.read()

# Upgrade 1
css = css.replace(
    '  animation: pageEnter 0.4s ease forwards;',
    '  animation: pageEnter 0.5s ease forwards;'
)
css = css.replace(
'''@keyframes pageEnter {
  from { opacity: 0; }
  to { opacity: 1; }
}''',
'''@keyframes pageEnter {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}'''
)

# Upgrade 2
old_nav = '''.nav-links a:not(.btn) {
  position: relative;
  padding-bottom: 3px;
}

.nav-links a:not(.btn)::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 1px;
  background-color: var(--color-stone);
  transition: width 0.3s ease;
}

.nav-links a:not(.btn):hover {
  color: var(--color-stone);
}

.nav-links a:not(.btn):hover::after {
  width: 100%;
}

.nav-links a.nav-active {
  color: var(--color-stone);
}

.nav-links a.nav-active::after {
  width: 100%;
}'''

new_nav = '''.nav-links a:not(.btn) {
  position: relative;
  padding-bottom: 4px;
  color: inherit;
}

.nav-links a:not(.btn)::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 1px;
  background-color: var(--color-stone);
  transition: width 0.3s ease;
}

.nav-links a:not(.btn):hover {
  color: var(--color-stone);
}

.nav-links a:not(.btn):hover::after,
.nav-links a.nav-active::after {
  width: 100%;
}

.nav-links a.nav-active {
  color: var(--color-stone);
}'''
css = css.replace(old_nav, new_nav)

# Upgrade 3
css = css.replace(
'''.reveal-left {
  opacity: 0;
  transform: translateX(-40px);
  transition: all var(--transition-slow);
}

.reveal-left.visible {
  opacity: 1;
  transform: translateX(0);
}

.reveal-right {
  opacity: 0;
  transform: translateX(40px);
  transition: all var(--transition-slow);
}

.reveal-right.visible {
  opacity: 1;
  transform: translateX(0);
}''',
'''.reveal-left {
  opacity: 0;
  transform: translateX(-40px);
  transition: opacity var(--transition-slow), transform var(--transition-slow);
}
.reveal-left.visible {
  opacity: 1;
  transform: translateX(0);
}

.reveal-right {
  opacity: 0;
  transform: translateX(40px);
  transition: opacity var(--transition-slow), transform var(--transition-slow);
}
.reveal-right.visible {
  opacity: 1;
  transform: translateX(0);
}'''
)

# Upgrade 5
css = css.replace(
'''.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.08);
  border-color: var(--color-stone);
}

.section-dark .card:hover {
  border-color: var(--color-stone);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4);
}''',
'''.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.09);
  border-color: var(--color-stone);
}

.section-dark .card:hover {
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.45);
  border-color: var(--color-stone);
}'''
)

# Upgrade 6
css = css.replace(
'''.gallery-item {
  overflow: hidden;
  position: relative;
  aspect-ratio: 1;
}

.gallery-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.gallery-item::after {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(28, 28, 28, 0);
  transition: background 0.5s ease;
  pointer-events: none;
}

.gallery-item:hover::after {
  background: rgba(28, 28, 28, 0.15);
}

.gallery-item:hover img {
  transform: scale(1.06);
}''',
'''.gallery-item {
  overflow: hidden;
  position: relative;
  aspect-ratio: 1;
  background-color: var(--color-dark);
}

.gallery-item::after {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(28, 28, 28, 0);
  transition: background 0.5s ease;
  pointer-events: none;
}

.gallery-item:hover::after {
  background: rgba(28, 28, 28, 0.18);
}

.gallery-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.gallery-item:hover img {
  transform: scale(1.07);
}'''
)

# Upgrade 7
css = css.replace('letter-spacing: -0.01em;', 'letter-spacing: -0.015em;', 1)
css = css.replace(
'''.intro-strip h2 {
  font-size: clamp(1.5rem, 3vw, 2.5rem);
  max-width: 800px;
  margin: 0 auto var(--spacing-sm);
  font-weight: 400;
  font-style: italic;
  color: var(--color-green);
}''',
'''.intro-strip h2 {
  font-size: clamp(1.5rem, 3vw, 2.5rem);
  max-width: 800px;
  margin: 0 auto var(--spacing-sm);
  font-weight: 400;
  font-style: italic;
  color: var(--color-green);
  letter-spacing: -0.01em;
}'''
)
css = css.replace(
'''.contact-form input::placeholder,
.contact-form textarea::placeholder {
  color: rgba(245, 240, 232, 0.35);
  font-size: 0.9rem;
  letter-spacing: 0.05em;
}''',
'''.contact-form input::placeholder,
.contact-form textarea::placeholder {
  color: rgba(245, 240, 232, 0.3);
  font-size: 0.9rem;
  letter-spacing: 0.04em;
}'''
)

# Upgrade 8
css = css.replace(
'''.map-container {
  width: 100%;
  height: 400px;
  margin-top: 0;
  border-top: 1px solid rgba(245, 240, 232, 0.08);
}

.map-container iframe {
  width: 100%;
  height: 100%;
  border: 0;
  filter: grayscale(100%) contrast(1.1) brightness(0.8);
}''',
'''.map-container {
  width: 100%;
  height: 420px;
  border-top: 1px solid rgba(245, 240, 232, 0.06);
}

.map-container iframe {
  width: 100%;
  height: 100%;
  border: 0;
  display: block;
  filter: grayscale(100%) contrast(1.05) brightness(0.75);
}'''
)

# Upgrade 9
css = css.replace(
'''.mobile-nav a {
  font-size: 2rem;
  font-family: var(--font-serif);
  letter-spacing: -0.02em;
  border-bottom: 1px solid rgba(245, 240, 232, 0.08);
  padding-bottom: var(--spacing-sm);
}''',
'''.mobile-nav a:not(.btn) {
  font-size: clamp(1.75rem, 6vw, 2.5rem);
  font-family: var(--font-serif);
  letter-spacing: -0.02em;
  padding-bottom: var(--spacing-sm);
  border-bottom: 1px solid rgba(245, 240, 232, 0.08);
  width: 100%;
}'''
)

# Upgrade 10
css = css.replace(
'''.section + .section-dark,
.section-dark + .section {
  position: relative;
}
.section + .section-dark::before,
.section-dark + .section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: rgba(200, 184, 154, 0.2);
}''',
'''.section-dark + .section,
.section + .section-dark {
  position: relative;
}

.section-dark + .section::before,
.section + .section-dark::before {
  content: '';
  position: absolute;
  top: 0;
  left: 10%;
  right: 10%;
  height: 1px;
  background: rgba(200, 184, 154, 0.15);
}'''
)

# Upgrade 11
css = css.replace(
'''.footer-col a:hover {
  color: var(--color-stone);
  text-decoration: underline;
  text-underline-offset: 3px;
}''',
'''.footer-col a {
  text-underline-offset: 3px;
  transition: color var(--transition-base);
}

.footer-col a:hover {
  color: var(--color-stone);
  text-decoration: underline;
}'''
)

# Write CSS
with open(css_path, 'w') as f:
    f.write(css)


js_path = 'js/main.js'
with open(js_path, 'r') as f:
    js = f.read()

# JS Upgrade 2
js = js.replace(
'''  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a, .mobile-nav a').forEach(link => {
    if (link.getAttribute('href') === currentPage) {
      link.classList.add('nav-active');
    }
  });''',
'''  const currentPage = window.location.pathname.replace(/\/$/, '').split('/').pop() || 'index';
  document.querySelectorAll('.nav-links a').forEach(link => {
    const href = link.getAttribute('href') || '';
    const linkPage = href.replace('.html', '').replace(/^\//, '');
    if (
      (currentPage === '' || currentPage === 'index') && (linkPage === '' || linkPage === 'index.html' || linkPage === 'index') ||
      (currentPage !== '' && currentPage !== 'index' && linkPage.includes(currentPage))
    ) {
      link.classList.add('nav-active');
    }
  });'''
)

# JS Upgrade 3
js = js.replace(
'''  const revealObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    });
  }, revealOptions);

  allReveal.forEach(el => {
    revealObserver.observe(el);
  });''',
'''  const revealObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    });
  }, {
    threshold: 0.12,
    rootMargin: '0px 0px -40px 0px'
  });

  allReveal.forEach(el => revealObserver.observe(el));'''
)

# JS Upgrade 4
js = js.replace(
'''  const animateTitle = document.querySelector('.hero-animate-title');
  if (animateTitle) {
    const words = animateTitle.innerText.split(' ');
    animateTitle.innerHTML = '';
    words.forEach((word, index) => {
      const span = document.createElement('span');
      span.innerText = word;
      // Increased stagger speed: 0.08s per word, base delay 0.2s
      span.style.animationDelay = `${0.2 + (index * 0.08)}s`;
      animateTitle.appendChild(span);
      // Append an actual space to ensure proper spacing between words
      animateTitle.appendChild(document.createTextNode(' '));
    });
  }''',
'''  const animateTitles = document.querySelectorAll('.hero-animate-title');
  animateTitles.forEach(animateTitle => {
    const words = animateTitle.innerText.trim().split(' ');
    animateTitle.innerHTML = '';
    words.forEach((word, index) => {
      const span = document.createElement('span');
      span.textContent = word + '\\u00A0'; // non-breaking space
      span.style.animationDelay = `${0.4 + (index * 0.12)}s`;
      animateTitle.appendChild(span);
    });
  });'''
)

# Write JS
with open(js_path, 'w') as f:
    f.write(js)

