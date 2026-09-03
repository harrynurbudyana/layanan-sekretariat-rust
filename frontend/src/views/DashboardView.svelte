<script lang="ts">
  import { onMount } from 'svelte';
  import { 
    FilePlus2, 
    BookOpenCheck, 
    CalendarDays, 
    FileText, 
    Sparkles, 
    TrendingUp, 
    Layers, 
    Clock, 
    DoorOpen, 
    CheckCircle2, 
    ArrowRight 
  } from 'lucide-svelte';
  import { router } from '../lib/router.svelte';
  import { formatDateIndo, getCategoryBadgeClass } from '../lib/utils';

  let stats = $state<any>(null);
  let roomStats = $state<any>(null);
  let loading = $state(true);

  async function fetchStats() {
    try {
      const [sRes, rRes] = await Promise.all([
        fetch('/api/stats').then(r => r.json()),
        fetch('/api/rooms/stats').then(r => r.json())
      ]);
      stats = sRes;
      roomStats = rRes;
    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    fetchStats();
  });
</script>

<div class="space-y-8">
  <!-- Welcome Banner (Stable Layout with reserved height) -->
  <div class="bg-gradient-to-r from-red-700 via-red-600 to-amber-600 rounded-3xl p-6 sm:p-8 text-white shadow-xl shadow-red-900/10 flex flex-col md:flex-row md:items-center justify-between gap-6 min-h-[170px]">
    <div class="space-y-2 max-w-2xl">
      <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/15 text-white text-xs font-semibold backdrop-blur-xs h-6">
        <Sparkles size={14} class="w-3.5 h-3.5 text-amber-300 shrink-0" />
        <span>Sistem Layanan Mandiri Sekretariat Fakultas</span>
      </div>
      <h1 class="text-2xl sm:text-3xl font-black tracking-tight leading-tight">
        E-Office Fakultas Ilmu Terapan
      </h1>
      <p class="text-sm text-red-50 leading-relaxed">
        Otomasi penomoran surat resmi, buku agenda digital, dan pencatatan riwayat administrasi fakultas secara instan tanpa antre manual.
      </p>
    </div>

    <div class="flex flex-wrap items-center gap-3 shrink-0">
      <button
        type="button"
        onclick={() => router.navigate('/generator')}
        class="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-white text-red-700 hover:bg-red-50 text-xs sm:text-sm font-bold shadow-md transition-all active:scale-95 cursor-pointer h-11"
      >
        <FilePlus2 size={16} class="w-4 h-4 text-red-600 shrink-0" />
        <span>Buat Nomor Surat</span>
      </button>
      <button
        type="button"
        onclick={() => router.navigate('/agenda')}
        class="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-red-800/60 hover:bg-red-800/80 text-white border border-white/20 text-xs sm:text-sm font-semibold transition-all cursor-pointer h-11"
      >
        <BookOpenCheck size={16} class="w-4 h-4 shrink-0" />
        <span>Buku Agenda</span>
      </button>
      <button
        type="button"
        onclick={() => router.navigate('/ruangan')}
        class="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-amber-500 hover:bg-amber-600 text-white text-xs sm:text-sm font-bold shadow-md transition-all active:scale-95 cursor-pointer h-11"
      >
        <CalendarDays size={16} class="w-4 h-4 shrink-0" />
        <span>Pinjam Ruangan</span>
      </button>
    </div>
  </div>

  <!-- Metric Cards (Consistent min-h-[104px] prevents vertical shift) -->
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
    <!-- Card 1 -->
    <div class="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between min-h-[108px]">
      <div>
        <span class="text-[11px] font-bold uppercase tracking-wider text-slate-400">
          Total Surat Tahun {stats?.current_year || new Date().getFullYear()}
        </span>
        <div class="text-2xl font-black text-slate-900 dark:text-white mt-1 h-8 flex items-baseline gap-1">
          {#if loading && !stats}
            <span class="inline-block w-16 h-7 bg-slate-200 dark:bg-slate-800 rounded-md animate-pulse"></span>
          {:else}
            <span>{stats?.total_this_year ?? 0}</span>
            <span class="text-xs font-normal text-slate-500">dokumen</span>
          {/if}
        </div>
        <span class="text-[11px] text-emerald-600 font-semibold flex items-center gap-1 mt-1">
          <TrendingUp size={12} class="w-3 h-3 shrink-0" />
          <span>Register Aktif FIT</span>
        </span>
      </div>
      <div class="h-12 w-12 rounded-xl bg-red-50 dark:bg-red-950/50 text-red-600 flex items-center justify-center shrink-0">
        <FileText size={24} class="w-6 h-6 shrink-0" />
      </div>
    </div>

    <!-- Card 2 -->
    <div class="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between min-h-[108px]">
      <div>
        <span class="text-[11px] font-bold uppercase tracking-wider text-slate-400">
          Surat Bulan Ini
        </span>
        <div class="text-2xl font-black text-slate-900 dark:text-white mt-1 h-8 flex items-baseline gap-1">
          {#if loading && !stats}
            <span class="inline-block w-12 h-7 bg-slate-200 dark:bg-slate-800 rounded-md animate-pulse"></span>
          {:else}
            <span>{stats?.total_this_month ?? 0}</span>
            <span class="text-xs font-normal text-slate-500">dokumen</span>
          {/if}
        </div>
        <span class="text-[11px] text-slate-500 font-medium flex items-center gap-1 mt-1">
          <Clock size={12} class="w-3 h-3 shrink-0" />
          <span>Bulan Berjalan</span>
        </span>
      </div>
      <div class="h-12 w-12 rounded-xl bg-amber-50 dark:bg-amber-950/50 text-amber-600 flex items-center justify-center shrink-0">
        <Layers size={24} class="w-6 h-6 shrink-0" />
      </div>
    </div>

    <!-- Card 3 -->
    <div class="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between min-h-[108px]">
      <div>
        <span class="text-[11px] font-bold uppercase tracking-wider text-slate-400">
          Ruangan Aktif
        </span>
        <div class="text-2xl font-black text-slate-900 dark:text-white mt-1 h-8 flex items-baseline gap-1">
          {#if loading && !roomStats}
            <span class="inline-block w-10 h-7 bg-slate-200 dark:bg-slate-800 rounded-md animate-pulse"></span>
          {:else}
            <span>{roomStats?.totalRooms ?? 6}</span>
            <span class="text-xs font-normal text-slate-500">fasilitas</span>
          {/if}
        </div>
        <span class="text-[11px] text-blue-600 font-semibold flex items-center gap-1 mt-1">
          <DoorOpen size={12} class="w-3 h-3 shrink-0" />
          <span>Gedung Selaru FIT</span>
        </span>
      </div>
      <div class="h-12 w-12 rounded-xl bg-blue-50 dark:bg-blue-950/50 text-blue-600 flex items-center justify-center shrink-0">
        <DoorOpen size={24} class="w-6 h-6 shrink-0" />
      </div>
    </div>

    <!-- Card 4 -->
    <div class="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between min-h-[108px]">
      <div>
        <span class="text-[11px] font-bold uppercase tracking-wider text-slate-400">
          Peminjaman Hari Ini
        </span>
        <div class="text-2xl font-black text-slate-900 dark:text-white mt-1 h-8 flex items-baseline gap-1">
          {#if loading && !roomStats}
            <span class="inline-block w-10 h-7 bg-slate-200 dark:bg-slate-800 rounded-md animate-pulse"></span>
          {:else}
            <span>{roomStats?.bookingsToday ?? 0}</span>
            <span class="text-xs font-normal text-slate-500">jadwal</span>
          {/if}
        </div>
        <span class="text-[11px] text-emerald-600 font-semibold flex items-center gap-1 mt-1">
          <CheckCircle2 size={12} class="w-3 h-3 shrink-0" />
          <span>Status Terkonfirmasi</span>
        </span>
      </div>
      <div class="h-12 w-12 rounded-xl bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 flex items-center justify-center shrink-0">
        <CalendarDays size={24} class="w-6 h-6 shrink-0" />
      </div>
    </div>
  </div>

  <!-- Recent Letters & Breakdowns (Stable Height Containers) -->
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
    <!-- Recent Letters List (2 cols) -->
    <div class="lg:col-span-2 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm p-6 min-h-[460px]">
      <div class="flex items-center justify-between mb-5">
        <div>
          <h2 class="text-base font-bold text-slate-900 dark:text-white">Surat Baru Terbit</h2>
          <p class="text-xs text-slate-500">5 nomor surat terbaru yang diterbitkan</p>
        </div>
        <button
          type="button"
          onclick={() => router.navigate('/agenda')}
          class="text-xs font-semibold text-red-600 hover:text-red-700 dark:text-red-400 flex items-center gap-1 cursor-pointer"
        >
          <span>Lihat Semua</span>
          <ArrowRight size={14} class="w-3.5 h-3.5" />
        </button>
      </div>

      {#if loading && !stats}
        <!-- Skeleton loading placeholder to reserve height and prevent CLS -->
        <div class="space-y-3">
          {#each [1, 2, 3, 4, 5] as _}
            <div class="p-3.5 rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 animate-pulse h-[68px]">
              <div class="h-3.5 bg-slate-200 dark:bg-slate-700 rounded w-1/3 mb-2"></div>
              <div class="h-3 bg-slate-100 dark:bg-slate-800 rounded w-2/3"></div>
            </div>
          {/each}
        </div>
      {:else if stats?.recent_letters && stats.recent_letters.length > 0}
        <div class="space-y-3">
          {#each stats.recent_letters as letter}
            <div class="p-3.5 rounded-xl border border-slate-100 dark:border-slate-800 hover:border-slate-200 dark:hover:border-slate-700 bg-slate-50/50 dark:bg-slate-800/30 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <div class="flex items-center gap-2 mb-1">
                  <span class="font-mono text-xs font-bold text-red-600 dark:text-red-400">{letter.full_number}</span>
                  <span class="text-[10px] font-semibold px-2 py-0.5 rounded-full {getCategoryBadgeClass(letter.classification_code)}">
                    {letter.category_name || 'Umum'}
                  </span>
                </div>
                <h3 class="text-xs font-medium text-slate-800 dark:text-slate-200 line-clamp-1">{letter.subject}</h3>
                <p class="text-[11px] text-slate-400 mt-0.5">Pemohon: {letter.applicant_name} ({letter.unit_name || '-'})</p>
              </div>
              <div class="text-[11px] text-slate-400 shrink-0 sm:text-right">
                {formatDateIndo(letter.letter_date)}
              </div>
            </div>
          {/each}
        </div>
      {:else}
        <div class="text-center py-16 text-slate-400 text-xs">Belum ada surat yang diterbitkan.</div>
      {/if}
    </div>

    <!-- Unit Distribution (1 col) -->
    <div class="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm p-6 flex flex-col justify-between min-h-[460px]">
      <div>
        <h2 class="text-base font-bold text-slate-900 dark:text-white mb-1">Top Pemohon Unit</h2>
        <p class="text-xs text-slate-500 mb-4">Aktivitas surat keluar tertinggi tahun ini</p>

        {#if loading && !stats}
          <div class="space-y-3">
            {#each [1, 2, 3, 4, 5] as _}
              <div class="h-8 rounded-lg bg-slate-100 dark:bg-slate-800/60 animate-pulse"></div>
            {/each}
          </div>
        {:else if stats?.unit_stats && stats.unit_stats.length > 0}
          <div class="space-y-3">
            {#each stats.unit_stats as item}
              <div class="flex items-center justify-between text-xs">
                <span class="text-slate-700 dark:text-slate-300 font-medium truncate max-w-[180px]">{item.unitName}</span>
                <span class="font-mono font-bold px-2 py-0.5 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                  {item.count} surat
                </span>
              </div>
            {/each}
          </div>
        {:else}
          <p class="text-xs text-slate-400 py-6 text-center">Belum ada data unit.</p>
        {/if}
      </div>

      <div class="mt-6 pt-4 border-t border-slate-100 dark:border-slate-800">
        <button
          type="button"
          onclick={() => router.navigate('/master')}
          class="w-full text-center text-xs font-semibold text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 cursor-pointer"
        >
          Kelola Master Unit & Prodi &rarr;
        </button>
      </div>
    </div>
  </div>
</div>
