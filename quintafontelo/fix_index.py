with open('index.html', 'r') as f:
    html = f.read()

# 1. Replace Hero
old_hero = """    <!-- Hero Section -->
    <header class="hero">
        <div class="hero-bg" style="background-image: url('https://quintafontelo.pt/wp-content/uploads/2025/06/473079078_122099888840721529_1802886727581582746_n.jpg');"></div>
        <div class="hero-overlay"></div>
        <div class="hero-content">
            <h1 class="hero-animate-title">Um refúgio em plena natureza.</h1>
            <p>Vouzela, Portugal</p>
            <a href="espaco.html" class="btn btn-ghost">Descubra a Quinta</a>
        </div>
    </header>"""

new_hero = """    <!-- Hero Section -->
    <header class="hero">
      <div class="hero-bg" id="heroBg" style="background-image: url('https://quintafontelo.pt/wp-content/uploads/2025/06/473079078_122099888840721529_1802886727581582746_n.jpg');"></div>
      <div class="hero-overlay"></div>
      <div class="hero-content">
        <div class="hero-badge">169298/AL — Vouzela, Portugal</div>
        <h1 class="hero-animate-title">Um refúgio em plena natureza.</h1>
        <p class="hero-sub">Quinta do Fontelo</p>
        <a href="contactos.html" class="btn btn-outline-light">Peça um Orçamento</a>
      </div>
      <div class="hero-scroll">
        <span>Scroll</span>
        <div class="hero-scroll-line"></div>
      </div>
    </header>"""
html = html.replace(old_hero, new_hero)

# 2. Intro Strip
old_intro = """    <!-- Intro Strip -->
    <section class="intro-strip reveal">
        <div class="container">
            <h2>"Na serenidade de Vouzela, o conforto e a natureza convivem em perfeita harmonia."</h2>
            <div class="caption">169298/AL</div>
        </div>
    </section>"""

new_intro = """    <!-- Intro Strip -->
    <section class="intro-strip reveal">
      <div class="container">
        <blockquote>"Na serenidade de Vouzela, o conforto e a natureza convivem em perfeita harmonia."</blockquote>
        <p class="caption">169298/AL</p>
      </div>
    </section>"""
html = html.replace(old_intro, new_intro)

# 3. Services
import re

# We will use regex to replace the entire "O que oferecemos?" section.
# It starts at <!-- O que oferecemos? --> and ends before <!-- Espaço -->
pattern_services = re.compile(r'<!-- O que oferecemos\? -->.*?<!-- Espaço -->', re.DOTALL)

new_services = """<!-- O que oferecemos? -->
    <section class="section section-dark reveal">
      <div class="container">
        <div style="text-align:center; margin-bottom: var(--spacing-lg);">
          <p class="label text-stone" style="margin-bottom:1rem;">O que oferecemos</p>
          <h2>Experiências inesquecíveis</h2>
        </div>
      </div>
      <div class="img-card-grid">
        <a href="servicos.html" class="img-card reveal">
          <img src="https://quintafontelo.pt/wp-content/uploads/2025/07/472666406_122097428834721529_1238239777585649646_n.jpg" alt="Alojamento" loading="lazy">
          <div class="img-card-body">
            <span class="img-card-label">Serviço</span>
            <h3>Alojamento</h3>
            <p>Suites de conforto rodeadas de natureza e vistas sobre o vale de Vouzela. Suite Fontelo, Suite Gamardo, Suite Vouzela.</p>
            <span class="img-card-link">Ver mais</span>
          </div>
        </a>
        <a href="servicos.html" class="img-card reveal" style="transition-delay:0.15s;">
          <img src="https://quintafontelo.pt/wp-content/uploads/2025/07/479481073_122113260266721529_5971978976084935239_n.jpg" alt="Tours 4x4" loading="lazy">
          <div class="img-card-body">
            <span class="img-card-label">Serviço</span>
            <h3>Tours 4×4</h3>
            <p>Rotas turísticas e gastronómicas por caminhos fora de estrada pela região de Vouzela e arredores.</p>
            <span class="img-card-link">Ver mais</span>
          </div>
        </a>
        <a href="servicos.html" class="img-card reveal" style="transition-delay:0.3s;">
          <img src="https://quintafontelo.pt/wp-content/uploads/2025/07/474476946_122109075272721529_5187786905983082750_n.jpg" alt="Restaurante" loading="lazy">
          <div class="img-card-body">
            <span class="img-card-label">Em breve</span>
            <h3>Restaurante</h3>
            <p>Uma nova experiência gastronómica na Quinta do Fontelo. Fique atento.</p>
            <span class="img-card-link">Saber mais</span>
          </div>
        </a>
      </div>
    </section>

    <!-- Espaço -->"""
html = pattern_services.sub(new_services, html)


# 4. Espaco
pattern_espaco = re.compile(r'<!-- Espaço -->.*?<!-- Eventos -->', re.DOTALL)

new_espaco = """<!-- Espaço -->
    <section class="section section-dark reveal">
      <div class="container">
        <div class="editorial-split">
          <div class="editorial-split-image reveal-left">
            <img src="https://quintafontelo.pt/wp-content/uploads/2025/07/quarto.jpg" alt="Interior da Quinta do Fontelo" loading="lazy">
          </div>
          <div class="editorial-split-text reveal-right">
            <p class="label text-stone" style="margin-bottom: 1.5rem;">O Espaço</p>
            <h2 style="margin-bottom: var(--spacing-md);">Conforto e charme em plena natureza</h2>
            <p>Na Quinta do Fontelo, cada detalhe foi pensado para proporcionar conforto, tranquilidade e charme. Os nossos quartos e suites combinam materiais naturais, design contemporâneo e vistas inspiradoras.</p>
            <p>Dispõem de ar condicionado, minibar, casa de banho privativa, varanda ou terraço. Dispomos ainda de sala de estar ampla e sala de pequenos-almoços com vista para o jardim.</p>
            <a href="espaco.html" class="btn btn-outline-light" style="margin-top: var(--spacing-md);">Conhecer o Espaço</a>
          </div>
        </div>
      </div>
    </section>

    <!-- Eventos -->"""
html = pattern_espaco.sub(new_espaco, html)


# 5. Eventos
pattern_eventos = re.compile(r'<!-- Eventos -->.*?<!-- Footer -->', re.DOTALL)

new_eventos = """<!-- Eventos -->
    <section class="section reveal">
      <div class="container">
        <div style="text-align:center; margin-bottom: var(--spacing-lg);">
          <p class="label" style="margin-bottom:1rem; color: var(--color-muted);">Celebre connosco</p>
          <h2>Eventos</h2>
          <p style="max-width:600px; margin: 1rem auto 0; color: var(--color-muted);">O cenário perfeito para os seus momentos mais importantes.</p>
        </div>
        <div class="events-list">
          <a href="eventos.html" class="event-row reveal">
            <span class="event-number">01</span>
            <span class="event-name">Casamentos</span>
            <span class="event-arrow">→</span>
          </a>
          <a href="eventos.html" class="event-row reveal" style="transition-delay:0.08s;">
            <span class="event-number">02</span>
            <span class="event-name">Aniversários</span>
            <span class="event-arrow">→</span>
          </a>
          <a href="eventos.html" class="event-row reveal" style="transition-delay:0.16s;">
            <span class="event-number">03</span>
            <span class="event-name">Batizados e Comunhões</span>
            <span class="event-arrow">→</span>
          </a>
          <a href="eventos.html" class="event-row reveal" style="transition-delay:0.24s;">
            <span class="event-number">04</span>
            <span class="event-name">Eventos Corporativos</span>
            <span class="event-arrow">→</span>
          </a>
          <a href="eventos.html" class="event-row reveal" style="transition-delay:0.32s;">
            <span class="event-number">05</span>
            <span class="event-name">Jantares Temáticos e Privados</span>
            <span class="event-arrow">→</span>
          </a>
          <a href="eventos.html" class="event-row reveal" style="transition-delay:0.4s;">
            <span class="event-number">06</span>
            <span class="event-name">Sunsets</span>
            <span class="event-arrow">→</span>
          </a>
        </div>
        <div style="text-align:center; margin-top: var(--spacing-lg);">
          <a href="eventos.html" class="btn btn-primary">Ver todos os eventos</a>
        </div>
      </div>
    </section>

    <!-- Footer -->"""
html = pattern_eventos.sub(new_eventos, html)

with open('index.html', 'w') as f:
    f.write(html)
