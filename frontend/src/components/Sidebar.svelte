<script lang="ts">
  import { 
    LayoutDashboard, 
    FilePlus2, 
    BookOpenCheck, 
    CalendarDays, 
    HelpCircle, 
    Database, 
    Building2,
    PanelLeftClose,
    History
  } from 'lucide-svelte';
  import { router } from '../lib/router.svelte';
  import { sidebarState } from '../lib/sidebar.svelte';
  import { cn } from '../lib/utils';

  let { onCloseMobile }: { onCloseMobile?: () => void } = $props();

  const navigation = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Buat Nomor Surat', href: '/generator', icon: FilePlus2 },
    { name: 'Buku Agenda Surat', href: '/agenda', icon: BookOpenCheck },
    { name: 'Peminjaman Ruangan', href: '/ruangan', icon: CalendarDays },
    { name: 'Histori Saya', href: '/histori', icon: History },
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
    } else if (typeof window !== 'undefined' && window.innerWidth < 768) {
      sidebarState.closeMobile();
    } else {
      sidebarState.toggle();
    }
  }
</script>

<aside class="w-full md:w-72 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-100 flex flex-col h-full border-r border-slate-200 dark:border-slate-800 shrink-0 select-none transition-colors duration-200">
  <!-- Brand Header -->
  <div class="p-4 sm:p-5 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between gap-3">
    <div class="flex items-center gap-3 min-w-0">
      <div class="h-10 w-10 rounded-xl bg-gradient-to-tr from-red-600 to-amber-500 flex items-center justify-center font-bold text-white shadow-md shadow-red-500/20 shrink-0">
        <Building2 class="h-5 w-5 text-white" />
      </div>
      <div class="min-w-0">
        <h1 class="font-bold text-base leading-tight tracking-tight text-slate-900 dark:text-white truncate">
          FIT E-Office
        </h1>
        <p class="text-xs text-slate-500 dark:text-slate-400 font-medium truncate">
          Fakultas Ilmu Terapan
        </p>
      </div>
    </div>

    <!-- Collapse / Hide Button -->
    <button
      type="button"
      onclick={handleCollapse}
      class="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer shrink-0"
      title="Sembunyikan Sidebar"
      aria-label="Sembunyikan Sidebar"
    >
      <PanelLeftClose class="w-5 h-5" />
    </button>
  </div>

  <!-- Navigation Links -->
  <div class="flex-1 py-6 px-3 space-y-1.5 overflow-y-auto">
    <div class="px-3 pb-2 text-[11px] font-semibold tracking-wider text-slate-400 dark:text-slate-500 uppercase">
      Menu Utama
    </div>

    {#each navigation as item}
      {@const isActive = router.currentPath === item.href}
      {@const Icon = item.icon}
      <button
        type="button"
        onclick={() => handleNav(item.href)}
        class={cn(
          "w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 group cursor-pointer text-left",
          isActive
            ? "bg-red-50 dark:bg-red-600/15 text-red-600 dark:text-red-400 border border-red-200 dark:border-red-500/30 font-semibold shadow-xs"
            : "text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/80 hover:text-slate-900 dark:hover:text-white"
        )}
      >
        <Icon
          class={cn(
            "h-4.5 w-4.5 shrink-0 transition-colors",
            isActive ? "text-red-600 dark:text-red-400" : "text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-200"
          )}
        />
        <span class="truncate whitespace-nowrap">{item.name}</span>
      </button>
    {/each}
  </div>

  <!-- Footer Info -->
  <div class="p-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50/80 dark:bg-slate-950/50 transition-colors">
    <div class="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 mb-1">
      <span class="font-semibold text-slate-700 dark:text-slate-300">Sekretariat FIT</span>
    </div>
    <p class="text-[11px] text-slate-400 dark:text-slate-500 line-clamp-1">
      Layanan Administrasi Mandiri
    </p>
    <div class="mt-2.5 pt-2 border-t border-slate-200/60 dark:border-slate-800/60 flex items-center justify-between text-[11px] text-slate-400 dark:text-slate-500">
      <span>made by <a href="https://lawkidd.my.id" target="_blank" rel="noopener noreferrer" class="font-medium text-slate-600 dark:text-slate-300 hover:text-red-600 dark:hover:text-red-400 transition-colors">Lawkidd</a></span>
      <a 
        href="https://github.com/harrynurbudyana" 
        target="_blank" 
        rel="noopener noreferrer" 
        title="GitHub Profile (@harrynurbudyana)"
        class="inline-flex items-center gap-1 hover:text-slate-900 dark:hover:text-white transition-colors"
      >
        <img 
          src="/github-avatar.png" 
          alt="GitHub" 
          class="w-3.5 h-3.5 rounded-full ring-1 ring-slate-300 dark:ring-slate-700 object-cover" 
          onerror={(e) => { (e.currentTarget as HTMLImageElement).src = 'https://github.com/harrynurbudyana.png'; }}
        />
        <svg class="w-3 h-3" viewBox="0 0 24 24" fill="currentColor">
          <path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
        </svg>
      </a>
    </div>
  </div>
</aside>
