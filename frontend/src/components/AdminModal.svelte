<script lang="ts">
  import { auth } from '../lib/auth.svelte';
  import { ShieldCheck, X, AlertCircle, RefreshCw } from 'lucide-svelte';

  function handleGoogleButtonRender() {
    if (typeof window !== 'undefined' && (window as any).google?.accounts?.id && auth.config.googleClientId) {
      const container = document.getElementById('google-signin-btn-target');
      if (container) {
        container.innerHTML = '';
        (window as any).google.accounts.id.initialize({
          client_id: auth.config.googleClientId,
          callback: (response: any) => {
            if (response.credential) {
              auth.loginWithGoogle(response.credential);
            }
          }
        });
        (window as any).google.accounts.id.renderButton(container, {
          theme: 'outline',
          size: 'large',
          text: 'signin_with',
          shape: 'pill',
          width: 300,
          locale: 'id'
        });
      }
    }
  }

  $effect(() => {
    if (auth.isModalOpen) {
      setTimeout(() => {
        handleGoogleButtonRender();
      }, 50);
    }
  });
</script>

{#if auth.isModalOpen}
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/65 backdrop-blur-xs animate-in fade-in duration-200">
    <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 sm:p-7 max-w-md w-full shadow-2xl relative">
      <!-- Close Button -->
      <button 
        onclick={() => auth.closeLoginModal()}
        class="absolute right-4 top-4 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1.5 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 cursor-pointer transition-colors"
        aria-label="Tutup Modal"
      >
        <X class="w-5 h-5" />
      </button>

      <!-- Modal Header -->
      <div class="flex items-center gap-3.5 mb-5">
        <div class="w-11 h-11 rounded-2xl bg-gradient-to-tr from-red-600 to-amber-500 text-white flex items-center justify-center shadow-md shadow-red-500/20 shrink-0">
          <ShieldCheck class="w-6 h-6" />
        </div>
        <div>
          <h3 class="text-base font-bold text-slate-900 dark:text-white leading-tight">
            Autentikasi Akun Google
          </h3>
          <p class="text-xs text-slate-500 dark:text-slate-400">
            Layanan Sekretariat Fakultas Ilmu Terapan
          </p>
        </div>
      </div>

      <!-- Role Guidance Cards -->
      <div class="space-y-2.5 mb-5 text-xs">
        <div class="p-3.5 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/60 flex items-start gap-2.5">
          <div class="w-2 h-2 rounded-full bg-emerald-500 shrink-0 mt-1.5"></div>
          <div class="text-emerald-900 dark:text-emerald-200 leading-relaxed">
            <strong class="font-bold text-emerald-800 dark:text-emerald-300 block mb-0.5">
              Staf Sekretariat:
            </strong>
            Wajib masuk dengan akun <code class="font-mono bg-emerald-100 dark:bg-emerald-900/60 px-1 py-0.5 rounded text-[11px] font-bold">sekretariat@tass.telkomuniversity.ac.id</code> untuk mengakses Buku Agenda, Mode Manual, Approval Ruangan, & Master Data.
          </div>
        </div>

        <div class="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/80 flex items-start gap-2.5">
          <div class="w-2 h-2 rounded-full bg-blue-500 shrink-0 mt-1.5"></div>
          <div class="text-slate-700 dark:text-slate-300 leading-relaxed">
            <strong class="font-bold text-slate-800 dark:text-slate-200 block mb-0.5">
              Pengguna / Pemohon:
            </strong>
            Masuk dengan akun Google Anda untuk memantau riwayat nomor surat & status peminjaman ruangan di menu <strong>Histori Saya</strong>.
          </div>
        </div>
      </div>

      <!-- Error message -->
      {#if auth.authError}
        <div class="mb-4 p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 text-xs text-rose-700 dark:text-rose-300 flex items-start gap-2">
          <AlertCircle class="w-4 h-4 shrink-0 mt-0.5" />
          <span>{auth.authError}</span>
        </div>
      {/if}

      <!-- Official Google Sign-In Button Container -->
      <div class="flex flex-col items-center justify-center p-4 bg-slate-50 dark:bg-slate-800/40 rounded-2xl border border-slate-200 dark:border-slate-700 min-h-[64px]">
        {#if auth.loading}
          <div class="flex items-center gap-2 text-xs text-slate-600 dark:text-slate-300 font-medium py-1.5">
            <RefreshCw class="w-4 h-4 animate-spin text-red-600" />
            <span>Memverifikasi akun Google...</span>
          </div>
        {:else}
          <div id="google-signin-btn-target" class="min-h-[44px] flex items-center justify-center">
            {#if !auth.config.googleClientId}
              <div class="text-xs text-slate-500 text-center py-2">
                Memuat konfigurasi Google Client ID...
              </div>
            {/if}
          </div>
        {/if}
      </div>

      <div class="mt-4 text-center">
        <p class="text-[11px] text-slate-400">
          Autentikasi diamankan secara resmi oleh Google Identity Services.
        </p>
      </div>
    </div>
  </div>
{/if}
