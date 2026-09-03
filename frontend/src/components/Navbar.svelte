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
    PanelLeftOpen
  } from 'lucide-svelte';
  import { theme } from '../lib/theme.svelte';
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
      class="p-2 rounded-xl text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all cursor-pointer flex items-center gap-1.5 border border-slate-200/80 dark:border-slate-700/80 shadow-2xs"
      aria-label="Toggle Sidebar"
      title={sidebarState.isOpen ? "Sembunyikan Sidebar" : "Tampilkan Sidebar"}
    >
      {#if sidebarState.isOpen}
        <PanelLeftClose class="h-5 w-5 text-slate-600 dark:text-slate-300" />
      {:else}
        <PanelLeftOpen class="h-5 w-5 text-red-600 dark:text-red-400" />
      {/if}
      <span class="hidden xl:inline text-xs font-semibold text-slate-500 dark:text-slate-400">
        {sidebarState.isOpen ? 'Sembunyikan' : 'Menu'}
      </span>
    </button>

    <div class="flex items-center gap-2">
      <span class="hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-red-50 text-red-700 border border-red-200 dark:bg-red-950/40 dark:text-red-300 dark:border-red-800">
        <Sparkles class="h-3.5 w-3.5 text-red-600 dark:text-red-400" />
        Sistem Otomasi Layanan Sekretariat FIT
      </span>
    </div>
  </div>

  <div class="flex items-center gap-2.5">
    <!-- Theme Toggle Button (Light / Dark) -->
    <button
      type="button"
      onclick={() => theme.toggle()}
      class="p-2 rounded-xl text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 border border-slate-200/80 dark:border-slate-700/80 transition-all cursor-pointer shadow-2xs flex items-center gap-1.5"
      aria-label="Ganti Tema Tampilan"
      title={theme.isDark ? "Ganti ke Mode Terang (Light Mode)" : "Ganti ke Mode Gelap (Dark Mode)"}
    >
      {#if theme.isDark}
        <Sun class="w-4 h-4 text-amber-400 animate-in spin-in-90 duration-200" />
        <span class="hidden lg:inline text-xs font-semibold text-slate-300">Terang</span>
      {:else}
        <Moon class="w-4 h-4 text-slate-600 animate-in spin-in-90 duration-200" />
        <span class="hidden lg:inline text-xs font-semibold text-slate-600">Gelap</span>
      {/if}
    </button>

    <!-- Admin Status / Login -->
    {#if admin.isAdmin}
      <div class="flex items-center gap-1.5 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/60 px-3 py-1.5 rounded-xl text-xs font-bold text-emerald-700 dark:text-emerald-300 shadow-2xs">
        <ShieldCheck class="h-4 w-4 text-emerald-600" />
        <span class="hidden sm:inline">Staf Sekretariat</span>
        <button
          type="button"
          onclick={() => admin.logout()}
          title="Kunci / Keluar Akses Staf"
          class="ml-1 sm:ml-2 p-1 text-slate-400 hover:text-red-600 dark:hover:text-red-400 transition-colors cursor-pointer rounded-lg hover:bg-red-50 dark:hover:bg-red-950/40"
        >
          <LogOut class="h-3.5 w-3.5" />
        </button>
      </div>
    {:else}
      <button
        type="button"
        onclick={() => admin.openLoginModal()}
        class="inline-flex items-center gap-1.5 text-xs text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all cursor-pointer font-medium shadow-2xs"
        title="Buka Akses Staf Sekretariat"
      >
        <Lock class="h-3.5 w-3.5 text-slate-400" />
        <span class="hidden sm:inline">Akses Staf</span>
      </button>
    {/if}

    <div class="hidden lg:flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400 bg-slate-100 dark:bg-slate-800/60 px-3 py-1.5 rounded-xl border border-slate-200/80 dark:border-slate-700">
      <Calendar class="h-3.5 w-3.5 text-slate-500" />
      <span>Tahun: <strong class="text-slate-700 dark:text-slate-200">{currentYear}</strong></span>
    </div>

    <!-- Quick Action Button -->
    <button
      type="button"
      onclick={() => router.navigate('/generator')}
      class="inline-flex items-center gap-1.5 px-3.5 sm:px-4 py-2 rounded-xl bg-red-600 hover:bg-red-700 text-white text-xs sm:text-sm font-bold shadow-sm shadow-red-600/25 transition-all active:scale-95 cursor-pointer"
    >
      <Plus class="h-4 w-4" />
      <span>Buat Nomor Surat</span>
    </button>
  </div>
</header>

<!-- Mobile Drawer -->
{#if sidebarState.isMobileOpen}
  <div class="fixed inset-0 z-50 flex md:hidden animate-in fade-in duration-150">
    <div
      class="fixed inset-0 bg-slate-900/60 backdrop-blur-xs transition-opacity"
      onclick={() => sidebarState.closeMobile()}
    ></div>
    <div class="relative flex-1 flex flex-col max-w-xs w-full bg-slate-900 shadow-2xl animate-in slide-in-from-left duration-200">
      <Sidebar onCloseMobile={() => sidebarState.closeMobile()} />
    </div>
  </div>
{/if}
