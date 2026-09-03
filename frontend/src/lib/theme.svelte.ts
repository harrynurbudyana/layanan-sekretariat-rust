class ThemeManager {
  isDark = $state(false);

  constructor() {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('fit-theme');
      // If dark is stored or no preference is stored, check or default
      if (stored === 'dark' || (!stored && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        this.applyTheme(true);
      } else {
        this.applyTheme(false);
      }
    }
  }

  applyTheme(dark: boolean) {
    this.isDark = dark;
    if (typeof window !== 'undefined') {
      if (dark) {
        document.documentElement.classList.add('dark');
        document.body.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
        document.body.classList.remove('dark');
      }
    }
  }

  toggle() {
    const nextState = !this.isDark;
    this.applyTheme(nextState);
    if (typeof window !== 'undefined') {
      localStorage.setItem('fit-theme', nextState ? 'dark' : 'light');
    }
  }
}

export const theme = new ThemeManager();
