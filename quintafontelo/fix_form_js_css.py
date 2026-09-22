js_path = 'js/main.js'
with open(js_path, 'r') as f:
    js = f.read()

old_form = '''  const contactForm = document.getElementById('contact-form');
  if (contactForm) {
    contactForm.addEventListener('submit', e => {
      e.preventDefault();
      const btn = contactForm.querySelector('button[type="submit"]');
      btn.textContent = 'A enviar...';
      btn.disabled = true;
      setTimeout(() => {
        contactForm.innerHTML = `
          <div class="form-success">
            <i class="fa-solid fa-check" style="font-size:2rem; color: var(--color-stone); display:block; margin-bottom:1rem;"></i>
            <p style="font-family: var(--font-serif); font-size:1.5rem; color: var(--color-stone);">Mensagem enviada!</p>
            <p style="opacity:0.7; margin-top:0.5rem;">Em breve entraremos em contacto consigo.</p>
          </div>`;
      }, 500); // Sped up the success message delay
    });
  }'''

new_form = '''  const contactForm = document.getElementById('contact-form');
  if (contactForm) {
    contactForm.addEventListener('submit', e => {
      e.preventDefault();
      const btn = contactForm.querySelector('button[type="submit"]');
      const originalText = btn.textContent;
      btn.textContent = 'A enviar...';
      btn.disabled = true;
      setTimeout(() => {
        contactForm.style.transition = 'opacity 0.4s ease';
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
  }'''

js = js.replace(old_form, new_form)

with open(js_path, 'w') as f:
    f.write(js)

css_path = 'css/style.css'
with open(css_path, 'r') as f:
    css = f.read()

old_success = '''.form-success {
  text-align: center;
  padding: var(--spacing-xl) var(--spacing-md);
}'''

new_success = '''.form-success {
  text-align: center;
  padding: var(--spacing-xl) var(--spacing-md);
}

.form-success i {
  font-size: 2.5rem;
  color: var(--color-stone);
  display: block;
  margin-bottom: var(--spacing-md);
}

.form-success-title {
  font-family: var(--font-serif);
  font-size: 2rem;
  color: var(--color-stone);
  margin-bottom: 0.5rem;
}

.form-success-sub {
  opacity: 0.6;
  font-size: 1rem;
}'''

css = css.replace(old_success, new_success)

with open(css_path, 'w') as f:
    f.write(css)

