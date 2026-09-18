<script lang="ts">
  import { 
    Menu, 
    Sparkles, 
    ShieldCheck, 
    Lock, 
    LogOut, 
    Calendar, 
    Plus, 
    Sun, 
    Moon,
    PanelLeftClose,
    PanelLeftOpen,
    User,
    History
  } from 'lucide-svelte';
  import { theme } from '../lib/theme.svelte';
  import { auth } from '../lib/auth.svelte';
  import { admin } from '../lib/admin.svelte';
  import { router } from '../lib/router.svelte';
  import { sidebarState } from '../lib/sidebar.svelte';
  import Sidebar from './Sidebar.svelte';

  const currentYear = new Date().getFullYear();

  function handleToggleSidebar() {
    if (typeof window !== 'undefined' && window.innerWidth < 768) {
      sidebarState.toggleMobile();
    } else {
      sidebarState.toggle();
    }
  }
</script>

<header class="sticky top-0 z-30 bg-white/90 dark:bg-slate-900/90 backdrop-blur border-b border-slate-200 dark:border-slate-800 h-16 flex items-center px-4 sm:px-6 justify-between transition-colors">
  <div class="flex items-center gap-3">
    <!-- Responsive Sidebar Toggle Button (Desktop & Mobile) -->
    <button
      type="button"
      onclick={handleToggleSidebar}
      class="p-2 rounded-xl text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all cursor-pointer flex items-center gap-1.5 border border-slate-200/80 dark:border-slate-700/80 shadow-2xs h-9"
      aria-label="Toggle Sidebar"
      title={sidebarState.isOpen ? "Sembunyikan Sidebar" : "Tampilkan Sidebar"}
    >
      {#if sidebarState.isOpen}
        <PanelLeftClose size={18} class="w-4.5 h-4.5 text-slate-600 dark:text-slate-300 shrink-0" />
      {:else}
        <PanelLeftOpen size={18} class="w-4.5 h-4.5 text-red-600 dark:text-red-400 shrink-0" />
      {/if}
      <span class="hidden xl:inline text-xs font-semibold text-slate-500 dark:text-slate-400">
        {sidebarState.isOpen ? 'Sembunyikan' : 'Menu'}
      </span>
    </button>

    <div class="flex items-center gap-2">
      <span class="hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-red-50 text-red-700 border border-red-200 dark:bg-red-950/40 dark:text-red-300 dark:border-red-800 h-7">
        <Sparkles size={14} class="w-3.5 h-3.5 text-red-600 dark:text-red-400 shrink-0" />
        Sistem Otomasi Layanan Sekretariat FIT
      </span>
    </div>
  </div>

  <div class="flex items-center gap-2.5">
    <!-- Theme Toggle Button (Light / Dark) -->
    <button
      type="button"
      onclick={() => theme.toggle()}
      class="p-2 rounded-xl text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 border border-slate-200/80 dark:border-slate-700/80 transition-all cursor-pointer shadow-2xs flex items-center gap-1.5 h-9"
      aria-label="Ganti Tema Tampilan"
      title={theme.isDark ? "Ganti ke Mode Terang (Light Mode)" : "Ganti ke Mode Gelap (Dark Mode)"}
    >
      {#if theme.isDark}
        <Sun size={16} class="w-4 h-4 text-amber-400 shrink-0" />
        <span class="hidden lg:inline text-xs font-semibold text-slate-300">Terang</span>
      {:else}
        <Moon size={16} class="w-4 h-4 text-slate-600 shrink-0" />
        <span class="hidden lg:inline text-xs font-semibold text-slate-600">Gelap</span>
      {/if}
    </button>

    <!-- Google Auth Status / Login -->
    {#if auth.isAdmin}
      <div class="flex items-center gap-1.5 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/60 px-3 py-1 rounded-xl text-xs font-bold text-emerald-700 dark:text-emerald-300 shadow-2xs h-9">
        {#if auth.user?.picture}
          <img src={auth.user.picture} alt="" class="w-5 h-5 rounded-full object-cover shrink-0" />
        {:else}
          <ShieldCheck size={16} class="w-4 h-4 text-emerald-600 shrink-0" />
        {/if}
        <span class="hidden sm:inline">Staf Sekretariat</span>
        <button
          type="button"
          onclick={() => auth.logout()}
          title="Keluar dari Staf Sekretariat"
          class="ml-1 sm:ml-2 p-1 text-slate-400 hover:text-red-600 dark:hover:text-red-400 transition-colors cursor-pointer rounded-lg hover:bg-red-50 dark:hover:bg-red-950/40"
        >
          <LogOut size={14} class="w-3.5 h-3.5 shrink-0" />
        </button>
      </div>
    {:else if auth.isLoggedIn}
      <div class="flex items-center gap-1.5 bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 px-2.5 py-1 rounded-xl text-xs font-semibold text-slate-700 dark:text-slate-300 shadow-2xs h-9">
        {#if auth.user?.picture}
          <img src={auth.user.picture} alt="" class="w-5 h-5 rounded-full object-cover shrink-0" />
        {:else}
          <User size={15} class="w-3.5 h-3.5 text-slate-500 shrink-0" />
        {/if}
        <span class="hidden md:inline max-w-[100px] truncate">{auth.user?.name}</span>
        <button
          type="button"
          onclick={() => router.navigate('/histori')}
          title="Buka Histori Pengajuan Saya"
          class="ml-0.5 px-2 py-0.5 text-[11px] font-bold bg-white dark:bg-slate-700 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-600 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-600 transition-colors cursor-pointer"
        >
          Histori
        </button>
        <button
          type="button"
          onclick={() => auth.logout()}
          title="Keluar / Logout"
          class="p-1 text-slate-400 hover:text-red-600 dark:hover:text-red-400 transition-colors cursor-pointer rounded-lg hover:bg-red-50 dark:hover:bg-red-950/40"
        >
          <LogOut size={14} class="w-3.5 h-3.5 shrink-0" />
        </button>
      </div>
    {:else}
      <button
        type="button"
        onclick={() => auth.openLoginModal()}
        class="inline-flex items-center gap-2 text-xs text-slate-700 hover:text-slate-900 dark:text-slate-200 dark:hover:text-white px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800/90 hover:bg-slate-50 dark:hover:bg-slate-700/80 transition-all cursor-pointer font-semibold shadow-2xs h-9"
        title="Masuk dengan Akun Google"
      >
        <svg class="w-4 h-4 shrink-0" viewBox="0 0 24 24">
          <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
          <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
          <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
          <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
        </svg>
        <span class="hidden sm:inline">Masuk dengan Google</span>
        <span class="sm:hidden">Masuk</span>
      </button>
    {/if}

    <div class="hidden lg:flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400 bg-slate-100 dark:bg-slate-800/60 px-3 py-1.5 rounded-xl border border-slate-200/80 dark:border-slate-700 h-9">
      <Calendar size={14} class="w-3.5 h-3.5 text-slate-500 shrink-0" />
      <span>Tahun: <strong class="text-slate-700 dark:text-slate-200">{currentYear}</strong></span>
    </div>

    <!-- Quick Action Button -->
    <button
      type="button"
      onclick={() => router.navigate('/generator')}
      class="inline-flex items-center gap-1.5 px-3.5 sm:px-4 py-2 rounded-xl bg-red-600 hover:bg-red-700 text-white text-xs sm:text-sm font-bold shadow-sm shadow-red-600/25 transition-all active:scale-95 cursor-pointer h-9"
    >
      <Plus size={16} class="w-4 h-4 shrink-0" />
      <span>Buat Nomor Surat</span>
    </button>
  </div>
</header>

<!-- Mobile Drawer -->
{#if sidebarState.isMobileOpen}
  <div class="fixed inset-0 z-50 flex md:hidden animate-in fade-in duration-150">
    <button
      type="button"
      aria-label="Tutup menu navigasi"
      class="fixed inset-0 bg-slate-900/60 backdrop-blur-xs transition-opacity w-full h-full border-none p-0 cursor-default"
      onclick={() => sidebarState.closeMobile()}
    ></button>
    <div class="relative flex-1 flex flex-col max-w-[288px] w-full bg-white dark:bg-slate-900 shadow-2xl animate-in slide-in-from-left duration-200">
      <Sidebar onCloseMobile={() => sidebarState.closeMobile()} />
    </div>
  </div>
{/if}
