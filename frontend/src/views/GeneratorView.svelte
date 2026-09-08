<script lang="ts">
  import { onMount } from 'svelte';
  import { 
    FileText, 
    Sparkles, 
    Layers, 
    Lock, 
    Copy, 
    Check, 
    AlertCircle, 
    RefreshCw, 
    PenTool, 
    ArrowRight, 
    Info, 
    FileSpreadsheet, 
    Plus, 
    Trash2,
    CheckCircle2
  } from 'lucide-svelte';
  import { admin } from '../lib/admin.svelte';
  import { router } from '../lib/router.svelte';
  import { formatDateIndo } from '../lib/utils';

  let units = $state<any[]>([]);
  let categories = $state<any[]>([]);
  let loadingMeta = $state(true);

  // 3-Way Mode Switcher: "single" | "batch" | "manual"
  let mode = $state<'single' | 'batch' | 'manual'>('single');

  // Shared Form State
  let unitId = $state('');
  let categoryId = $state('');
  let customSignee = $state('IT-DEK');
  let customClassification = $state('SKR05');

  let subject = $state('');
  let recipient = $state('');
  let applicantName = $state('');
  let applicantContact = $state('');
  let letterDate = $state(new Date().toISOString().slice(0, 10));
  let notes = $state('');

  // Manual Mode specific
  let manualSequence = $state<number | null>(null);
  let manualFullNumber = $state('');

  // Batch Mode specific
  let batchCount = $state<number>(3);
  let batchDetailed = $state(false);
  interface BatchRow {
    applicantName: string;
    recipient: string;
    subject: string;
  }
  let batchRows = $state<BatchRow[]>([
    { applicantName: '', recipient: '', subject: '' },
    { applicantName: '', recipient: '', subject: '' },
    { applicantName: '', recipient: '', subject: '' },
  ]);

  // Submission State
  let isPending = $state(false);
  let errorMsg = $state<string | null>(null);
  let successResult = $state<any | null>(null);
  let batchSuccessResult = $state<any | null>(null);
  let copied = $state(false);
  let copiedBatch = $state(false);

  // Signee Options grouped as in Telkom University FIT
  const categoryGroups = [
    { key: "SKR", label: "SKR — Sekretariat & Undangan Resmi" },
    { key: "AKD", label: "AKD — Akademik, Perkuliahan & Magang" },
    { key: "KMH", label: "KMH — Kemahasiswaan, Lomba & Beasiswa" },
    { key: "SDM", label: "SDM — Kepegawaian & Penugasan Dosen" },
    { key: "SAM", label: "SAM — Kerjasama, MoU, MoA & Kemitraan" },
    { key: "LIT", label: "LIT — Penelitian, Jurnal & Konferensi" },
    { key: "ABD", label: "ABD — Pengabdian kepada Masyarakat (Abdimas)" },
    { key: "AST", label: "AST — Sarana, Ruangan & Laboratorium" },
    { key: "KUG", label: "KUG — Keuangan & Anggaran" },
  ];

  const signeeGroups = [
    {
      group: "Pimpinan Fakultas",
      options: [
        { code: "IT-DEK", label: "IT-DEK — Dekan Fakultas Ilmu Terapan" },
        { code: "IT-WD1", label: "IT-WD1 — Wakil Dekan 1 (Akademik & Riset)" },
        { code: "IT-WD2", label: "IT-WD2 — Wakil Dekan 2 (Keuangan, SDM & Kemahasiswaan)" },
      ],
    },
    {
      group: "Kepala Urusan / Bagian FIT",
      options: [
        { code: "IT-SDM", label: "IT-SDM — Kaur Sumber Daya, Keuangan & Logistik" },
        { code: "IT-SKR", label: "IT-SKR — Kaur Sekretariat" },
        { code: "IT-LAB", label: "IT-LAB — Kaur Laboratorium & Bengkel" },
        { code: "IT-LKM", label: "IT-LKM — Kaur Layanan Kerjasama dan Magang" },
        { code: "IT-LA", label: "IT-LA — Kaur Layanan Akademik" },
        { code: "IT-KMH", label: "IT-KMH — Kaur Kemahasiswaan" },
      ],
    },
    {
      group: "Ketua Program Studi (Kaprodi)",
      options: [
        { code: "IT-D3-SI", label: "IT-D3-SI — Prodi D3 Sistem Informasi" },
        { code: "IT-D3-TKO", label: "IT-D3-TKO — Prodi D3 Teknologi Komputer" },
        { code: "IT-D3-SIA", label: "IT-D3-SIA — Prodi D3 Sistem Informasi Akuntansi" },
        { code: "IT-D3-RPL", label: "IT-D3-RPL — Prodi D3 Rekayasa Perangkat Lunak Aplikasi" },
        { code: "IT-D3-MP", label: "IT-D3-MP — Prodi D3 Manajemen Pemasaran" },
        { code: "IT-D3-PHT", label: "IT-D3-PHT — Prodi D3 Perhotelan" },
        { code: "IT-D3-TT", label: "IT-D3-TT — Prodi D3 Teknologi Telekomunikasi" },
        { code: "IT-D4-TRM", label: "IT-D4-TRM — Prodi S1 Terapan Teknologi Rekayasa Multimedia" },
        { code: "IT-D4-SIKC", label: "IT-D4-SIKC — Prodi S1 Terapan Sistem Informasi Kota Cerdas" },
        { code: "IT-S2-RTI", label: "IT-S2-RTI — Prodi S2 Terapan Rekayasa Teknologi Informasi" },
      ],
    },
    {
      group: "Kelompok Keahlian & Riset (KK / Research Alliance)",
      options: [
        { code: "IT-KK-AITM", label: "IT-KK-AITM — KK Applied Information Technology and Multimedia" },
        { code: "IT-KK-DBS", label: "IT-KK-DBS — KK Applied Digital Business Entrepreneur and Tourism" },
        { code: "IT-RA-ATAP", label: "IT-RA-ATAP — Research Alliance ATAP" },
      ],
    },
  ];

  async function loadMetadata() {
    loadingMeta = true;
    try {
      const [uRes, cRes] = await Promise.all([
        fetch('/api/units').then(r => r.json()),
        fetch('/api/categories').then(r => r.json())
      ]);
      units = uRes;
      categories = cRes;

      const defUnit = units.find(u => u.code === 'DEK' || u.signee_code === 'IT-DEK') || units[0];
      const defCat = categories.find(c => c.code === 'SKR05') || categories[0];

      if (defUnit) {
        unitId = defUnit.id;
        customSignee = defUnit.signee_code || 'IT-DEK';
      }
      if (defCat) {
        categoryId = defCat.id;
        customClassification = defCat.code || 'SKR05';
      }
    } catch (e) {
      console.error(e);
    } finally {
      loadingMeta = false;
    }
  }

  onMount(() => {
    loadMetadata();
  });

  function onUnitChange() {
    const u = units.find(u => u.id === unitId);
    if (u && u.signee_code) {
      customSignee = u.signee_code;
    }
  }

  function onCategoryChange() {
    const c = categories.find(c => c.id === categoryId);
    if (c && c.code) {
      customClassification = c.code;
    }
  }

  function handleBatchCountChange(newVal: number) {
    const val = Math.max(1, Math.min(newVal, 100));
    batchCount = val;
    if (batchDetailed) {
      while (batchRows.length < val) {
        batchRows.push({ applicantName: '', recipient: '', subject: '' });
      }
      if (batchRows.length > val) {
        batchRows = batchRows.slice(0, val);
      }
    }
  }

  function addBatchRow() {
    if (batchCount >= 100) return;
    handleBatchCountChange(batchCount + 1);
  }

  function removeBatchRow(index: number) {
    if (batchCount <= 1) return;
    batchRows = batchRows.filter((_, idx) => idx !== index);
    batchCount = batchRows.length;
  }

  // Grouped Categories and Units for clean optgroup dropdowns
  let groupedCategories = $derived.by(() => {
    const list = categoryGroups.map(g => ({
      label: g.label,
      items: categories.filter(c => c.group === g.key)
    })).filter(g => g.items.length > 0);

    const others = categories.filter(c => !categoryGroups.some(g => g.key === c.group));
    if (others.length > 0) {
      list.push({
        label: "Lainnya / Klasifikasi Tambahan",
        items: others
      });
    }
    return list;
  });

  let groupedUnits = $derived.by(() => {
    return [
      {
        label: "Pimpinan Fakultas & Dekanat",
        items: units.filter(u => u.category === 'DEKANAT')
      },
      {
        label: "Program Studi FIT",
        items: units.filter(u => u.category === 'PRODI')
      },
      {
        label: "Kepala Urusan / Bagian Layanan",
        items: units.filter(u => u.category === 'BAGIAN')
      },
      {
        label: "Kelompok Keahlian & Riset (KK / RA)",
        items: units.filter(u => u.category === 'KELOMPOK_KEAHLIAN' || u.category === 'RISET')
      }
    ].filter(g => g.items.length > 0);
  });

  // Selected elements derived
  let previewYear = $derived(letterDate ? new Date(letterDate).getFullYear() : new Date().getFullYear());

  let previewNumber = $derived.by(() => {
    const classCode = customClassification || 'SKR05';
    const signee = customSignee || 'IT-DEK';
    const year = previewYear;

    if (mode === 'batch') {
      return `[${batchCount}_Nomor_Berurutan] / ${classCode} / ${signee} / ${year}`;
    }
    if (mode === 'manual') {
      if (manualFullNumber.trim()) return manualFullNumber.trim();
      const seq = manualSequence ? manualSequence.toString() : '...';
      return `${seq} / ${classCode} / ${signee} / ${year}`;
    }
    return `[No_Urut] / ${classCode} / ${signee} / ${year}`;
  });

  $effect(() => {
    if (!admin.isAdmin && mode === 'manual') {
      mode = 'single';
    }
  });

  async function handleSubmit(e: Event) {
    e.preventDefault();
    errorMsg = null;

    if (!unitId || !categoryId || !subject.trim() || !applicantName.trim()) {
      errorMsg = 'Harap lengkapi semua field wajib bertanda bintang (*).';
      return;
    }

    isPending = true;

    try {
      if (mode === 'batch') {
        const items = batchDetailed
          ? batchRows.map(r => ({
              applicant_name: r.applicantName.trim() || applicantName.trim(),
              recipient: r.recipient.trim() || recipient.trim() || null,
              subject: r.subject.trim() || subject.trim(),
            }))
          : undefined;

        const res = await fetch('/api/letters/generate-batch', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            count: batchCount,
            unit_id: unitId,
            category_id: categoryId,
            classification_code: customClassification,
            signee_code: customSignee,
            subject: subject.trim(),
            recipient: recipient.trim() || null,
            applicant_name: applicantName.trim(),
            applicant_contact: applicantContact.trim() || null,
            letter_date: letterDate,
            notes: notes.trim() || null,
            items
          })
        });
        const data = await res.json();
        if (data.success) {
          batchSuccessResult = data;
          successResult = null;
        } else {
          errorMsg = data.error || 'Gagal membuat batch nomor surat.';
        }
      } else {
        const res = await fetch('/api/letters/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            is_manual: mode === 'manual',
            manual_sequence_number: mode === 'manual' ? manualSequence : null,
            manual_full_number: mode === 'manual' && manualFullNumber.trim() ? manualFullNumber.trim() : null,
            unit_id: unitId,
            category_id: categoryId,
            classification_code: customClassification,
            signee_code: customSignee,
            subject: subject.trim(),
            recipient: recipient.trim() || null,
            applicant_name: applicantName.trim(),
            applicant_contact: applicantContact.trim() || null,
            letter_date: letterDate,
            notes: notes.trim() || null
          })
        });
        const data = await res.json();
        if (data.success) {
          successResult = data.letter;
          batchSuccessResult = null;
        } else {
          errorMsg = data.error || 'Gagal membuat nomor surat.';
        }
      }
    } catch (e) {
      errorMsg = 'Gagal menghubungi server Rust.';
    } finally {
      isPending = false;
    }
  }

  function handleCopy(text: string) {
    navigator.clipboard.writeText(text);
    copied = true;
    setTimeout(() => copied = false, 2500);
  }

  function handleCopyAllBatch() {
    if (!batchSuccessResult || !batchSuccessResult.letters) return;
    const all = batchSuccessResult.letters.map((l: any) => l.fullNumber).join('\n');
    navigator.clipboard.writeText(all);
    copiedBatch = true;
    setTimeout(() => copiedBatch = false, 2500);
  }

  function exportBatchCSV() {
    if (!batchSuccessResult || !batchSuccessResult.letters) return;
    const headers = ["No Urut", "Nomor Surat", "Perihal", "Pemohon", "Tujuan", "Tanggal"];
    const rows = batchSuccessResult.letters.map((l: any) => [
      l.sequenceNumber,
      `"${l.fullNumber}"`,
      `"${(l.subject || '').replace(/"/g, '""')}"`,
      `"${l.applicantName}"`,
      `"${l.recipient || ''}"`,
      l.letterDate
    ]);
    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map((e: (string | number)[]) => e.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `batch_${batchSuccessResult.count}_nomor_surat.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  function resetForNew() {
    successResult = null;
    batchSuccessResult = null;
    subject = '';
    recipient = '';
    applicantContact = '';
    notes = '';
    manualFullNumber = '';
    manualSequence = null;
    errorMsg = null;
  }
</script>

<div class="space-y-8">
  <!-- Page Header -->
  <div>
    <h1 class="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white tracking-tight">
      Pembuatan Nomor Surat Otomatis
    </h1>
    <p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
      Layanan penomoran surat resmi Fakultas Ilmu Terapan untuk dosen, staf prodi, dan unit kerja.
    </p>
  </div>

  <!-- 3-Way Mode Switcher Tabs -->
  <div class="bg-white dark:bg-slate-900 p-1.5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-wrap sm:flex-nowrap items-center gap-1.5 max-w-lg">
    <!-- Tab 1: Satu Surat -->
    <button
      type="button"
      onclick={() => { mode = 'single'; errorMsg = null; }}
      class="flex-1 flex items-center justify-center gap-2 py-2 px-3.5 rounded-xl text-xs font-bold transition-all cursor-pointer {mode === 'single' ? 'bg-red-600 text-white shadow-md shadow-red-600/25' : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'}"
    >
      <Sparkles class="h-3.5 w-3.5" />
      <span>Satu Surat</span>
    </button>

    <!-- Tab 2: Banyak Surat (Batch) -->
    <button
      type="button"
      onclick={() => { mode = 'batch'; errorMsg = null; }}
      class="flex-1 flex items-center justify-center gap-2 py-2 px-3.5 rounded-xl text-xs font-bold transition-all cursor-pointer {mode === 'batch' ? 'bg-red-600 text-white shadow-md shadow-red-600/25' : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'}"
    >
      <Layers class="h-3.5 w-3.5" />
      <span>Banyak Surat (Batch)</span>
    </button>

    <!-- Tab 3: Mode Manual (Admin) -->
    <button
      type="button"
      onclick={() => {
        if (!admin.isAdmin) {
          admin.openLoginModal();
        } else {
          mode = 'manual';
          errorMsg = null;
        }
      }}
      class="flex-1 flex items-center justify-center gap-2 py-2 px-3.5 rounded-xl text-xs font-bold transition-all cursor-pointer {mode === 'manual' ? 'bg-red-600 text-white shadow-md shadow-red-600/25' : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'}"
    >
      <Lock class="h-3.5 w-3.5 {mode === 'manual' ? 'text-white' : 'text-amber-500'}" />
      <span>Mode Manual (Admin)</span>
    </button>
  </div>

  <!-- SINGLE SUCCESS BANNER -->
  {#if successResult}
    <div class="bg-emerald-50 dark:bg-emerald-950/40 border-2 border-emerald-500/50 rounded-2xl p-6 sm:p-8 shadow-xl shadow-emerald-500/5 animate-in fade-in duration-200 space-y-5">
      <div class="flex items-center gap-3">
        <div class="h-12 w-12 rounded-xl bg-emerald-600 text-white flex items-center justify-center shrink-0 shadow-md shadow-emerald-600/20">
          <CheckCircle2 class="h-7 w-7" />
        </div>
        <div>
          <span class="text-xs uppercase tracking-wider font-bold text-emerald-700 dark:text-emerald-300">
            Nomor Surat Berhasil Diterbitkan
          </span>
          <h3 class="text-xl sm:text-2xl font-black text-slate-900 dark:text-white tracking-tight">
            Tersimpan di Buku Agenda Digital FIT
          </h3>
        </div>
      </div>

      <div class="bg-white dark:bg-slate-900 border border-emerald-200 dark:border-emerald-800 rounded-xl p-5 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-sm">
        <div class="text-center sm:text-left">
          <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
            Nomor Surat Resmi
          </div>
          <div class="text-xl sm:text-2xl md:text-3xl font-mono font-bold text-slate-900 dark:text-slate-100 selection:bg-emerald-200">
            {successResult.fullNumber}
          </div>
        </div>

        <button
          type="button"
          onclick={() => handleCopy(successResult.fullNumber)}
          class="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs sm:text-sm font-bold shadow-md shadow-emerald-600/20 transition-all active:scale-95 cursor-pointer"
        >
          {#if copied}
            <Check class="h-4 w-4" />
            <span>Tersalin ke Clipboard!</span>
          {:else}
            <Copy class="h-4 w-4" />
            <span>Salin Nomor Surat</span>
          {/if}
        </button>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs bg-emerald-100/50 dark:bg-emerald-950/60 p-4 rounded-xl border border-emerald-200/50 dark:border-emerald-800/50">
        <div>
          <span class="text-slate-500 dark:text-slate-400">Unit Pemohon:</span>
          <p class="font-semibold text-slate-800 dark:text-slate-200 mt-0.5">{successResult.unitName}</p>
        </div>
        <div>
          <span class="text-slate-500 dark:text-slate-400">Klasifikasi Perihal:</span>
          <p class="font-semibold text-slate-800 dark:text-slate-200 mt-0.5">{successResult.categoryName}</p>
        </div>
        <div>
          <span class="text-slate-500 dark:text-slate-400">Penandatangan:</span>
          <p class="font-semibold text-slate-800 dark:text-slate-200 mt-0.5">{customSignee}</p>
        </div>
        <div>
          <span class="text-slate-500 dark:text-slate-400">Tanggal Terbit:</span>
          <p class="font-semibold text-slate-800 dark:text-slate-200 mt-0.5">{formatDateIndo(successResult.letterDate)}</p>
        </div>
      </div>

      <div class="flex flex-wrap items-center gap-3">
        <button
          type="button"
          onclick={resetForNew}
          class="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-white dark:bg-slate-100 dark:hover:bg-white dark:text-slate-900 text-xs font-semibold shadow-sm transition-all cursor-pointer"
        >
          <RefreshCw class="h-3.5 w-3.5" />
          <span>Buat Nomor Lainnya</span>
        </button>
        <button
          type="button"
          onclick={() => router.navigate('/agenda')}
          class="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-white dark:bg-slate-900 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 border border-slate-300 dark:border-slate-700 text-xs font-semibold transition-all cursor-pointer"
        >
          <span>Lihat di Buku Agenda</span>
          <ArrowRight class="h-3.5 w-3.5" />
        </button>
      </div>
    </div>
  {/if}

  <!-- BATCH SUCCESS BANNER -->
  {#if batchSuccessResult}
    <div class="bg-blue-50 dark:bg-blue-950/40 border-2 border-blue-500/50 rounded-2xl p-6 sm:p-8 shadow-xl shadow-blue-500/5 animate-in fade-in duration-200 space-y-6">
      <div class="flex items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <div class="h-12 w-12 rounded-xl bg-blue-600 text-white flex items-center justify-center shrink-0 shadow-md shadow-blue-600/20">
            <Layers class="h-7 w-7" />
          </div>
          <div>
            <span class="text-xs uppercase tracking-wider font-bold text-blue-700 dark:text-blue-300">
              Batch Generator Berhasil
            </span>
            <h3 class="text-xl sm:text-2xl font-black text-slate-900 dark:text-white tracking-tight">
              {batchSuccessResult.count} Nomor Surat Berurutan Resmi Diterbitkan!
            </h3>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <button
            type="button"
            onclick={handleCopyAllBatch}
            class="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold shadow-md shadow-blue-600/20 transition-all active:scale-95 cursor-pointer"
          >
            {#if copiedBatch}
              <Check class="h-4 w-4" />
              <span>Semua Tersalin!</span>
            {:else}
              <Copy class="h-4 w-4" />
              <span>Salin Semua ({batchSuccessResult.count})</span>
            {/if}
          </button>
          <button
            type="button"
            onclick={exportBatchCSV}
            class="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shadow-md shadow-emerald-600/20 transition-all active:scale-95 cursor-pointer"
          >
            <FileSpreadsheet class="h-4 w-4" />
            <span>Ekspor CSV</span>
          </button>
        </div>
      </div>

      <div class="bg-white dark:bg-slate-900 border border-blue-200 dark:border-blue-800 rounded-xl p-4 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
        <div>
          <span class="text-slate-400 font-medium">Rentang Nomor yang Diterbitkan:</span>
          <p class="font-mono text-base font-bold text-blue-700 dark:text-blue-300 mt-0.5">
            {batchSuccessResult.startNumber} &nbsp;&rarr;&nbsp; {batchSuccessResult.endNumber}
          </p>
        </div>
        <div class="text-slate-500 font-semibold bg-blue-50 dark:bg-blue-900/40 px-3 py-1.5 rounded-lg border border-blue-100 dark:border-blue-800">
          Total: {batchSuccessResult.count} Surat
        </div>
      </div>

      <div class="bg-white dark:bg-slate-900 border border-blue-200 dark:border-blue-800 rounded-xl overflow-hidden shadow-xs">
        <div class="max-h-80 overflow-y-auto">
          <table class="w-full text-left text-xs">
            <thead class="bg-slate-50 dark:bg-slate-800/80 border-b border-slate-200 dark:border-slate-800 text-slate-500 font-bold sticky top-0">
              <tr>
                <th class="py-2.5 px-3 w-14 text-center">Urut</th>
                <th class="py-2.5 px-3">Nomor Surat Resmi</th>
                <th class="py-2.5 px-3">Perihal</th>
                <th class="py-2.5 px-3">Pemohon / Mahasiswa</th>
                <th class="py-2.5 px-3">Tujuan</th>
                <th class="py-2.5 px-3 text-center w-16">Aksi</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 dark:divide-slate-800 text-slate-700 dark:text-slate-300">
              {#each batchSuccessResult.letters as l}
                <tr class="hover:bg-slate-50/60 dark:hover:bg-slate-800/40">
                  <td class="py-2.5 px-3 text-center font-mono font-bold text-slate-500">#{l.sequenceNumber}</td>
                  <td class="py-2.5 px-3 font-mono font-bold text-blue-700 dark:text-blue-300">{l.fullNumber}</td>
                  <td class="py-2.5 px-3 font-medium truncate max-w-[200px]" title={l.subject}>{l.subject}</td>
                  <td class="py-2.5 px-3 text-slate-600 dark:text-slate-300">{l.applicantName}</td>
                  <td class="py-2.5 px-3 text-slate-500">{l.recipient || "-"}</td>
                  <td class="py-2.5 px-3 text-center">
                    <button
                      type="button"
                      onclick={() => handleCopy(l.fullNumber)}
                      title="Salin nomor ini"
                      class="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded text-slate-500 cursor-pointer"
                    >
                      <Copy class="h-3.5 w-3.5" />
                    </button>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </div>

      <div class="flex flex-wrap items-center gap-3">
        <button
          type="button"
          onclick={resetForNew}
          class="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-white dark:bg-slate-100 dark:hover:bg-white dark:text-slate-900 text-xs font-semibold shadow-sm transition-all cursor-pointer"
        >
          <RefreshCw class="h-3.5 w-3.5" />
          <span>Buat Batch Lainnya</span>
        </button>
        <button
          type="button"
          onclick={() => router.navigate('/agenda')}
          class="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-white dark:bg-slate-900 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 border border-slate-300 dark:border-slate-700 text-xs font-semibold transition-all cursor-pointer"
        >
          <span>Buka Buku Agenda</span>
          <ArrowRight class="h-3.5 w-3.5" />
        </button>
      </div>
    </div>
  {/if}

  <!-- Main Form & Preview Grid (Exact screenshot match) -->
  <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
    <!-- Left Column: Form Card (7 cols) -->
    <div class="lg:col-span-7 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 sm:p-8 shadow-sm">
      <div class="mb-6 pb-6 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
        <div>
          <h2 class="text-base sm:text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
            {#if mode === 'batch'}
              <Layers class="h-5 w-5 text-blue-600" />
              <span>Form Generator Banyak Surat (Batch)</span>
            {:else if mode === 'manual'}
              <PenTool class="h-5 w-5 text-purple-600" />
              <span>Form Input Nomor Surat Manual (Admin)</span>
            {:else}
              <FileText class="h-5 w-5 text-red-600" />
              <span>Form Generator Satu Nomor Surat</span>
            {/if}
          </h2>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">
            {#if mode === 'batch'}
              Terbitkan beberapa nomor surat berurutan sekaligus dalam 1 kali klik tanpa risiko bentrok.
            {:else if mode === 'manual'}
              Staf dapat memasukkan nomor urut spesifik, surat susulan/backdate, atau format custom.
            {:else}
              Sistem otomatis menetapkan nomor urut berikutnya sesuai buku agenda resmi FIT.
            {/if}
          </p>
        </div>
        <span
          class="px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider shrink-0 {mode === 'batch' ? 'bg-blue-50 text-blue-700 dark:bg-blue-950/60 dark:text-blue-300' : mode === 'manual' ? 'bg-purple-50 text-purple-700 dark:bg-purple-950/60 dark:text-purple-300' : 'bg-red-50 text-red-700 dark:bg-red-950/60 dark:text-red-400 border border-red-200 dark:border-red-900/50'}"
        >
          {mode === 'batch' ? 'Mode Batch' : mode === 'manual' ? 'Mode Manual' : 'Mode Tunggal'}
        </span>
      </div>

      {#if errorMsg}
        <div class="mb-6 p-4 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 flex items-start gap-3 text-red-700 dark:text-red-300 text-xs font-medium">
          <AlertCircle class="h-4 w-4 shrink-0 mt-0.5" />
          <span>{errorMsg}</span>
        </div>
      {/if}

      <form onsubmit={handleSubmit} class="space-y-4">
        <!-- MANUAL SPECIFIC INPUTS -->
        {#if mode === 'manual'}
          <div class="p-4 rounded-xl bg-purple-50 dark:bg-purple-950/30 border border-purple-200 dark:border-purple-800 text-xs space-y-3">
            <div class="font-bold text-purple-900 dark:text-purple-300 flex items-center gap-1.5">
              <Info class="w-4 h-4" />
              <span>Opsi Penomoran Khusus Staf Sekretariat</span>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label for="manual-seq" class="block font-semibold text-purple-900 dark:text-purple-200 mb-1">Nomor Urut Manual (Opsional)</label>
                <input
                  id="manual-seq"
                  type="number"
                  bind:value={manualSequence}
                  placeholder="Misal: 1530"
                  class="w-full px-3 py-2 bg-white dark:bg-slate-800 border border-purple-300 dark:border-purple-700 rounded-lg text-xs"
                />
              </div>
              <div>
                <label for="manual-full" class="block font-semibold text-purple-900 dark:text-purple-200 mb-1">Nomor Lengkap Spesifik (Opsional)</label>
                <input
                  id="manual-full"
                  type="text"
                  bind:value={manualFullNumber}
                  placeholder="Misal: 1530/AKD01/IT-DEK/2026"
                  class="w-full px-3 py-2 bg-white dark:bg-slate-800 border border-purple-300 dark:border-purple-700 rounded-lg text-xs"
                />
              </div>
            </div>
          </div>
        {/if}

        <!-- BATCH SPECIFIC CONTROLS -->
        {#if mode === 'batch'}
          <div class="p-4 rounded-xl bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 text-xs space-y-3">
            <div class="flex items-center justify-between">
              <div>
                <span class="font-bold text-blue-900 dark:text-blue-200">Jumlah Nomor yang Ingin Diterbitkan:</span>
                <p class="text-blue-700 dark:text-blue-400 text-[11px] mt-0.5">Alokasi nomor urut beruntun sekaligus (Maksimal 100 nomor per batch).</p>
              </div>
              <div class="flex items-center gap-2">
                <input
                  type="number"
                  min="1"
                  max="100"
                  bind:value={batchCount}
                  onchange={(e) => handleBatchCountChange(parseInt((e.target as HTMLInputElement).value, 10))}
                  class="w-20 px-3 py-1.5 bg-white dark:bg-slate-800 border border-blue-300 dark:border-blue-700 rounded-lg font-mono font-bold text-center text-sm"
                />
                <span class="font-semibold text-blue-900 dark:text-blue-200">Surat</span>
              </div>
            </div>

            <div class="pt-2 border-t border-blue-200/60 dark:border-blue-800/60 flex items-center justify-between">
              <label class="flex items-center gap-2 cursor-pointer select-none">
                <input
                  type="checkbox"
                  bind:checked={batchDetailed}
                  class="rounded text-blue-600 focus:ring-blue-500"
                />
                <span class="font-semibold text-blue-900 dark:text-blue-200">Isi Rincian Tiap Surat (Mahasiswa / Mitra / Penerima Berbeda)</span>
              </label>
              {#if batchDetailed}
                <button
                  type="button"
                  onclick={addBatchRow}
                  class="inline-flex items-center gap-1 text-[11px] font-bold text-blue-600 dark:text-blue-400 hover:underline cursor-pointer"
                >
                  <Plus class="w-3.5 h-3.5" />
                  <span>Tambah Baris</span>
                </button>
              {/if}
            </div>

            {#if batchDetailed}
              <div class="space-y-2 max-h-60 overflow-y-auto pr-1 pt-1">
                {#each batchRows as row, idx}
                  <div class="p-2.5 bg-white dark:bg-slate-800 border border-blue-200 dark:border-blue-700 rounded-lg flex items-center gap-2">
                    <span class="font-mono font-bold text-blue-600 text-xs w-6">#{idx + 1}</span>
                    <input
                      type="text"
                      bind:value={row.applicantName}
                      placeholder="Nama Mahasiswa / PIC"
                      class="flex-1 px-2.5 py-1 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded text-xs"
                    />
                    <input
                      type="text"
                      bind:value={row.recipient}
                      placeholder="Mitra / Perusahaan"
                      class="flex-1 px-2.5 py-1 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded text-xs"
                    />
                    {#if batchRows.length > 1}
                      <button
                        type="button"
                        onclick={() => removeBatchRow(idx)}
                        class="p-1 text-slate-400 hover:text-red-500 cursor-pointer"
                      >
                        <Trash2 class="w-3.5 h-3.5" />
                      </button>
                    {/if}
                  </div>
                {/each}
              </div>
            {/if}
          </div>
        {/if}

        <!-- 1. PROGRAM STUDI / UNIT PEMOHON -->
        <div>
          <label for="unit-select" class="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
            PROGRAM STUDI / UNIT PEMOHON <span class="text-red-500">*</span>
          </label>
          <select
            id="unit-select"
            bind:value={unitId}
            onchange={onUnitChange}
            class="w-full bg-slate-50 dark:bg-[#1A2234] border border-slate-300 dark:border-slate-700/80 rounded-xl px-4 py-2.5 text-xs sm:text-sm text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-red-500 focus:outline-none transition-all cursor-pointer"
          >
            {#each groupedUnits as group}
              <optgroup label={group.label}>
                {#each group.items as u}
                  <option value={u.id}>{u.name} ({u.signee_code || u.code})</option>
                {/each}
              </optgroup>
            {/each}
          </select>
        </div>

        <!-- 2. KLASIFIKASI & PENANDATANGAN ROW (2 cols) -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label for="category-select" class="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
              KLASIFIKASI PERIHAL SURAT <span class="text-red-500">*</span>
            </label>
            <select
              id="category-select"
              bind:value={categoryId}
              onchange={onCategoryChange}
              class="w-full bg-slate-50 dark:bg-[#1A2234] border border-slate-300 dark:border-slate-700/80 rounded-xl px-4 py-2.5 text-xs sm:text-sm text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-red-500 focus:outline-none transition-all cursor-pointer"
            >
              {#each groupedCategories as group}
                <optgroup label={group.label}>
                  {#each group.items as c}
                    <option value={c.id}>[{c.code}] {c.name}</option>
                  {/each}
                </optgroup>
              {/each}
            </select>
          </div>

          <div>
            <label for="signee-select" class="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
              PEJABAT PENANDATANGAN <span class="text-red-500">*</span>
            </label>
            <select
              id="signee-select"
              bind:value={customSignee}
              class="w-full bg-slate-50 dark:bg-[#1A2234] border border-slate-300 dark:border-slate-700/80 rounded-xl px-4 py-2.5 text-xs sm:text-sm text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-red-500 focus:outline-none transition-all cursor-pointer"
            >
              {#each signeeGroups as group}
                <optgroup label={group.group}>
                  {#each group.options as opt}
                    <option value={opt.code}>{opt.label}</option>
                  {/each}
                </optgroup>
              {/each}
            </select>
          </div>
        </div>

        <!-- 3. TANGGAL SURAT -->
        <div>
          <label for="date-input" class="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
            TANGGAL SURAT <span class="text-red-500">*</span>
          </label>
          <input
            id="date-input"
            type="date"
            bind:value={letterDate}
            required
            class="w-full bg-slate-50 dark:bg-[#1A2234] border border-slate-300 dark:border-slate-700/80 rounded-xl px-4 py-2.5 text-xs sm:text-sm text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-red-500 focus:outline-none transition-all"
          />
        </div>

        <!-- 4. PERIHAL / URAIAN SURAT -->
        <div>
          <label for="subject-textarea" class="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
            PERIHAL / URAIAN SURAT <span class="text-red-500">*</span>
          </label>
          <textarea
            id="subject-textarea"
            rows="2"
            bind:value={subject}
            required
            placeholder="Contoh: Surat Tugas Dosen Pembimbing Lapangan Magang MBKM Semester Ganjil 2026/2027"
            class="w-full bg-slate-50 dark:bg-[#1A2234] border border-slate-300 dark:border-slate-700/80 rounded-xl px-4 py-2.5 text-xs sm:text-sm text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:ring-2 focus:ring-red-500 focus:outline-none transition-all"
          ></textarea>
        </div>

        <!-- 5. PEMOHON & WHATSAPP (2 cols) -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label for="applicant-input" class="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
              {mode === 'batch' ? 'NAMA KOORDINATOR / PIC PENGAJU' : 'NAMA PEMOHON / PIC'} <span class="text-red-500">*</span>
            </label>
            <input
              id="applicant-input"
              type="text"
              bind:value={applicantName}
              required
              placeholder="Nama Dosen / Staff / Koordinator"
              class="w-full bg-slate-50 dark:bg-[#1A2234] border border-slate-300 dark:border-slate-700/80 rounded-xl px-4 py-2.5 text-xs sm:text-sm text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:ring-2 focus:ring-red-500 focus:outline-none transition-all"
            />
          </div>

          <div>
            <label for="phone-input" class="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
              NOMOR WHATSAPP PEMOHON (OPSIONAL)
            </label>
            <input
              id="phone-input"
              type="tel"
              bind:value={applicantContact}
              placeholder="0812xxxxxxxx"
              class="w-full bg-slate-50 dark:bg-[#1A2234] border border-slate-300 dark:border-slate-700/80 rounded-xl px-4 py-2.5 text-xs sm:text-sm text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:ring-2 focus:ring-red-500 focus:outline-none transition-all"
            />
          </div>
        </div>

        <!-- 6. TUJUAN / PENERIMA SURAT -->
        {#if !batchDetailed || mode !== 'batch'}
          <div>
            <label for="recipient-input" class="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
              TUJUAN / PENERIMA SURAT (OPSIONAL)
            </label>
            <input
              id="recipient-input"
              type="text"
              bind:value={recipient}
              placeholder="Contoh: HR Division PT Telkom Indonesia (Persero) Tbk"
              class="w-full bg-slate-50 dark:bg-[#1A2234] border border-slate-300 dark:border-slate-700/80 rounded-xl px-4 py-2.5 text-xs sm:text-sm text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:ring-2 focus:ring-red-500 focus:outline-none transition-all"
            />
          </div>
        {/if}

        <!-- 7. CATATAN TAMBAHAN -->
        <div>
          <label for="notes-input" class="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
            CATATAN TAMBAHAN (OPSIONAL)
          </label>
          <input
            id="notes-input"
            type="text"
            bind:value={notes}
            placeholder="Keterangan berkas, agenda kegiatan, dll."
            class="w-full bg-slate-50 dark:bg-[#1A2234] border border-slate-300 dark:border-slate-700/80 rounded-xl px-4 py-2.5 text-xs sm:text-sm text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:ring-2 focus:ring-red-500 focus:outline-none transition-all"
          />
        </div>

        <!-- Submit Button -->
        <div class="pt-2">
          <button
            type="submit"
            disabled={isPending}
            class="w-full flex items-center justify-center gap-2 py-3.5 px-6 rounded-xl font-bold text-sm text-white shadow-lg transition-all active:scale-[0.99] cursor-pointer disabled:opacity-50 {mode === 'batch' ? 'bg-blue-600 hover:bg-blue-700 shadow-blue-600/25' : mode === 'manual' ? 'bg-purple-600 hover:bg-purple-700 shadow-purple-600/25' : 'bg-red-600 hover:bg-red-700 shadow-red-600/25'}"
          >
            {#if isPending}
              <RefreshCw class="h-4 w-4 animate-spin" />
              <span>Memproses {mode === 'batch' ? `${batchCount} Nomor Surat...` : 'Nomor Surat...'}</span>
            {:else if mode === 'batch'}
              <Layers class="h-4 w-4" />
              <span>Terbitkan {batchCount} Nomor Surat Sekaligus</span>
            {:else if mode === 'manual'}
              <PenTool class="h-4 w-4" />
              <span>Daftarkan Nomor Surat Manual</span>
            {:else}
              <Sparkles class="h-4 w-4" />
              <span>Terbitkan Satu Nomor Surat Otomatis</span>
            {/if}
          </button>
        </div>
      </form>
    </div>

    <!-- Right Column: Live Preview & Guidance (5 cols) (Exact screenshot match) -->
    <div class="lg:col-span-5 space-y-6">
      <!-- Card 1: LIVE PREVIEW FORMAT SURAT FIT -->
      <div class="bg-gradient-to-br from-slate-900 to-slate-950 text-white rounded-2xl p-6 border border-slate-800 shadow-lg">
        <div class="flex items-center justify-between pb-4 mb-4 border-b border-slate-800">
          <div class="flex items-center gap-2">
            <Sparkles class="h-4 w-4 text-amber-400" />
            <span class="text-xs font-bold uppercase tracking-wider text-slate-300">
              LIVE PREVIEW FORMAT SURAT FIT
            </span>
          </div>
          <span
            class="text-[10px] border px-2 py-0.5 rounded-full font-mono font-semibold {mode === 'batch' ? 'bg-blue-900/40 text-blue-300 border-blue-500/30' : mode === 'manual' ? 'bg-purple-900/40 text-purple-300 border-purple-500/30' : 'bg-red-900/40 text-red-300 border-red-500/30'}"
          >
            {mode === 'batch' ? `Batch ${batchCount} Surat` : mode === 'manual' ? 'Custom Manual' : 'Auto-Increment'}
          </span>
        </div>

        <!-- Big Inset Output Box -->
        <div class="bg-slate-800/80 rounded-xl p-4 text-center border border-slate-700/80 my-3">
          <div class="text-[11px] text-slate-400 uppercase font-medium mb-1">
            {mode === 'batch' ? 'Format Alokasi Rentang Nomor:' : 'NOMOR YANG AKAN DITERBITKAN:'}
          </div>
          <div class="font-mono text-lg sm:text-xl font-black text-amber-300 tracking-tight break-all">
            {previewNumber}
          </div>
          {#if mode === 'batch'}
            <div class="text-[11px] text-blue-400 font-semibold mt-1">
              Sistem akan mengalokasikan {batchCount} nomor urut berurutan tanpa celah
            </div>
          {/if}
        </div>

        <!-- Structure Breakdown -->
        <div class="mt-5 space-y-2.5 text-xs">
          <div class="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-2">
            RINCIAN SEGMEN NOMOR SESUAI PANDUAN PU.006:
          </div>

          <!-- Segmen 1 -->
          <div class="flex items-center justify-between py-1.5 border-b border-slate-800">
            <span class="text-slate-400">1. Nomor Urut:</span>
            <span class="font-mono font-bold text-amber-400 bg-slate-800 px-2 py-0.5 rounded">
              {mode === 'batch' ? `${batchCount} Nomor Beruntun` : mode === 'manual' && manualSequence ? manualSequence : 'Urutan Otomatis'}
            </span>
          </div>

          <!-- Segmen 2 -->
          <div class="flex items-center justify-between py-1.5 border-b border-slate-800">
            <span class="text-slate-400">2. Klasifikasi Perihal:</span>
            <span class="font-mono font-bold text-blue-400 bg-slate-800 px-2 py-0.5 rounded">
              {customClassification || 'SKR05'}
            </span>
          </div>

          <!-- Segmen 3 -->
          <div class="flex items-center justify-between py-1.5 border-b border-slate-800">
            <span class="text-slate-400">3. Pejabat / Penandatangan:</span>
            <span class="font-mono font-bold text-emerald-400 bg-slate-800 px-2 py-0.5 rounded">
              {customSignee || 'IT-DEK'}
            </span>
          </div>

          <!-- Segmen 4 -->
          <div class="flex items-center justify-between py-1.5">
            <span class="text-slate-400">4. Tahun Surat:</span>
            <span class="font-mono font-bold text-purple-400 bg-slate-800 px-2 py-0.5 rounded">
              {previewYear}
            </span>
          </div>
        </div>
      </div>

      <!-- Card 2: Quick Guidance Info -->
      <div class="bg-slate-50 dark:bg-slate-800/50 rounded-2xl p-5 border border-slate-200 dark:border-slate-800 text-xs text-slate-600 dark:text-slate-300 space-y-3">
        <div class="flex items-center gap-2 font-bold text-slate-900 dark:text-white">
          <Info class="h-4 w-4 text-blue-600" />
          <span>Kapan Menggunakan Mode Batch?</span>
        </div>
        <div class="space-y-1.5 text-[11px] leading-relaxed text-slate-500 dark:text-slate-400">
          <p>
            &bull; <strong>Surat Tugas Magang / MBKM:</strong> Ketika prodi menerbitkan puluhan surat pengantar untuk mahasiswa ke mitra industri yang berbeda.
          </p>
          <p>
            &bull; <strong>Surat Undangan Rapat / Narasumber:</strong> Ketika mengundang belasan pemateri atau dosen penguji sidang.
          </p>
          <p>
            &bull; <strong>Blok Nomor Kegiatan:</strong> Alokasi cepat rentang nomor berurutan tanpa perlu mengulang-ulang klik form puluhan kali.
          </p>
        </div>
      </div>
    </div>
  </div>
</div>
