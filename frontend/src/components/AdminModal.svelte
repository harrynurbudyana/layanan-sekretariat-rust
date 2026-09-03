<script lang="ts">
  import { admin } from '../lib/admin.svelte';
  import { Lock, ShieldCheck, X } from 'lucide-svelte';

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter') {
      admin.verifyPin();
    }
  }
</script>

{#if admin.isModalOpen}
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-xs animate-in fade-in duration-200">
    <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 max-w-sm w-full shadow-2xl relative">
      <button 
        onclick={() => admin.closeLoginModal()}
        class="absolute right-4 top-4 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1 rounded-lg cursor-pointer"
        aria-label="Tutup Modal"
      >
        <X class="w-5 h-5" />
      </button>

      <div class="flex items-center gap-3 mb-4">
        <div class="w-10 h-10 rounded-xl bg-red-100 dark:bg-red-950/60 text-red-600 dark:text-red-400 flex items-center justify-center">
          <ShieldCheck class="w-5 h-5" />
        </div>
        <div>
          <h3 class="text-base font-bold text-slate-900 dark:text-white">Masuk Mode Admin</h3>
          <p class="text-xs text-slate-500 dark:text-slate-400">Khusus staf Sekretariat FIT</p>
        </div>
      </div>

      <div class="space-y-3">
        <p class="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
          Masukkan PIN Admin untuk mengaktifkan fitur hapus surat, persetujuan ruangan, dan kelola master data.
        </p>

        <div>
          <label for="admin-pin-input" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
            PIN Keamanan
          </label>
          <div class="relative">
            <Lock class="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input 
              id="admin-pin-input"
              type="password"
              bind:value={admin.pin}
              onkeydown={handleKeydown}
              placeholder="Masukkan PIN Admin..."
              autofocus
              class="w-full pl-9 pr-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-red-500/40 focus:border-red-500"
            />
          </div>
        </div>

        {#if admin.error}
          <div class="p-2.5 rounded-lg bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 text-xs text-red-600 dark:text-red-300">
            {admin.error}
          </div>
        {/if}

        <div class="flex gap-2 pt-2">
          <button 
            onclick={() => admin.closeLoginModal()}
            class="flex-1 px-4 py-2 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 cursor-pointer"
          >
            Batal
          </button>
          <button 
            onclick={() => admin.verifyPin()}
            disabled={admin.loading}
            class="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 disabled:opacity-50 text-white rounded-xl text-xs font-bold shadow-sm shadow-red-600/30 cursor-pointer"
          >
            {admin.loading ? 'Memeriksa...' : 'Konfirmasi'}
          </button>
        </div>
      </div>
    </div>
  </div>
{/if}
