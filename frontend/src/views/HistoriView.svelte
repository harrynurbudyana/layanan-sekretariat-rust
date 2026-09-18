<script lang="ts">
  import { onMount } from 'svelte';
  import { 
    History, 
    FileText, 
    CalendarDays, 
    Copy, 
    Check, 
    Search, 
    Clock, 
    AlertCircle, 
    CheckCircle2, 
    XCircle, 
    User, 
    Mail, 
    Building2, 
    Tag, 
    Plus, 
    ExternalLink, 
    RefreshCw,
    LogIn,
    ShieldCheck
  } from 'lucide-svelte';
  import { auth } from '../lib/auth.svelte';
  import { router } from '../lib/router.svelte';
  import { formatDateIndo, getCategoryBadgeClass, cn } from '../lib/utils';

  let activeTab = $state<'letters' | 'rooms'>('letters');
  let copiedId = $state<string | null>(null);

  // Letters state
  let letters = $state<any[]>([]);
  let lettersLoading = $state(false);
  let letterSearch = $state('');
  let letterYear = $state<number | null>(new Date().getFullYear());

  // Rooms state
  let bookings = $state<any[]>([]);
  let bookingsLoading = $state(false);
  let bookingStatusFilter = $state<string>('ALL');

  async function fetchMyLetters() {
    if (!auth.isLoggedIn) return;
    lettersLoading = true;
    try {
      let url = '/api/letters?my_only=true';
      if (letterYear) url += `&year=${letterYear}`;
      if (letterSearch.trim()) url += `&search=${encodeURIComponent(letterSearch.trim())}`;
      
      const res = await fetch(url, {
        headers: auth.getAuthHeaders()
      });
      if (res.ok) {
        const data = await res.json();
        letters = data.letters || [];
      } else {
        letters = [];
      }
    } catch (err) {
      console.error('Failed to load user letters', err);
      letters = [];
    } finally {
      lettersLoading = false;
    }
  }

  async function fetchMyBookings() {
    if (!auth.isLoggedIn) return;
    bookingsLoading = true;
    try {
      let url = '/api/rooms/bookings?my_only=true';
      if (bookingStatusFilter !== 'ALL') {
        url += `&status=${bookingStatusFilter}`;
      }
      const res = await fetch(url, {
        headers: auth.getAuthHeaders()
      });
      if (res.ok) {
        bookings = await res.json();
      } else {
        bookings = [];
      }
    } catch (err) {
      console.error('Failed to load user bookings', err);
      bookings = [];
    } finally {
      bookingsLoading = false;
    }
  }

  function copyNumber(id: string, text: string) {
    if (typeof navigator !== 'undefined') {
      navigator.clipboard.writeText(text);
      copiedId = id;
      setTimeout(() => {
        if (copiedId === id) copiedId = null;
      }, 2000);
    }
  }

  onMount(() => {
    if (auth.isLoggedIn) {
      fetchMyLetters();
      fetchMyBookings();
    }
  });

  $effect(() => {
    if (auth.isLoggedIn) {
      if (activeTab === 'letters') {
        fetchMyLetters();
      } else {
        fetchMyBookings();
      }
    }
  });
</script>

<div class="space-y-6">
  <!-- Header Banner -->
  <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 sm:p-8 shadow-xs transition-colors">
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div class="flex items-center gap-3 sm:gap-4">
        <div class="w-12 h-12 rounded-2xl bg-gradient-to-tr from-red-600 to-amber-500 flex items-center justify-center text-white shadow-md shadow-red-500/20 shrink-0">
          <History class="w-6 h-6" />
        </div>
        <div>
          <h1 class="text-xl sm:text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
            Histori Pengajuan Saya
          </h1>
          <p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
            Riwayat pembuatan nomor surat dan status persetujuan peminjaman ruangan yang Anda ajukan.
          </p>
        </div>
      </div>

      {#if auth.isLoggedIn && auth.user}
        <div class="flex items-center gap-3 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/80 px-3.5 py-2 rounded-2xl shadow-2xs">
          {#if auth.user.picture}
            <img src={auth.user.picture} alt={auth.user.name} class="w-8 h-8 rounded-full ring-2 ring-red-500/30 shrink-0" />
          {:else}
            <div class="w-8 h-8 rounded-full bg-red-100 dark:bg-red-900/60 text-red-600 dark:text-red-300 flex items-center justify-center font-bold text-xs shrink-0">
              {auth.user.name ? auth.user.name[0].toUpperCase() : 'U'}
            </div>
          {/if}
          <div class="text-left min-w-0">
            <div class="text-xs font-bold text-slate-900 dark:text-white truncate">
              {auth.user.name}
            </div>
            <div class="text-[11px] text-slate-500 dark:text-slate-400 font-mono truncate">
              {auth.user.email}
            </div>
          </div>
          {#if auth.isAdmin}
            <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800 shrink-0 ml-1">
              <ShieldCheck class="w-3 h-3" />
              Staf Sekre
            </span>
          {/if}
        </div>
      {/if}
    </div>

    <!-- Navigation Tabs -->
    {#if auth.isLoggedIn}
      <div class="flex items-center gap-2 mt-6 pt-6 border-t border-slate-100 dark:border-slate-800">
        <button
          type="button"
          onclick={() => activeTab = 'letters'}
          class={cn(
            "flex items-center gap-2 px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all cursor-pointer",
            activeTab === 'letters'
              ? "bg-red-600 text-white shadow-sm shadow-red-600/30"
              : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
          )}
        >
          <FileText class="w-4 h-4" />
          <span>Nomor Surat Saya</span>
          {#if letters.length > 0}
            <span class={cn(
              "px-1.5 py-0.2 rounded-full text-[10px] font-bold",
              activeTab === 'letters' ? "bg-white/25 text-white" : "bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300"
            )}>
              {letters.length}
            </span>
          {/if}
        </button>

        <button
          type="button"
          onclick={() => activeTab = 'rooms'}
          class={cn(
            "flex items-center gap-2 px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all cursor-pointer",
            activeTab === 'rooms'
              ? "bg-red-600 text-white shadow-sm shadow-red-600/30"
              : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
          )}
        >
          <CalendarDays class="w-4 h-4" />
          <span>Peminjaman Ruangan Saya</span>
          {#if bookings.length > 0}
            <span class={cn(
              "px-1.5 py-0.2 rounded-full text-[10px] font-bold",
              activeTab === 'rooms' ? "bg-white/25 text-white" : "bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300"
            )}>
              {bookings.length}
            </span>
          {/if}
        </button>
      </div>
    {/if}
  </div>

  {#if !auth.isLoggedIn}
    <!-- Not Logged In State -->
    <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-8 sm:p-12 text-center max-w-xl mx-auto shadow-sm">
      <div class="w-16 h-16 rounded-3xl bg-red-50 dark:bg-red-950/60 text-red-600 dark:text-red-400 flex items-center justify-center mx-auto mb-4 ring-1 ring-red-500/20">
        <LogIn class="w-8 h-8" />
      </div>
      <h2 class="text-lg sm:text-xl font-bold text-slate-900 dark:text-white mb-2">
        Masuk dengan Akun Google Anda
      </h2>
      <p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400 leading-relaxed mb-6">
        Untuk melihat histori pembuatan nomor surat dan status persetujuan peminjaman ruangan yang pernah Anda ajukan, silakan masuk dengan akun Google Anda (@tass.telkomuniversity.ac.id atau akun Google lainnya).
      </p>
      <button
        type="button"
        onclick={() => auth.openLoginModal()}
        class="inline-flex items-center gap-2.5 px-6 py-3 bg-red-600 hover:bg-red-700 text-white font-bold text-sm rounded-2xl shadow-md shadow-red-600/30 transition-all cursor-pointer active:scale-95"
      >
        <LogIn class="w-4 h-4" />
        <span>Masuk dengan Google</span>
      </button>
    </div>

  {:else if activeTab === 'letters'}
    <!-- TAB 1: NOMOR SURAT SAYA -->
    <div class="space-y-4">
      <div class="flex flex-col sm:flex-row items-center justify-between gap-3 bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-2xs">
        <div class="relative w-full sm:w-80">
          <Search class="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            bind:value={letterSearch}
            onkeydown={(e) => e.key === 'Enter' && fetchMyLetters()}
            placeholder="Cari nomor, perihal, penerima..."
            class="w-full pl-9 pr-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs sm:text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-red-500/40"
          />
        </div>

        <div class="flex items-center gap-2 w-full sm:w-auto justify-end">
          <select
            bind:value={letterYear}
            onchange={fetchMyLetters}
            class="bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 text-xs rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-red-500/40"
          >
            <option value={null}>Semua Tahun</option>
            <option value={2026}>Tahun 2026</option>
            <option value={2025}>Tahun 2025</option>
          </select>

          <button
            type="button"
            onclick={fetchMyLetters}
            title="Muat Ulang"
            class="p-2 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl cursor-pointer"
          >
            <RefreshCw class={cn("w-4 h-4", lettersLoading && "animate-spin")} />
          </button>

          <button
            type="button"
            onclick={() => router.navigate('/generator')}
            class="inline-flex items-center gap-1.5 px-3.5 py-2 bg-red-600 hover:bg-red-700 text-white rounded-xl text-xs font-bold shadow-xs cursor-pointer"
          >
            <Plus class="w-4 h-4" />
            <span>Buat Baru</span>
          </button>
        </div>
      </div>

      {#if lettersLoading}
        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-12 text-center">
          <RefreshCw class="w-8 h-8 text-red-600 animate-spin mx-auto mb-2" />
          <p class="text-xs text-slate-500">Memuat riwayat nomor surat...</p>
        </div>
      {:else if letters.length === 0}
        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-12 text-center">
          <div class="w-12 h-12 rounded-2xl bg-slate-100 dark:bg-slate-800 text-slate-400 flex items-center justify-center mx-auto mb-3">
            <FileText class="w-6 h-6" />
          </div>
          <h3 class="text-sm font-bold text-slate-900 dark:text-white mb-1">
            Belum Ada Nomor Surat Terdaftar
          </h3>
          <p class="text-xs text-slate-500 dark:text-slate-400 mb-4 max-w-md mx-auto">
            Anda belum pernah membuat nomor surat resmi dengan email Google ini ({auth.user?.email}). Nomor surat yang Anda buat akan otomatis tercatat di sini.
          </p>
          <button
            type="button"
            onclick={() => router.navigate('/generator')}
            class="inline-flex items-center gap-1.5 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-xl text-xs font-bold shadow-xs cursor-pointer"
          >
            <Plus class="w-4 h-4" />
            <span>Buat Nomor Surat Sekarang</span>
          </button>
        </div>
      {:else}
        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl overflow-hidden shadow-xs">
          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs">
              <thead class="bg-slate-50 dark:bg-slate-800/80 text-slate-500 dark:text-slate-400 font-semibold border-b border-slate-200 dark:border-slate-800">
                <tr>
                  <th class="py-3 px-4">Nomor Surat Resmi</th>
                  <th class="py-3 px-4">Tanggal</th>
                  <th class="py-3 px-4">Perihal / Subjek</th>
                  <th class="py-3 px-4">Tujuan / Penerima</th>
                  <th class="py-3 px-4">Unit & Kategori</th>
                  <th class="py-3 px-4 text-center">Aksi</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 dark:divide-slate-800 text-slate-700 dark:text-slate-300">
                {#each letters as letter}
                  <tr class="hover:bg-slate-50/70 dark:hover:bg-slate-800/40 transition-colors">
                    <td class="py-3.5 px-4 font-mono font-bold text-slate-900 dark:text-white">
                      <div class="flex items-center gap-2">
                        <span class="text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950/40 px-2 py-0.5 rounded-lg border border-red-200 dark:border-red-900/50">
                          {letter.fullNumber}
                        </span>
                      </div>
                    </td>
                    <td class="py-3.5 px-4 whitespace-nowrap text-slate-500">
                      {formatDateIndo(letter.letterDate)}
                    </td>
                    <td class="py-3.5 px-4 font-medium max-w-xs text-slate-900 dark:text-white">
                      <div class="truncate" title={letter.subject}>
                        {letter.subject}
                      </div>
                    </td>
                    <td class="py-3.5 px-4 text-slate-600 dark:text-slate-400 max-w-[180px]">
                      <div class="truncate" title={letter.recipient || '-'}>
                        {letter.recipient || '-'}
                      </div>
                    </td>
                    <td class="py-3.5 px-4 whitespace-nowrap">
                      <div class="flex flex-col gap-0.5">
                        <span class="font-semibold text-slate-800 dark:text-slate-200 text-[11px]">
                          {letter.unitName || letter.unitId}
                        </span>
                        <span class="text-[10px] text-slate-400">
                          {letter.categoryName || letter.categoryId}
                        </span>
                      </div>
                    </td>
                    <td class="py-3.5 px-4 text-center whitespace-nowrap">
                      <button
                        type="button"
                        onclick={() => copyNumber(letter.id, letter.fullNumber)}
                        class="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-semibold text-[11px] transition-colors cursor-pointer"
                        title="Salin Nomor Surat"
                      >
                        {#if copiedId === letter.id}
                          <Check class="w-3.5 h-3.5 text-emerald-600" />
                          <span class="text-emerald-600">Tersalin</span>
                        {:else}
                          <Copy class="w-3.5 h-3.5 text-slate-500" />
                          <span>Salin</span>
                        {/if}
                      </button>
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        </div>
      {/if}
    </div>

  {:else}
    <!-- TAB 2: PEMINJAMAN RUANGAN SAYA -->
    <div class="space-y-4">
      <div class="flex flex-col sm:flex-row items-center justify-between gap-3 bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-2xs">
        <div class="flex items-center gap-2">
          <span class="text-xs font-semibold text-slate-500">Filter Status:</span>
          <select
            bind:value={bookingStatusFilter}
            onchange={fetchMyBookings}
            class="bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 text-xs rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-red-500/40"
          >
            <option value="ALL">Semua Status</option>
            <option value="PENDING">Menunggu Persetujuan (Pending)</option>
            <option value="CONFIRMED">Disetujui (Confirmed)</option>
            <option value="REJECTED">Ditolak / Perlu Penyesuaian (Rejected)</option>
          </select>
        </div>

        <div class="flex items-center gap-2">
          <button
            type="button"
            onclick={fetchMyBookings}
            title="Muat Ulang"
            class="p-2 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl cursor-pointer"
          >
            <RefreshCw class={cn("w-4 h-4", bookingsLoading && "animate-spin")} />
          </button>

          <button
            type="button"
            onclick={() => router.navigate('/ruangan')}
            class="inline-flex items-center gap-1.5 px-3.5 py-2 bg-red-600 hover:bg-red-700 text-white rounded-xl text-xs font-bold shadow-xs cursor-pointer"
          >
            <Plus class="w-4 h-4" />
            <span>Ajukan Ruangan</span>
          </button>
        </div>
      </div>

      {#if bookingsLoading}
        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-12 text-center">
          <RefreshCw class="w-8 h-8 text-red-600 animate-spin mx-auto mb-2" />
          <p class="text-xs text-slate-500">Memuat riwayat peminjaman ruangan...</p>
        </div>
      {:else if bookings.length === 0}
        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-12 text-center">
          <div class="w-12 h-12 rounded-2xl bg-slate-100 dark:bg-slate-800 text-slate-400 flex items-center justify-center mx-auto mb-3">
            <CalendarDays class="w-6 h-6" />
          </div>
          <h3 class="text-sm font-bold text-slate-900 dark:text-white mb-1">
            Belum Ada Pengajuan Ruangan
          </h3>
          <p class="text-xs text-slate-500 dark:text-slate-400 mb-4 max-w-md mx-auto">
            Anda belum pernah mengajukan peminjaman ruangan dengan akun email ini. Silakan buat pengajuan jadwal ruangan rapat atau multimedia.
          </p>
          <button
            type="button"
            onclick={() => router.navigate('/ruangan')}
            class="inline-flex items-center gap-1.5 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-xl text-xs font-bold shadow-xs cursor-pointer"
          >
            <Plus class="w-4 h-4" />
            <span>Ajukan Peminjaman Ruangan</span>
          </button>
        </div>
      {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          {#each bookings as booking}
            <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-xs space-y-3.5 relative overflow-hidden">
              <!-- Status Ribbon Top -->
              <div class="flex items-center justify-between gap-2">
                <div class="font-mono text-xs font-bold text-slate-600 dark:text-slate-300">
                  {booking.bookingNumber}
                </div>

                {#if booking.status === 'CONFIRMED'}
                  <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/60 dark:text-emerald-300 dark:border-emerald-800">
                    <CheckCircle2 class="w-3.5 h-3.5" />
                    Disetujui
                  </span>
                {:else if booking.status === 'REJECTED'}
                  <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-rose-50 text-rose-700 border border-rose-200 dark:bg-rose-950/60 dark:text-rose-300 dark:border-rose-800">
                    <XCircle class="w-3.5 h-3.5" />
                    Ditolak / Perlu Penyesuaian
                  </span>
                {:else}
                  <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-amber-50 text-amber-700 border border-amber-200 dark:bg-amber-950/60 dark:text-amber-300 dark:border-amber-800">
                    <Clock class="w-3.5 h-3.5 animate-pulse" />
                    Menunggu Persetujuan
                  </span>
                {/if}
              </div>

              <!-- Room & Schedule Details -->
              <div>
                <h3 class="text-base font-bold text-slate-900 dark:text-white">
                  {booking.roomName || 'Ruangan FIT'}
                </h3>
                <div class="flex flex-wrap items-center gap-y-1 gap-x-3 text-xs text-slate-500 dark:text-slate-400 mt-1">
                  <span class="font-semibold text-slate-700 dark:text-slate-300">
                    {formatDateIndo(booking.dateStr)}
                  </span>
                  <span>•</span>
                  <span class="font-mono text-slate-700 dark:text-slate-300">
                    {booking.startTime} - {booking.endTime} WIB
                  </span>
                </div>
              </div>

              <!-- Purpose / Agenda -->
              <div class="bg-slate-50 dark:bg-slate-800/60 p-3 rounded-xl border border-slate-100 dark:border-slate-800 text-xs">
                <div class="font-semibold text-slate-500 dark:text-slate-400 mb-0.5">Keperluan:</div>
                <div class="font-medium text-slate-800 dark:text-slate-200">
                  {booking.purpose}
                </div>
                {#if booking.facilityNotes}
                  <div class="mt-2 pt-2 border-t border-slate-200 dark:border-slate-700 text-[11px] text-slate-500">
                    <strong>Fasilitas:</strong> {booking.facilityNotes}
                  </div>
                {/if}
              </div>

              <!-- Secretariat Staff Notes (if any) -->
              {#if booking.notes}
                <div class={cn(
                  "p-3 rounded-xl border text-xs leading-relaxed",
                  booking.status === 'REJECTED'
                    ? "bg-rose-50/70 dark:bg-rose-950/30 border-rose-200 dark:border-rose-900/60 text-rose-800 dark:text-rose-300"
                    : "bg-blue-50/70 dark:bg-blue-950/30 border-blue-200 dark:border-blue-900/60 text-blue-800 dark:text-blue-300"
                )}>
                  <div class="font-bold flex items-center gap-1.5 mb-0.5">
                    <ShieldCheck class="w-3.5 h-3.5" />
                    <span>Catatan Staf Sekretariat:</span>
                  </div>
                  <div>{booking.notes}</div>
                </div>
              {/if}
            </div>
          {/each}
        </div>
      {/if}
    </div>
  {/if}
</div>
