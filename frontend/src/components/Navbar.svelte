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
    Moon 
  } from 'lucide-svelte';
  import { theme } from '../lib/theme.svelte';
  import { admin } from '../lib/admin.svelte';
  import { router } from '../lib/router.svelte';
  import Sidebar from './Sidebar.svelte';

  let mobileMenuOpen = $state(false);
  const currentYear = new Date().getFullYear();
</script>

<header class="sticky top-0 z-30 bg-white/90 dark:bg-slate-900/90 backdrop-blur border-b border-slate-200 dark:border-slate-800 h-16 flex items-center px-4 sm:px-6 justify-between transition-colors">
  <div class="flex items-center gap-3">
    <button
      type="button"
      onclick={() => mobileMenuOpen = true}
      class="md:hidden p-2 rounded-lg text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800 cursor-pointer"
      aria-label="Buka Menu"
    >
      <Menu class="h-5 w-5" />
    </button>

    <div class="flex items-center gap-2">
      <span class="hidden sm:inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-red-50 text-red-700 border border-red-200 dark:bg-red-950/40 dark:text-red-300 dark:border-red-800">
        <Sparkles class="h-3 w-3" />
        Sistem Otomasi Layanan Sekretariat FIT
      </span>
    </div>
  </div>

  <div class="flex items-center gap-2.5">
    <!-- Theme Toggle -->
    <button
      onclick={() => theme.toggle()}
      class="p-2 rounded-lg text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
      aria-label="Ganti Tema"
      title={theme.isDark ? "Ganti ke Mode Terang" : "Ganti ke Mode Gelap"}
    >
      {#if theme.isDark}
        <Sun class="w-4 h-4 text-amber-400" />
      {:else}
        <Moon class="w-4 h-4 text-slate-600" />
      {/if}
    </button>

    <!-- Admin Status / Login -->
    {#if admin.isAdmin}
      <div class="flex items-center gap-1.5 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/60 px-3 py-1.5 rounded-lg text-xs font-bold text-emerald-700 dark:text-emerald-300 shadow-xs">
        <ShieldCheck class="h-4 w-4 text-emerald-600" />
        <span class="hidden sm:inline">Admin Sekretariat</span>
        <button
          onclick={() => admin.logout()}
          title="Keluar dari Mode Admin"
          class="ml-1 sm:ml-2 p-0.5 text-slate-400 hover:text-red-600 dark:hover:text-red-400 transition-colors cursor-pointer"
        >
          <LogOut class="h-3.5 w-3.5" />
        </button>
      </div>
    {:else}
      <button
        onclick={() => admin.openLoginModal()}
        class="inline-flex items-center gap-1.5 text-xs text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white px-2.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all cursor-pointer font-medium"
        title="Masuk sebagai Admin Sekretariat"
      >
        <Lock class="h-3.5 w-3.5 text-slate-400" />
        <span class="hidden sm:inline">Masuk Admin</span>
      </button>
    {/if}

    <div class="hidden lg:flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400 bg-slate-100 dark:bg-slate-800/60 px-3 py-1.5 rounded-lg border border-slate-200/80 dark:border-slate-700">
      <Calendar class="h-3.5 w-3.5 text-slate-500" />
      <span>Tahun: <strong class="text-slate-700 dark:text-slate-200">{currentYear}</strong></span>
    </div>

    <!-- Quick Action Button -->
    <button
      onclick={() => router.navigate('/generator')}
      class="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-red-600 hover:bg-red-700 text-white text-xs sm:text-sm font-semibold shadow-sm shadow-red-600/20 transition-all active:scale-95 cursor-pointer"
    >
      <Plus class="h-4 w-4" />
      <span>Buat Nomor Surat</span>
    </button>
  </div>
</header>

<!-- Mobile Drawer -->
{#if mobileMenuOpen}
  <div class="fixed inset-0 z-50 flex md:hidden">
    <div
      class="fixed inset-0 bg-slate-900/60 backdrop-blur-xs transition-opacity"
      onclick={() => mobileMenuOpen = false}
    ></div>
    <div class="relative flex-1 flex flex-col max-w-xs w-full bg-slate-900 shadow-2xl">
      <Sidebar onCloseMobile={() => mobileMenuOpen = false} />
    </div>
  </div>
{/if}
