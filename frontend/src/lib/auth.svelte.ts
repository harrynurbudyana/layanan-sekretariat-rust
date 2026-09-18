export interface UserProfile {
  email: string;
  name: string;
  picture?: string | null;
  role: 'admin' | 'user';
}

export interface AuthConfig {
  googleClientId?: string | null;
  adminEmails: string;
}

class AuthManager {
  user = $state<UserProfile | null>(null);
  token = $state<string | null>(null);
  loading = $state(false);
  isModalOpen = $state(false);
  authError = $state<string | null>(null);
  config = $state<AuthConfig>({
    googleClientId: null,
    adminEmails: 'sekretariat@tass.telkomuniversity.ac.id'
  });

  isAdmin = $derived(this.user?.role === 'admin');
  isLoggedIn = $derived(this.user !== null);

  constructor() {
    if (typeof window !== 'undefined') {
      const savedToken = localStorage.getItem('fit-auth-token') || sessionStorage.getItem('fit-auth-token');
      const savedUser = localStorage.getItem('fit-auth-user') || sessionStorage.getItem('fit-auth-user');
      if (savedToken && savedUser) {
        try {
          this.token = savedToken;
          this.user = JSON.parse(savedUser);
        } catch (e) {
          // Ignore json parse error
        }
      }
      this.fetchConfig();
      this.verifySession();
    }
  }

  async fetchConfig() {
    try {
      const res = await fetch('/api/auth/config');
      if (res.ok) {
        this.config = await res.json();
      }
    } catch (e) {
      console.warn('Failed to fetch auth config', e);
    }
  }

  async verifySession() {
    if (!this.token) return;
    try {
      const res = await fetch('/api/auth/me', {
        headers: this.getAuthHeaders()
      });
      if (res.ok) {
        const data = await res.json();
        if (data.authenticated && data.user) {
          this.user = data.user;
          localStorage.setItem('fit-auth-user', JSON.stringify(data.user));
          sessionStorage.setItem('fit-auth-user', JSON.stringify(data.user));
        } else {
          this.clearStorage();
        }
      }
    } catch (e) {
      // Offline / server error, keep existing session state
    }
  }

  getAuthHeaders(): Record<string, string> {
    if (this.token) {
      return {
        'Authorization': `Bearer ${this.token}`,
        'x-auth-token': this.token
      };
    }
    return {};
  }

  openLoginModal() {
    this.authError = null;
    this.isModalOpen = true;
  }

  closeLoginModal() {
    this.isModalOpen = false;
    this.authError = null;
  }

  setSession(token: string, user: UserProfile) {
    this.token = token;
    this.user = user;
    if (typeof window !== 'undefined') {
      localStorage.setItem('fit-auth-token', token);
      localStorage.setItem('fit-auth-user', JSON.stringify(user));
      sessionStorage.setItem('fit-auth-token', token);
      sessionStorage.setItem('fit-auth-user', JSON.stringify(user));
      
      // Backward compatibility flags
      if (user.role === 'admin') {
        localStorage.setItem('fit-admin-session', 'active');
        sessionStorage.setItem('fit-admin-session', 'active');
      } else {
        localStorage.removeItem('fit-admin-session');
        sessionStorage.removeItem('fit-admin-session');
      }
    }
    this.closeLoginModal();
  }

  clearStorage() {
    this.token = null;
    this.user = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('fit-auth-token');
      localStorage.removeItem('fit-auth-user');
      localStorage.removeItem('fit-admin-session');
      sessionStorage.removeItem('fit-auth-token');
      sessionStorage.removeItem('fit-auth-user');
      sessionStorage.removeItem('fit-admin-session');
    }
  }

  async loginWithGoogle(credential: string) {
    this.loading = true;
    this.authError = null;
    try {
      const res = await fetch('/api/auth/google', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ credential })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        this.setSession(data.token, data.user);
        return { success: true, user: data.user };
      } else {
        this.authError = data.error || 'Autentikasi Google gagal.';
        return { success: false, error: this.authError };
      }
    } catch (e: any) {
      this.authError = e?.message || 'Gagal menghubungi server autentikasi.';
      return { success: false, error: this.authError };
    } finally {
      this.loading = false;
    }
  }

  async logout() {
    if (this.token) {
      try {
        await fetch('/api/auth/logout', {
          method: 'POST',
          headers: this.getAuthHeaders()
        });
      } catch (e) {
        // ignore
      }
    }
    this.clearStorage();
  }
}

export const auth = new AuthManager();
