import { auth } from './auth.svelte';

class AdminManager {
  // Delegated reactive properties to auth
  get isAdmin() {
    return auth.isAdmin;
  }

  get isModalOpen() {
    return auth.isModalOpen;
  }

  set isModalOpen(val: boolean) {
    auth.isModalOpen = val;
  }

  get error() {
    return auth.authError;
  }

  set error(val: string | null) {
    auth.authError = val;
  }

  get loading() {
    return auth.loading;
  }

  openLoginModal() {
    auth.openLoginModal();
  }

  closeLoginModal() {
    auth.closeLoginModal();
  }

  getAuthHeaders(): Record<string, string> {
    return auth.getAuthHeaders();
  }

  logout() {
    auth.logout();
  }
}

export const admin = new AdminManager();
export { auth };
