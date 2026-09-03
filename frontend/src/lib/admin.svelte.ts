class AdminManager {
  isAdmin = $state(false);
  isModalOpen = $state(false);
  pin = $state('');
  error = $state<string | null>(null);
  loading = $state(false);

  constructor() {
    if (typeof window !== 'undefined') {
      const saved = sessionStorage.getItem('fit-admin-session');
      if (saved === 'active') {
        this.isAdmin = true;
      }
    }
  }

  openLoginModal() {
    this.pin = '';
    this.error = null;
    this.isModalOpen = true;
  }

  closeLoginModal() {
    this.isModalOpen = false;
    this.pin = '';
    this.error = null;
  }

  async verifyPin() {
    if (!this.pin.trim()) {
      this.error = 'Masukkan PIN admin terlebih dahulu.';
      return;
    }
    this.loading = true;
    this.error = null;
    try {
      const res = await fetch('/api/admin/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pin: this.pin.trim() })
      });
      const data = await res.json();
      if (data.success) {
        this.isAdmin = true;
        sessionStorage.setItem('fit-admin-session', 'active');
        this.closeLoginModal();
      } else {
        this.error = data.error || 'PIN admin salah.';
      }
    } catch (e: any) {
      this.error = 'Gagal menghubungi server.';
    } finally {
      this.loading = false;
    }
  }

  logout() {
    this.isAdmin = false;
    sessionStorage.removeItem('fit-admin-session');
  }
}

export const admin = new AdminManager();
