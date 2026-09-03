<script lang="ts">
  import { onMount } from 'svelte';
  import { 
    HelpCircle, 
    BookOpen, 
    CheckCircle2, 
    Building2, 
    Layers, 
    AlertCircle, 
    Sparkles 
  } from 'lucide-svelte';

  let units = $state<any[]>([]);
  let categories = $state<any[]>([]);

  onMount(async () => {
    try {
      const [uRes, cRes] = await Promise.all([
        fetch('/api/units').then(r => r.json()),
        fetch('/api/categories').then(r => r.json())
      ]);
      units = uRes;
      categories = cRes;
    } catch (e) {
      console.error(e);
    }
  });
</script>

<div class="space-y-8 max-w-4xl">
  <!-- Header -->
  <div class="pb-6 border-b border-slate-200 dark:border-slate-800">
    <div class="flex items-center gap-2 text-xs font-bold text-red-600 uppercase tracking-wider mb-1">
      <HelpCircle class="h-4 w-4" />
      <span>Buku Pedoman Tata Naskah Dinas</span>
    </div>
    <h1 class="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white tracking-tight">
      Panduan Format Penomoran Surat FIT
    </h1>
    <p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
      Pedoman resmi struktur format nomor surat dan kode klasifikasi perihal di lingkungan Fakultas Ilmu Terapan (FIT).
    </p>
  </div>

  <!-- Anatomi Penomoran Card -->
  <div class="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 sm:p-8 shadow-sm space-y-6">
    <h2 class="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
      <BookOpen class="h-5 w-5 text-red-600" />
      <span>1. Anatomi & Struktur Nomor Surat Resmi</span>
    </h2>

    <!-- Format Display -->
    <div class="bg-slate-900 text-white p-6 rounded-2xl text-center space-y-2 border border-slate-800">
      <div class="text-xs text-slate-400 uppercase font-semibold">Format Baku Surat Fakultas Ilmu Terapan:</div>
      <div class="text-2xl sm:text-3xl font-mono font-black text-amber-300 tracking-tight">
        1532 / AKD01 / IT-DEK / 2026
      </div>
      <p class="text-xs text-slate-400 font-mono">
        [No_Urut] / [Kode_Klasifikasi_Perihal] / [Kode_Fakultas_dan_Penandatangan] / [Tahun]
      </p>
    </div>

    <!-- Explanation -->
    <div class="space-y-3 text-xs">
      <h3 class="font-bold text-slate-900 dark:text-white uppercase tracking-wider text-[11px]">
        Penjelasan Setiap Segmen:
      </h3>
      <div class="grid grid-cols-1 gap-2.5">
        <div class="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/80 dark:border-slate-700/80 flex items-start gap-3">
          <span class="font-mono font-bold text-amber-600 bg-amber-50 dark:bg-amber-950 px-2 py-0.5 rounded text-xs shrink-0">
            1532
          </span>
          <div>
            <strong class="text-slate-900 dark:text-slate-100">1. Nomor Urut Register Agenda</strong>
            <p class="text-slate-500 text-[11px] mt-0.5">
              Nomor urut yang di-generate otomatis oleh sistem (atau diisi secara manual oleh staf sekretariat). Urutan bersifat tunggal dalam fakultas dan dihitung akumulatif per tahun kalender.
            </p>
          </div>
        </div>

        <div class="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/80 dark:border-slate-700/80 flex items-start gap-3">
          <span class="font-mono font-bold text-blue-600 bg-blue-50 dark:bg-blue-950 px-2 py-0.5 rounded text-xs shrink-0">
            AKD01 / AKD13
          </span>
          <div>
            <strong class="text-slate-900 dark:text-slate-100">2. Kode Klasifikasi & Rincian Perihal</strong>
            <p class="text-slate-500 text-[11px] mt-0.5">
              Menandakan bidang dan sub-perihal surat. Misalnya AKD01 untuk Akademik Umum, AKD13 untuk Magang/MBKM, KMH01 untuk Kemahasiswaan, dan SDM01 untuk Kepegawaian.
            </p>
          </div>
        </div>

        <div class="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/80 dark:border-slate-700/80 flex items-start gap-3">
          <span class="font-mono font-bold text-emerald-600 bg-emerald-50 dark:bg-emerald-950 px-2 py-0.5 rounded text-xs shrink-0">
            IT-DEK
          </span>
          <div>
            <strong class="text-slate-900 dark:text-slate-100">3. Fakultas & Pejabat Penandatangan</strong>
            <p class="text-slate-500 text-[11px] mt-0.5">
              <strong>IT</strong> singkatan dari Fakultas Ilmu Terapan, diikuti kode penandatangan: IT-DEK (Dekan), IT-WD1/IT-WD2 (Wakil Dekan), IT-SKR (Sekretariat), atau IT-D3-SI / IT-D3-RPL (Ketua Prodi).
            </p>
          </div>
        </div>

        <div class="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/80 dark:border-slate-700/80 flex items-start gap-3">
          <span class="font-mono font-bold text-purple-600 bg-purple-50 dark:bg-purple-950 px-2 py-0.5 rounded text-xs shrink-0">
            2026
          </span>
          <div>
            <strong class="text-slate-900 dark:text-slate-100">4. Tahun Penerbitan Surat</strong>
            <p class="text-slate-500 text-[11px] mt-0.5">
              Tahun kalender masehi saat naskah dinas diterbitkan secara resmi.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Reference Tables -->
  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
    <!-- Categories Reference -->
    <div class="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm space-y-3">
      <h3 class="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
        <Layers class="w-4 h-4 text-amber-500" />
        <span>Daftar Klasifikasi Perihal</span>
      </h3>
      <div class="space-y-2 max-h-72 overflow-y-auto pr-1 text-xs">
        {#each categories as c}
          <div class="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800 flex items-center justify-between">
            <div>
              <div class="font-semibold text-slate-800 dark:text-slate-200">{c.name}</div>
              <span class="text-[10px] text-slate-400">{c.group}</span>
            </div>
            <span class="font-mono font-bold px-2 py-0.5 rounded bg-amber-100 dark:bg-amber-950/60 text-amber-700 dark:text-amber-400 text-[11px]">
              {c.code}
            </span>
          </div>
        {/each}
      </div>
    </div>

    <!-- Units Reference -->
    <div class="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm space-y-3">
      <h3 class="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
        <Building2 class="w-4 h-4 text-red-500" />
        <span>Kode Penandatangan Unit</span>
      </h3>
      <div class="space-y-2 max-h-72 overflow-y-auto pr-1 text-xs">
        {#each units as u}
          <div class="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800 flex items-center justify-between">
            <div>
              <div class="font-semibold text-slate-800 dark:text-slate-200">{u.name}</div>
              <span class="text-[10px] text-slate-400">{u.category}</span>
            </div>
            <span class="font-mono font-bold px-2 py-0.5 rounded bg-red-100 dark:bg-red-950/60 text-red-700 dark:text-red-400 text-[11px]">
              {u.signee_code}
            </span>
          </div>
        {/each}
      </div>
    </div>
  </div>
</div>
