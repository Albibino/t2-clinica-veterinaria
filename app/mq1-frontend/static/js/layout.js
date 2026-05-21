function buildLayout(pageTitle) {
  Auth.requireAuth();

  const layout = `
    <div class="app-wrapper">

      <!-- SIDEBAR -->
      <aside class="sidebar" id="sidebar">
        <div class="sidebar-logo">
          <div class="logo-icon">🐾</div>
          <h2>VetClínica</h2>
          <span>Sistema de Gestão</span>
        </div>

        <nav class="sidebar-nav">
          <div class="nav-section-label">Principal</div>

          <a class="nav-item" data-href="dashboard" href="/dashboard.html">
            <span class="nav-icon">🏠</span>
            <span>Dashboard</span>
          </a>

          <div class="nav-section-label" style="margin-top:8px">Pacientes</div>

          <a class="nav-item" data-href="animais" href="/animais.html">
            <span class="nav-icon">🐾</span>
            <span>Animais</span>
          </a>

          <div class="nav-section-label" style="margin-top:8px">Atendimento</div>

          <a class="nav-item" data-href="consultas" href="/consultas.html">
            <span class="nav-icon">📋</span>
            <span>Consultas</span>
          </a>

          <a class="nav-item" data-href="nova-consulta" href="/nova-consulta.html">
            <span class="nav-icon">➕</span>
            <span>Nova Consulta</span>
          </a>
        </nav>

        <div class="sidebar-footer">
          <button class="btn-logout" id="btn-logout">
            <span>🚪</span>
            <span>Sair do Sistema</span>
          </button>
        </div>
      </aside>

      <!-- CONTEÚDO PRINCIPAL -->
      <div class="main-content">

        <!-- TOPBAR -->
        <header class="topbar">
          <h1 class="topbar-title" id="topbar-title">${pageTitle}</h1>
          <div class="topbar-right">
            <div class="topbar-user">
              <div class="topbar-avatar" id="topbar-avatar">A</div>
              <span class="topbar-username" id="topbar-username">Admin</span>
            </div>
          </div>
        </header>

        <!-- ÁREA DA PÁGINA -->
        <main class="page-content" id="page-content">
          <!-- Conteúdo dinâmico será inserido aqui -->
        </main>
      </div>

    </div>

    <!-- TOAST CONTAINER -->
    <div class="toast-container" id="toast-container"></div>
  `;

  document.body.innerHTML = layout;
  Toast.container = document.getElementById('toast-container');
}
