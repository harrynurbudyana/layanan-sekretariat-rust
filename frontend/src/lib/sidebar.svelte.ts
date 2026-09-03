class SidebarManager {
  isOpen = $state(true);
  isMobileOpen = $state(false);

  constructor() {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('fit-sidebar-open');
      if (saved !== null) {
        this.isOpen = saved === 'true';
      }
    }
  }

  toggle() {
    this.isOpen = !this.isOpen;
    if (typeof window !== 'undefined') {
      localStorage.setItem('fit-sidebar-open', this.isOpen ? 'true' : 'false');
    }
  }

  openMobile() {
    this.isMobileOpen = true;
  }

  closeMobile() {
    this.isMobileOpen = false;
  }

  toggleMobile() {
    this.isMobileOpen = !this.isMobileOpen;
  }
}

export const sidebarState = new SidebarManager();
