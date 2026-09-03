class ThemeManager {
  isDark = $state(false);

  constructor() {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('fit-theme');
      if (stored === 'dark' || (!stored && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        this.isDark = true;
        document.documentElement.classList.add('dark');
      } else {
        this.isDark = false;
        document.documentElement.classList.remove('dark');
      }
    }
  }

  toggle() {
    this.isDark = !this.isDark;
    if (this.isDark) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('fit-theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('fit-theme', 'light');
    }
  }
}

export const theme = new ThemeManager();
