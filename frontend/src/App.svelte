<script lang="ts">
  import Sidebar from './components/Sidebar.svelte';
  import Navbar from './components/Navbar.svelte';
  import AdminModal from './components/AdminModal.svelte';
  import DashboardView from './views/DashboardView.svelte';
  import GeneratorView from './views/GeneratorView.svelte';
  import AgendaView from './views/AgendaView.svelte';
  import RuanganView from './views/RuanganView.svelte';
  import MasterView from './views/MasterView.svelte';
  import PanduanView from './views/PanduanView.svelte';
  import HistoriView from './views/HistoriView.svelte';
  import Footer from './components/Footer.svelte';
  import { router } from './lib/router.svelte';
  import { sidebarState } from './lib/sidebar.svelte';
  let scrollContainer = $state<HTMLDivElement | null>(null);

  $effect(() => {
    if (router.currentPath && scrollContainer) {
      scrollContainer.scrollTo({ top: 0, behavior: 'smooth' });
    }
  });
</script>

<div class="flex h-screen w-full overflow-hidden bg-slate-100 dark:bg-slate-950 text-slate-900 dark:text-slate-100 transition-colors font-sans selection:bg-red-600 selection:text-white">
  <!-- Desktop Sidebar (Bisa dimunculkan dan disembunyikan) -->
  {#if sidebarState.isOpen}
    <div class="hidden md:flex md:w-72 md:flex-col shrink-0 transition-all duration-200 h-full">
      <Sidebar />
    </div>
  {/if}

  <!-- Main Content Area -->
  <div class="flex flex-col flex-1 min-w-0 h-full overflow-hidden">
    <Navbar />
    <div bind:this={scrollContainer} class="flex-1 overflow-y-auto flex flex-col">
      <main class="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
        {#if router.currentPath === '/generator'}
          <GeneratorView />
        {:else if router.currentPath === '/agenda'}
          <AgendaView />
        {:else if router.currentPath === '/ruangan'}
          <RuanganView />
        {:else if router.currentPath === '/histori'}
          <HistoriView />
        {:else if router.currentPath === '/master'}
          <MasterView />
        {:else if router.currentPath === '/panduan'}
          <PanduanView />
        {:else}
          <DashboardView />
        {/if}
      </main>
    </div>
    <Footer />
  </div>
</div>

<!-- Admin PIN Verification Modal -->
<AdminModal />
