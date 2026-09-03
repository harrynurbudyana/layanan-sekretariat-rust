<script lang="ts">
  import { 
    LayoutDashboard, 
    FilePlus2, 
    BookOpenCheck, 
    CalendarDays, 
    HelpCircle, 
    Database, 
    Building2,
    PanelLeftClose
  } from 'lucide-svelte';
  import { router } from '../lib/router.svelte';
  import { sidebarState } from '../lib/sidebar.svelte';
  import { cn } from '../lib/utils';

  let { onCloseMobile }: { onCloseMobile?: () => void } = $props();

  const navigation = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Buat Nomor Surat', href: '/generator', icon: FilePlus2, badge: 'Instan' },
    { name: 'Buku Agenda Surat', href: '/agenda', icon: BookOpenCheck, badge: 'Sekretariat' },
    { name: 'Peminjaman Ruangan', href: '/ruangan', icon: CalendarDays, badge: 'Baru' },
    { name: 'Panduan Format', href: '/panduan', icon: HelpCircle },
    { name: 'Master Data', href: '/master', icon: Database },
  ];

  function handleNav(href: string) {
    router.navigate(href);
    if (onCloseMobile) {
      onCloseMobile();
    } else {
      sidebarState.closeMobile();
    }
  }

  function handleCollapse() {
    if (onCloseMobile) {
      onCloseMobile();
    } else if (window.innerWidth < 768) {
      sidebarState.closeMobile();
    } else {
      sidebarState.toggle();
    }
  }
</script>

<aside class="w-64 bg-slate-900 text-slate-100 flex flex-col h-full border-r border-slate-800 shrink-0 select-none">
  <!-- Brand Header -->
  <div class="p-4 sm:p-5 border-b border-slate-800 flex items-center justify-between">
    <div class="flex items-center gap-3">
      <div class="h-10 w-10 rounded-xl bg-gradient-to-tr from-red-600 to-amber-500 flex items-center justify-center font-bold text-white shadow-md shadow-red-500/20 shrink-0">
        <Building2 class="h-5 w-5 text-white" />
      </div>
      <div>
        <h1 class="font-bold text-base leading-tight tracking-tight text-white flex items-center gap-1.5">
          FIT E-Office
        </h1>
        <p class="text-xs text-slate-400 font-medium">
          Fakultas Ilmu Terapan
        </p>
      </div>
    </div>

    <!-- Collapse / Hide Button -->
    <button
      type="button"
      onclick={handleCollapse}
      class="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
      title="Sembunyikan Sidebar"
      aria-label="Sembunyikan Sidebar"
    >
      <PanelLeftClose class="w-5 h-5" />
    </button>
  </div>

  <!-- Navigation Links -->
  <div class="flex-1 py-6 px-3 space-y-1.5 overflow-y-auto">
    <div class="px-3 pb-2 text-[11px] font-semibold tracking-wider text-slate-400 uppercase">
      Menu Utama
    </div>

    {#each navigation as item}
      {@const isActive = router.currentPath === item.href}
      {@const Icon = item.icon}
      <button
        type="button"
        onclick={() => handleNav(item.href)}
        class={cn(
          "w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 group cursor-pointer text-left",
          isActive
            ? "bg-red-600/15 text-red-400 border border-red-500/30 font-semibold shadow-sm"
            : "text-slate-300 hover:bg-slate-800/80 hover:text-white"
        )}
      >
        <div class="flex items-center gap-3">
          <Icon
            class={cn(
              "h-4.5 w-4.5 transition-colors",
              isActive ? "text-red-400" : "text-slate-400 group-hover:text-slate-200"
            )}
          />
          <span>{item.name}</span>
        </div>

        {#if item.badge}
          <span class="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
            {item.badge}
          </span>
        {/if}
      </button>
    {/each}
  </div>

  <!-- Footer Info -->
  <div class="p-4 border-t border-slate-800 bg-slate-950/50">
    <div class="flex items-center justify-between text-xs text-slate-400 mb-1">
      <span class="font-semibold text-slate-300">Sekretariat FIT</span>
      <span class="text-[10px] bg-red-950 text-red-400 font-mono px-1.5 py-0.5 rounded border border-red-800/40">Rust+Svelte</span>
    </div>
    <p class="text-[11px] text-slate-400 line-clamp-1">
      Layanan Administrasi Mandiri
    </p>
  </div>
</aside>
