const API_BASE = '/api';

// ─────────────────────────────────────────
// AUTENTICAÇÃO
// ─────────────────────────────────────────
const Auth = {
  getToken() {
    return localStorage.getItem('vet_token');
  },
  getUser() {
    return localStorage.getItem('vet_user');
  },
  setAuth(token, username) {
    localStorage.setItem('vet_token', token);
    localStorage.setItem('vet_user', username);
  },
  clear() {
    localStorage.removeItem('vet_token');
    localStorage.removeItem('vet_user');
  },
  isLoggedIn() {
    return !!this.getToken();
  },
  requireAuth() {
    if (!this.isLoggedIn()) {
      window.location.href = '/login.html';
    }
  },
  logout() {
    this.clear();
    window.location.href = '/login.html';
  }
};

// ─────────────────────────────────────────
// API HELPER
// ─────────────────────────────────────────
const Api = {
  async request(method, endpoint, body = null, isFormData = false) {
    const token = Auth.getToken();
    const headers = {};

    if (token) headers['Authorization'] = `Bearer ${token}`;
    if (!isFormData && body) headers['Content-Type'] = 'application/json';

    const options = { method, headers };
    if (body) options.body = isFormData ? body : JSON.stringify(body);

    try {
      const res = await fetch(`${API_BASE}${endpoint}`, options);

      if (res.status === 401) {
        Auth.logout();
        return null;
      }

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || `Erro ${res.status}`);
      }

      return data;
    } catch (err) {
      if (err.name !== 'TypeError') throw err;
      throw new Error('Erro de conexão com o servidor');
    }
  },

  get(endpoint) {
    return this.request('GET', endpoint);
  },
  post(endpoint, body) {
    return this.request('POST', endpoint, body);
  },
  put(endpoint, body) {
    return this.request('PUT', endpoint, body);
  },
  delete(endpoint) {
    return this.request('DELETE', endpoint);
  },
  postForm(endpoint, formData) {
    return this.request('POST', endpoint, formData, true);
  },
  putForm(endpoint, formData) {
    return this.request('PUT', endpoint, formData, true);
  }
};

// ─────────────────────────────────────────
// TOAST NOTIFICATIONS
// ─────────────────────────────────────────
const Toast = {
  container: null,

  init() {
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.className = 'toast-container';
      document.body.appendChild(this.container);
    }
  },

  show(message, type = 'default', duration = 3500) {
    this.init();
    const icons = { success: '✓', error: '✗', warning: '⚠', default: 'ℹ' };
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span>${icons[type] || icons.default}</span> ${message}`;
    this.container.appendChild(toast);

    requestAnimationFrame(() => {
      requestAnimationFrame(() => toast.classList.add('show'));
    });

    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 400);
    }, duration);
  },

  success(msg) { this.show(msg, 'success'); },
  error(msg)   { this.show(msg, 'error', 4500); },
  warning(msg) { this.show(msg, 'warning'); },
};

// ─────────────────────────────────────────
// MODAL
// ─────────────────────────────────────────
const Modal = {
  open(id) {
    const overlay = document.getElementById(id);
    if (overlay) overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
  },
  close(id) {
    const overlay = document.getElementById(id);
    if (overlay) overlay.classList.remove('open');
    document.body.style.overflow = '';
  },
  closeAll() {
    document.querySelectorAll('.modal-overlay.open').forEach(m => {
      m.classList.remove('open');
    });
    document.body.style.overflow = '';
  }
};

// Fechar modal ao clicar no overlay
document.addEventListener('click', e => {
  if (e.target.classList.contains('modal-overlay')) {
    Modal.closeAll();
  }
});

// ─────────────────────────────────────────
// FORMATAÇÃO
// ─────────────────────────────────────────
const Format = {
  date(iso) {
    if (!iso) return '—';
    const d = new Date(iso);
    return d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' });
  },
  datetime(iso) {
    if (!iso) return '—';
    const d = new Date(iso);
    return d.toLocaleString('pt-BR', {
      day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit'
    });
  },
  datetimeInput(iso) {
    if (!iso) return '';
    const d = new Date(iso);
    const pad = n => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
  },
  peso(val) {
    if (!val && val !== 0) return '—';
    return `${parseFloat(val).toFixed(1)} kg`;
  },
  idade(anos) {
    if (!anos && anos !== 0) return '—';
    return anos === 1 ? '1 ano' : `${anos} anos`;
  }
};

// ─────────────────────────────────────────
// NAVEGAÇÃO ATIVA
// ─────────────────────────────────────────
function setActiveNav() {
  const path = window.location.pathname;
  document.querySelectorAll('.nav-item').forEach(item => {
    const href = item.getAttribute('data-href');
    if (href && path.includes(href)) {
      item.classList.add('active');
    }
  });
}

// ─────────────────────────────────────────
// INICIALIZAÇÃO
// ─────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  setActiveNav();

  // Exibe usuário na topbar
  const userEl = document.getElementById('topbar-username');
  if (userEl) userEl.textContent = Auth.getUser() || 'Admin';

  // Botão de logout
  const logoutBtn = document.getElementById('btn-logout');
  if (logoutBtn) logoutBtn.addEventListener('click', () => Auth.logout());

  // Badge avatar inicial
  const avatarEl = document.getElementById('topbar-avatar');
  if (avatarEl) {
    const user = Auth.getUser() || 'A';
    avatarEl.textContent = user.charAt(0).toUpperCase();
  }
});

// ─────────────────────────────────────────
// BADGE HELPERS
// ─────────────────────────────────────────
function statusBadge(status) {
  const map = {
    agendada:  { class: 'badge-agendada',  label: '📅 Agendada' },
    realizada: { class: 'badge-realizada', label: '✅ Realizada' },
    cancelada: { class: 'badge-cancelada', label: '❌ Cancelada' },
  };
  const s = map[status] || { class: 'badge-outros', label: status };
  return `<span class="badge ${s.class}">${s.label}</span>`;
}

function especieBadge(especie) {
  const e = especie?.toLowerCase();
  if (e === 'cachorro') return `<span class="badge badge-cachorro">🐶 Cachorro</span>`;
  if (e === 'gato')     return `<span class="badge badge-gato">🐱 Gato</span>`;
  return `<span class="badge badge-outros">🐾 ${especie}</span>`;
}

function animalAvatar(foto, nome) {
  if (foto) {
    return `<img src="${foto}" alt="${nome}" class="animal-avatar" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'">
            <div class="animal-avatar-placeholder" style="display:none">🐾</div>`;
  }
  return `<div class="animal-avatar-placeholder">🐾</div>`;
}
