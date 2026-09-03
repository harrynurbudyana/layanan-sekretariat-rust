class Router {
  currentPath = $state(typeof window !== 'undefined' ? window.location.pathname : '/');

  constructor() {
    if (typeof window !== 'undefined') {
      window.addEventListener('popstate', () => {
        this.currentPath = window.location.pathname;
      });
    }
  }

  navigate(path: string) {
    if (typeof window !== 'undefined') {
      window.history.pushState({}, '', path);
      this.currentPath = path;
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }
}

export const router = new Router();
