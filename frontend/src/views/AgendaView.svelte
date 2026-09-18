<script lang="ts">
  import { onMount } from 'svelte';
  import { 
    BookOpenCheck, 
    Search, 
    Trash2, 
    Edit, 
    Eye, 
    RefreshCw, 
    Check, 
    Copy, 
    AlertCircle, 
    ChevronLeft, 
    ChevronRight,
    X,
    FileSpreadsheet,
    Lock,
    ShieldCheck,
    LogOut,
    Plus,
    Inbox,
    Send,
    ArrowDownLeft,
    ArrowUpRight,
    Building2,
    Calendar
  } from 'lucide-svelte';
  import { admin } from '../lib/admin.svelte';
  import { auth } from '../lib/auth.svelte';
  import { router } from '../lib/router.svelte';
  import { formatDateIndo, getCategoryBadgeClass, cn } from '../lib/utils';

  let isUnlocked = $derived(admin.isAdmin);

  let letters = $state<any[]>([]);
  let total = $state(0);
  let units = $state<any[]>([]);
  let categories = $state<any[]>([]);
  let loading = $state(false);

  // Filters
  let search = $state('');
  let selectedYear = $state<number | null>(new Date().getFullYear());
  let selectedMonth = $state<number | null>(null);
  let selectedUnit = $state('ALL');
  let selectedCategory = $state('ALL');
  let selectedLetterType = $state<'ALL' | 'OUTGOING' | 'INCOMING'>('ALL');
  let page = $state(1);
  const pageSize = 25;

  // Selected for bulk
  let selectedIds = $state<string[]>([]);

  // Modals
  let detailLetter = $state<any | null>(null);
  let editLetter = $state<any | null>(null);
  let deleteLetterId = $state<string | null>(null);
  let bulkDeleteOpen = $state(false);
  let editForm = $state({
    subject: '',
    recipient: '',
    applicantName: '',
    applicantContact: '',
    status: 'ISSUED',
    notes: '',
    sender: '',
    receivedDate: ''
  });
  let modalLoading = $state(false);
  let copied = $state(false);

  // Incoming Letter Modal State
  let incomingModalOpen = $state(false);
  let incomingLoading = $state(false);
  let incomingError = $state<string | null>(null);
  let nextSeqPreview = $state<number | null>(null);
  let incomingForm = $state({
    manualSequence: null as number | null,
    fullNumber: '',
    sender: '',
    letterDate: new Date().toISOString().slice(0, 10),
    receivedDate: new Date().toISOString().slice(0, 10),
    subject: '',
    recipient: 'Dekan Fakultas Ilmu Terapan',
    unitId: '',
    categoryId: '',
    notes: ''
  });

  async function lockAgenda() {
    await admin.logout();
  }

  async function fetchMetadata() {
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
  }

  async function fetchNextSequence() {
    try {
      const yr = selectedYear || new Date().getFullYear();
      const res = await fetch(`/api/letters/next-sequence?year=${yr}`);
      if (res.ok) {
        const data = await res.json();
        nextSeqPreview = data.nextSequence;
      }
    } catch (e) {
      console.error(e);
    }
  }

  async function openIncomingModal() {
    incomingError = null;
    incomingForm.manualSequence = null;
    incomingForm.fullNumber = '';
    incomingForm.sender = '';
    incomingForm.subject = '';
    incomingForm.notes = '';
    incomingForm.letterDate = new Date().toISOString().slice(0, 10);
    incomingForm.receivedDate = new Date().toISOString().slice(0, 10);
    incomingForm.recipient = 'Dekan Fakultas Ilmu Terapan';
    if (units.length > 0 && !incomingForm.unitId) {
      incomingForm.unitId = units[0].id;
    }
    if (categories.length > 0 && !incomingForm.categoryId) {
      incomingForm.categoryId = categories[0].id;
    }
    await fetchNextSequence();
    incomingModalOpen = true;
  }

  async function submitIncomingLetter() {
    if (!incomingForm.fullNumber.trim()) {
      incomingError = 'Nomor surat asli dari pengirim wajib diisi.';
      return;
    }
    if (!incomingForm.sender.trim()) {
      incomingError = 'Asal instansi / pengirim surat wajib diisi.';
      return;
    }
    if (!incomingForm.subject.trim()) {
      incomingError = 'Perihal surat masuk wajib diisi.';
      return;
    }
    if (!incomingForm.unitId || !incomingForm.categoryId) {
      incomingError = 'Unit tujuan disposisi dan kategori wajib dipilih.';
      return;
    }

    incomingLoading = true;
    incomingError = null;
    try {
      const res = await fetch('/api/letters/incoming', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...auth.getAuthHeaders()
        },
        body: JSON.stringify({
          manual_sequence_number: incomingForm.manualSequence ? Number(incomingForm.manualSequence) : undefined,
          full_number: incomingForm.fullNumber.trim(),
          sender: incomingForm.sender.trim(),
          letter_date: incomingForm.letterDate,
          received_date: incomingForm.receivedDate,
          subject: incomingForm.subject.trim(),
          recipient: incomingForm.recipient.trim() || undefined,
          unit_id: incomingForm.unitId,
          category_id: incomingForm.categoryId,
          notes: incomingForm.notes.trim() || undefined
        })
      });
      const data = await res.json();
      if (data.success) {
        incomingModalOpen = false;
        page = 1;
        fetchLetters();
      } else {
        incomingError = data.error || 'Gagal menyimpan surat masuk.';
      }
    } catch (e: any) {
      incomingError = e?.message || 'Terjadi kesalahan saat menghubungi server.';
    } finally {
      incomingLoading = false;
    }
  }

  async function fetchLetters() {
    loading = true;
    try {
      const params = new URLSearchParams();
      params.append('limit', pageSize.toString());
      params.append('offset', ((page - 1) * pageSize).toString());
      if (search.trim()) params.append('search', search.trim());
      if (selectedYear) params.append('year', selectedYear.toString());
      if (selectedMonth) params.append('month', selectedMonth.toString());
      if (selectedUnit !== 'ALL') params.append('unit_id', selectedUnit);
      if (selectedCategory !== 'ALL') params.append('category_id', selectedCategory);
      if (selectedLetterType !== 'ALL') params.append('letter_type', selectedLetterType);

      const res = await fetch(`/api/letters?${params.toString()}`, {
        headers: auth.getAuthHeaders()
      });
      const data = await res.json();
      letters = data.letters || [];
      total = data.total || 0;
    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
  }

  $effect(() => {
    if (admin.isAdmin && letters.length === 0 && !loading) {
      fetchMetadata();
      fetchLetters();
    }
  });

  onMount(() => {
    if (admin.isAdmin) {
      fetchMetadata();
      fetchLetters();
    }
  });

  function handleFilterChange() {
    page = 1;
    selectedIds = [];
    fetchLetters();
  }

  function handleSelectAll(e: Event) {
    const checked = (e.target as HTMLInputElement).checked;
    if (checked) {
      selectedIds = letters.map(l => l.id);
    } else {
      selectedIds = [];
    }
  }

  function toggleSelect(id: string) {
    if (selectedIds.includes(id)) {
      selectedIds = selectedIds.filter(item => item !== id);
    } else {
      selectedIds = [...selectedIds, id];
    }
  }

  function openEdit(letter: any) {
    editLetter = letter;
    editForm = {
      subject: letter.subject || '',
      recipient: letter.recipient || '',
      applicantName: letter.applicant_name || '',
      applicantContact: letter.applicant_contact || '',
      status: letter.status || 'ISSUED',
      notes: letter.notes || '',
      sender: letter.sender || '',
      receivedDate: letter.received_date || ''
    };
  }

  async function saveEdit() {
    if (!editLetter) return;
    modalLoading = true;
    try {
      const res = await fetch(`/api/letters/${editLetter.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', ...auth.getAuthHeaders() },
        body: JSON.stringify({
          subject: editForm.subject,
          recipient: editForm.recipient || null,
          applicant_name: editForm.applicantName,
          applicant_contact: editForm.applicantContact || null,
          status: editForm.status,
          notes: editForm.notes || null,
          sender: editForm.sender || null,
          received_date: editForm.receivedDate || null
        })
      });
      const data = await res.json();
      if (data.success) {
        editLetter = null;
        fetchLetters();
      }
    } catch (e) {
      console.error(e);
    } finally {
      modalLoading = false;
    }
  }

  async function confirmDeleteSingle() {
    if (!deleteLetterId) return;
    modalLoading = true;
    try {
      const res = await fetch(`/api/letters/${deleteLetterId}`, {
        method: 'DELETE',
        headers: auth.getAuthHeaders()
      });
      const data = await res.json();
      if (data.success) {
        deleteLetterId = null;
        fetchLetters();
      }
    } catch (e) {
      console.error(e);
    } finally {
      modalLoading = false;
    }
  }

  async function confirmBulkDelete() {
    if (selectedIds.length === 0) return;
    modalLoading = true;
    try {
      const res = await fetch('/api/letters/bulk-delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...auth.getAuthHeaders() },
        body: JSON.stringify({ ids: selectedIds })
      });
      const data = await res.json();
      if (data.success) {
        selectedIds = [];
        bulkDeleteOpen = false;
        fetchLetters();
      }
    } catch (e) {
      console.error(e);
    } finally {
      modalLoading = false;
    }
  }

  function exportCSV() {
    if (letters.length === 0) return;
    const headers = ["No Urut", "Jenis Surat", "Nomor Surat", "Perihal", "Asal / Pengirim", "Kategori", "Pemohon / Tujuan", "Unit", "Tanggal Surat", "Tanggal Diterima", "Status"];
    const rows = letters.map(l => [
      l.sequence_number,
      l.letter_type === 'INCOMING' ? 'SURAT MASUK' : 'SURAT KELUAR',
      `"${l.full_number}"`,
      `"${(l.subject || '').replace(/"/g, '""')}"`,
      `"${(l.sender || '-').replace(/"/g, '""')}"`,
      `"${l.category_name || ''}"`,
      `"${((l.letter_type === 'INCOMING' ? l.recipient : l.applicant_name) || '').replace(/"/g, '""')}"`,
      `"${l.unit_name || ''}"`,
      l.letter_date,
      l.received_date || '-',
      l.status
    ]);
    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `buku_agenda_fit_${selectedLetterType.toLowerCase()}_${selectedYear || 'all'}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  function copyText(txt: string) {
    navigator.clipboard.writeText(txt);
    copied = true;
    setTimeout(() => copied = false, 2000);
  }

  const totalPages = $derived(Math.max(1, Math.ceil(total / pageSize)));
</script>

{#if !isUnlocked}
  <!-- ACCESS GATE SCREEN (Restricted to Staf Sekretariat) -->
  <div class="max-w-md mx-auto py-12 px-4 animate-in fade-in zoom-in-95 duration-200">
    <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 sm:p-8 shadow-xl text-center space-y-5">
      <div class="w-16 h-16 rounded-2xl bg-red-100 dark:bg-red-950/60 text-red-600 dark:text-red-400 mx-auto flex items-center justify-center shadow-lg shadow-red-600/10 ring-1 ring-red-500/20">
        <Lock class="w-8 h-8" />
      </div>

      <div>
        <span class="px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider rounded-full bg-red-100 dark:bg-red-950/60 text-red-600 dark:text-red-400 border border-red-200 dark:border-red-800">
          Khusus Staf Sekretariat
        </span>
        <h2 class="text-xl font-black text-slate-900 dark:text-white mt-2">
          Buku Agenda Surat Resmi
        </h2>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-2 leading-relaxed">
          Halaman ini khusus untuk staf sekretariat fakultas. Silakan login menggunakan akun Google resmi <code class="font-mono bg-slate-100 dark:bg-slate-800 px-1 py-0.5 rounded text-red-600 font-bold">sekretariat@tass.telkomuniversity.ac.id</code>.
        </p>
      </div>

      <button
        type="button"
        onclick={() => auth.openLoginModal()}
        class="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-red-600 to-amber-600 hover:from-red-700 hover:to-amber-700 text-white font-bold text-xs shadow-md shadow-red-500/20 transition-all flex items-center justify-center gap-2 cursor-pointer"
      >
        <ShieldCheck class="w-4 h-4" />
        <span>Masuk dengan Google (sekretariat@tass...)</span>
      </button>

      {#if auth.isLoggedIn && !admin.isAdmin}
        <div class="p-3 bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 rounded-xl text-left text-xs text-amber-800 dark:text-amber-300">
          Anda sedang login sebagai <strong>{auth.user?.email}</strong>. Untuk melihat riwayat nomor surat yang pernah Anda ajukan, silakan buka menu <strong>Histori Saya</strong>.
        </div>
      {/if}
    </div>
  </div>
{:else}
  <!-- UNLOCKED AGENDA TABLE VIEW -->
  <div class="space-y-6">
    <!-- Title & Action Bar -->
    <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <div class="flex items-center gap-2 flex-wrap">
          <h1 class="text-xl font-black text-slate-900 dark:text-white tracking-tight">
            Buku Agenda Surat Resmi
          </h1>
          <span class="px-2.5 py-0.5 text-xs font-bold rounded-full bg-red-100 dark:bg-red-950/60 text-red-600 dark:text-red-400">
            {total} Dokumen
          </span>
          <span class="px-2 py-0.5 text-[10px] font-bold rounded-full bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800">
            Staf Sekretariat
          </span>
        </div>
        <p class="text-xs text-slate-500 mt-1">
          Daftar seluruh nomor surat resmi (Surat Keluar & Surat Masuk) Fakultas Ilmu Terapan Telkom University.
        </p>
      </div>

      <div class="flex items-center gap-2 flex-wrap">
        <!-- Input Surat Masuk Button -->
        <button
          onclick={openIncomingModal}
          class="inline-flex items-center gap-1.5 px-3.5 py-2 bg-gradient-to-r from-red-600 to-amber-600 hover:from-red-700 hover:to-amber-700 text-white rounded-xl text-xs font-bold shadow-sm shadow-red-500/20 transition-all cursor-pointer"
        >
          <Plus class="w-4 h-4" />
          <span>+ Input Surat Masuk</span>
        </button>

        <button
          onclick={exportCSV}
          class="inline-flex items-center gap-1.5 px-3.5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold shadow-xs transition-colors cursor-pointer"
        >
          <FileSpreadsheet class="w-4 h-4" />
          <span>Ekspor CSV</span>
        </button>

        {#if admin.isAdmin && selectedIds.length > 0}
          <button
            onclick={() => bulkDeleteOpen = true}
            class="inline-flex items-center gap-1.5 px-3.5 py-2 bg-red-600 hover:bg-red-700 text-white rounded-xl text-xs font-bold shadow-xs transition-colors cursor-pointer"
          >
            <Trash2 class="w-4 h-4" />
            <span>Hapus ({selectedIds.length})</span>
          </button>
        {/if}

        <button
          onclick={lockAgenda}
          title="Kunci Akses Buku Agenda"
          class="inline-flex items-center gap-1.5 px-3 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-xl text-xs font-bold transition-colors cursor-pointer border border-slate-200 dark:border-slate-700"
        >
          <LogOut class="w-3.5 h-3.5" />
          <span>Kunci</span>
        </button>
      </div>
    </div>

    <!-- Filter Toolbar -->
    <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 shadow-sm space-y-3">
      <!-- Tab Filter: Semua Surat | Surat Keluar | Surat Masuk -->
      <div class="flex items-center gap-1.5 p-1 bg-slate-100 dark:bg-slate-800/80 rounded-xl w-fit">
        <button
          type="button"
          onclick={() => { selectedLetterType = 'ALL'; handleFilterChange(); }}
          class={cn(
            "px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5",
            selectedLetterType === 'ALL'
              ? "bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-xs"
              : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
          )}
        >
          <span>Semua Surat</span>
        </button>
        <button
          type="button"
          onclick={() => { selectedLetterType = 'OUTGOING'; handleFilterChange(); }}
          class={cn(
            "px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5",
            selectedLetterType === 'OUTGOING'
              ? "bg-white dark:bg-slate-900 text-blue-600 dark:text-blue-400 shadow-xs"
              : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
          )}
        >
          <Send class="w-3.5 h-3.5" />
          <span>Surat Keluar</span>
        </button>
        <button
          type="button"
          onclick={() => { selectedLetterType = 'INCOMING'; handleFilterChange(); }}
          class={cn(
            "px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5",
            selectedLetterType === 'INCOMING'
              ? "bg-white dark:bg-slate-900 text-emerald-600 dark:text-emerald-400 shadow-xs"
              : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
          )}
        >
          <Inbox class="w-3.5 h-3.5" />
          <span>Surat Masuk</span>
        </button>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        <!-- Search Input -->
        <div class="lg:col-span-2 relative">
          <Search class="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            bind:value={search}
            oninput={handleFilterChange}
            placeholder="Cari nomor surat, pengirim, perihal, pemohon..."
            class="w-full pl-9 pr-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-red-500/30"
          />
        </div>

        <!-- Year Filter -->
        <div>
          <select
            bind:value={selectedYear}
            onchange={handleFilterChange}
            class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white"
          >
            <option value={null}>Semua Tahun</option>
            <option value={2026}>Tahun 2026</option>
            <option value={2025}>Tahun 2025</option>
            <option value={2024}>Tahun 2024</option>
          </select>
        </div>

        <!-- Unit Filter -->
        <div>
          <select
            bind:value={selectedUnit}
            onchange={handleFilterChange}
            class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white"
          >
            <option value="ALL">Semua Unit / Prodi</option>
            {#each units as u}
              <option value={u.id}>{u.name}</option>
            {/each}
          </select>
        </div>

        <!-- Category Filter -->
        <div>
          <select
            bind:value={selectedCategory}
            onchange={handleFilterChange}
            class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white"
          >
            <option value="ALL">Semua Kategori</option>
            {#each categories as c}
              <option value={c.id}>[{c.code}] {c.name}</option>
            {/each}
          </select>
        </div>
      </div>
    </div>

    <!-- Table Area -->
    <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm overflow-hidden">
      {#if loading}
        <div class="py-16 text-center text-slate-400 flex flex-col items-center justify-center gap-2">
          <RefreshCw class="w-6 h-6 animate-spin text-red-500" />
          <span class="text-xs">Memuat agenda surat dari database...</span>
        </div>
      {:else if letters.length === 0}
        <div class="py-16 text-center text-slate-400 text-xs">
          Tidak ada surat yang ditemukan sesuai filter yang dipilih.
        </div>
      {:else}
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead class="bg-slate-50 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-800 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
              <tr>
                {#if admin.isAdmin}
                  <th class="p-3.5 w-10 text-center">
                    <input
                      type="checkbox"
                      checked={selectedIds.length === letters.length && letters.length > 0}
                      onchange={handleSelectAll}
                      class="rounded text-red-600 focus:ring-red-500"
                    />
                  </th>
                {/if}
                <th class="p-3.5 w-16 text-center">No</th>
                <th class="p-3.5">Jenis</th>
                <th class="p-3.5">Nomor Surat Lengkap</th>
                <th class="p-3.5">Perihal Surat</th>
                <th class="p-3.5">Asal / Pemohon & Unit</th>
                <th class="p-3.5">Tanggal</th>
                <th class="p-3.5 text-right">Aksi</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
              {#each letters as letter}
                <tr class="hover:bg-slate-50/70 dark:hover:bg-slate-800/40 transition-colors">
                  {#if admin.isAdmin}
                    <td class="p-3.5 text-center">
                      <input
                        type="checkbox"
                        checked={selectedIds.includes(letter.id)}
                        onchange={() => toggleSelect(letter.id)}
                        class="rounded text-red-600 focus:ring-red-500"
                      />
                    </td>
                  {/if}
                  <td class="p-3.5 text-center font-mono font-bold text-slate-400">
                    #{letter.sequence_number}
                  </td>
                  <td class="p-3.5 whitespace-nowrap">
                    {#if letter.letter_type === 'INCOMING'}
                      <span class="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800">
                        <ArrowDownLeft class="w-3 h-3 text-emerald-600" />
                        <span>Masuk</span>
                      </span>
                    {:else}
                      <span class="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-100 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 border border-blue-300 dark:border-blue-800">
                        <ArrowUpRight class="w-3 h-3 text-blue-600" />
                        <span>Keluar</span>
                      </span>
                    {/if}
                  </td>
                  <td class="p-3.5">
                    <div class="font-mono font-bold text-slate-900 dark:text-red-400 break-all">{letter.full_number}</div>
                    <span class="inline-block mt-0.5 text-[10px] font-semibold px-2 py-0.5 rounded {getCategoryBadgeClass(letter.classification_code)}">
                      {letter.category_name || 'Umum'}
                    </span>
                  </td>
                  <td class="p-3.5 max-w-xs">
                    <div class="font-medium text-slate-800 dark:text-slate-200 line-clamp-2">{letter.subject}</div>
                    {#if letter.recipient}
                      <div class="text-[11px] text-slate-400 mt-0.5">Tujuan: {letter.recipient}</div>
                    {/if}
                  </td>
                  <td class="p-3.5">
                    {#if letter.letter_type === 'INCOMING'}
                      <div class="font-semibold text-emerald-700 dark:text-emerald-400 flex items-center gap-1">
                        <Building2 class="w-3.5 h-3.5 shrink-0" />
                        <span>{letter.sender || 'Instansi Luar'}</span>
                      </div>
                      <div class="text-[11px] text-slate-400">Disposisi: {letter.unit_name || '-'}</div>
                    {:else}
                      <div class="font-semibold text-slate-800 dark:text-slate-200">{letter.applicant_name}</div>
                      <div class="text-[11px] text-slate-400">{letter.unit_name || '-'}</div>
                    {/if}
                  </td>
                  <td class="p-3.5 text-slate-500 whitespace-nowrap">
                    <div>{formatDateIndo(letter.letter_date)}</div>
                    {#if letter.letter_type === 'INCOMING' && letter.received_date}
                      <div class="text-[10px] text-slate-400">Terima: {letter.received_date}</div>
                    {/if}
                  </td>
                  <td class="p-3.5 text-right whitespace-nowrap space-x-1">
                    <button
                      onclick={() => detailLetter = letter}
                      title="Lihat Detail"
                      class="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 cursor-pointer"
                    >
                      <Eye class="w-4 h-4" />
                    </button>

                    {#if admin.isAdmin}
                      <button
                        onclick={() => openEdit(letter)}
                        title="Edit Surat"
                        class="p-1.5 rounded-lg text-slate-400 hover:text-amber-500 hover:bg-slate-100 dark:hover:bg-slate-800 cursor-pointer"
                      >
                        <Edit class="w-4 h-4" />
                      </button>
                      <button
                        onclick={() => deleteLetterId = letter.id}
                        title="Hapus Surat"
                        class="p-1.5 rounded-lg text-slate-400 hover:text-red-500 hover:bg-slate-100 dark:hover:bg-slate-800 cursor-pointer"
                      >
                        <Trash2 class="w-4 h-4" />
                      </button>
                    {/if}
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div class="p-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs text-slate-500">
          <div>
            Halaman <strong class="text-slate-800 dark:text-slate-200">{page}</strong> dari <strong class="text-slate-800 dark:text-slate-200">{totalPages}</strong> ({total} total)
          </div>
          <div class="flex items-center gap-1">
            <button
              disabled={page <= 1}
              onclick={() => { page -= 1; fetchLetters(); }}
              class="p-1.5 rounded-lg border border-slate-200 dark:border-slate-700 disabled:opacity-30 hover:bg-slate-100 dark:hover:bg-slate-800 cursor-pointer"
            >
              <ChevronLeft class="w-4 h-4" />
            </button>
            <button
              disabled={page >= totalPages}
              onclick={() => { page += 1; fetchLetters(); }}
              class="p-1.5 rounded-lg border border-slate-200 dark:border-slate-700 disabled:opacity-30 hover:bg-slate-100 dark:hover:bg-slate-800 cursor-pointer"
            >
              <ChevronRight class="w-4 h-4" />
            </button>
          </div>
        </div>
      {/if}
    </div>

    <!-- Detail Modal -->
    {#if detailLetter}
      <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-xs animate-in fade-in duration-200">
        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 max-w-lg w-full shadow-2xl relative space-y-4">
          <button 
            onclick={() => detailLetter = null}
            class="absolute right-4 top-4 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1 rounded-lg cursor-pointer"
          >
            <X class="w-5 h-5" />
          </button>

          <div class="flex items-center gap-2">
            <BookOpenCheck class="w-5 h-5 text-red-500" />
            <h3 class="text-base font-bold text-slate-900 dark:text-white">
              Detail Agenda #{detailLetter.sequence_number}
            </h3>
            {#if detailLetter.letter_type === 'INCOMING'}
              <span class="px-2 py-0.5 text-[10px] font-bold rounded-full bg-emerald-100 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300">
                Surat Masuk
              </span>
            {:else}
              <span class="px-2 py-0.5 text-[10px] font-bold rounded-full bg-blue-100 text-blue-700 dark:bg-blue-950/60 dark:text-blue-300">
                Surat Keluar
              </span>
            {/if}
          </div>

          <div class="bg-slate-50 dark:bg-slate-800/60 p-4 rounded-2xl border border-slate-200 dark:border-slate-700 space-y-1.5">
            <span class="text-[10px] uppercase font-bold text-slate-400">
              {detailLetter.letter_type === 'INCOMING' ? 'Nomor Surat Asli Pengirim' : 'Nomor Surat Resmi FIT'}
            </span>
            <div class="font-mono text-base font-black text-red-600 dark:text-red-400 break-all select-all flex items-center justify-between">
              <span>{detailLetter.full_number}</span>
              <button
                onclick={() => copyText(detailLetter.full_number)}
                class="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-white cursor-pointer"
              >
                {#if copied}
                  <Check class="w-4 h-4 text-emerald-500" />
                {:else}
                  <Copy class="w-4 h-4" />
                {/if}
              </button>
            </div>
          </div>

          <div class="space-y-2 text-xs text-slate-600 dark:text-slate-400">
            <div><strong class="text-slate-900 dark:text-slate-200">Perihal:</strong> {detailLetter.subject}</div>
            
            {#if detailLetter.letter_type === 'INCOMING'}
              <div><strong class="text-slate-900 dark:text-slate-200">Asal / Pengirim:</strong> {detailLetter.sender || '-'}</div>
              <div><strong class="text-slate-900 dark:text-slate-200">Ditujukan Kepada:</strong> {detailLetter.recipient || '-'}</div>
              <div><strong class="text-slate-900 dark:text-slate-200">Unit Disposisi:</strong> {detailLetter.unit_name}</div>
              <div><strong class="text-slate-900 dark:text-slate-200">Tanggal Surat:</strong> {formatDateIndo(detailLetter.letter_date)}</div>
              {#if detailLetter.received_date}
                <div><strong class="text-slate-900 dark:text-slate-200">Tanggal Diterima:</strong> {detailLetter.received_date}</div>
              {/if}
            {:else}
              {#if detailLetter.recipient}
                <div><strong class="text-slate-900 dark:text-slate-200">Tujuan / Penerima:</strong> {detailLetter.recipient}</div>
              {/if}
              <div><strong class="text-slate-900 dark:text-slate-200">Unit Pengaju:</strong> {detailLetter.unit_name}</div>
              <div><strong class="text-slate-900 dark:text-slate-200">Nama Pemohon:</strong> {detailLetter.applicant_name} ({detailLetter.applicant_contact || 'Tanpa Kontak'})</div>
              <div><strong class="text-slate-900 dark:text-slate-200">Tanggal Surat:</strong> {formatDateIndo(detailLetter.letter_date)}</div>
            {/if}

            <div><strong class="text-slate-900 dark:text-slate-200">Kategori:</strong> {detailLetter.category_name} ({detailLetter.classification_code})</div>
            {#if detailLetter.notes}
              <div><strong class="text-slate-900 dark:text-slate-200">Catatan:</strong> {detailLetter.notes}</div>
            {/if}
          </div>

          <div class="pt-2">
            <button
              onclick={() => detailLetter = null}
              class="w-full py-2 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 rounded-xl text-xs font-bold cursor-pointer hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
            >
              Tutup
            </button>
          </div>
        </div>
      </div>
    {/if}

    <!-- Edit Modal -->
    {#if editLetter}
      <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-xs animate-in fade-in duration-200">
        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 max-w-md w-full shadow-2xl space-y-4">
          <h3 class="text-base font-bold text-slate-900 dark:text-white">Edit Data Surat</h3>
          <p class="text-xs text-slate-500 font-mono">{editLetter.full_number}</p>

          <div class="space-y-3 text-xs">
            {#if editLetter.letter_type === 'INCOMING'}
              <div>
                <label for="edit-sender" class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Asal / Instansi Pengirim</label>
                <input id="edit-sender" type="text" bind:value={editForm.sender} class="w-full px-3 py-1.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs" />
              </div>
              <div>
                <label for="edit-recv-date" class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Tanggal Diterima</label>
                <input id="edit-recv-date" type="date" bind:value={editForm.receivedDate} class="w-full px-3 py-1.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs" />
              </div>
            {/if}
            <div>
              <label for="edit-subject" class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Perihal</label>
              <input id="edit-subject" type="text" bind:value={editForm.subject} class="w-full px-3 py-1.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs" />
            </div>
            <div>
              <label for="edit-recipient" class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Penerima / Tujuan</label>
              <input id="edit-recipient" type="text" bind:value={editForm.recipient} class="w-full px-3 py-1.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs" />
            </div>
            {#if editLetter.letter_type !== 'INCOMING'}
              <div>
                <label for="edit-applicant" class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Nama Pemohon</label>
                <input id="edit-applicant" type="text" bind:value={editForm.applicantName} class="w-full px-3 py-1.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs" />
              </div>
            {/if}
            <div>
              <label for="edit-notes" class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Catatan</label>
              <input id="edit-notes" type="text" bind:value={editForm.notes} class="w-full px-3 py-1.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs" />
            </div>
          </div>

          <div class="flex gap-2 pt-2">
            <button onclick={() => editLetter = null} class="flex-1 py-2 border rounded-xl text-xs font-semibold cursor-pointer">Batal</button>
            <button onclick={saveEdit} disabled={modalLoading} class="flex-1 py-2 bg-red-600 text-white rounded-xl text-xs font-bold cursor-pointer">
              {modalLoading ? 'Menyimpan...' : 'Simpan Perubahan'}
            </button>
          </div>
        </div>
      </div>
    {/if}

    <!-- Modal Input Surat Masuk -->
    {#if incomingModalOpen}
      <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/65 backdrop-blur-xs animate-in fade-in duration-200">
        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 sm:p-7 max-w-xl w-full shadow-2xl relative space-y-4 max-h-[90vh] overflow-y-auto">
          <!-- Close Button -->
          <button 
            onclick={() => incomingModalOpen = false}
            class="absolute right-4 top-4 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1.5 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 cursor-pointer transition-colors"
            aria-label="Tutup"
          >
            <X class="w-5 h-5" />
          </button>

          <!-- Header -->
          <div class="flex items-center gap-3">
            <div class="w-11 h-11 rounded-2xl bg-gradient-to-tr from-emerald-600 to-teal-500 text-white flex items-center justify-center shadow-md shadow-emerald-500/20 shrink-0">
              <Inbox class="w-6 h-6" />
            </div>
            <div>
              <h3 class="text-base font-bold text-slate-900 dark:text-white leading-tight">
                Registrasi Surat Masuk Resmi
              </h3>
              <p class="text-xs text-slate-500 dark:text-slate-400">
                Pencatatan surat masuk dari instansi luar ke Buku Agenda FIT
              </p>
            </div>
          </div>

          <!-- Sequence Info Banner -->
          <div class="p-3.5 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/60 flex items-center justify-between gap-3 text-xs">
            <div class="flex items-center gap-2">
              <span class="w-2 h-2 rounded-full bg-emerald-500 shrink-0"></span>
              <span class="text-emerald-900 dark:text-emerald-200 font-medium">
                Nomor Urut Agenda Berikutnya:
              </span>
            </div>
            <div class="font-mono text-base font-black text-emerald-700 dark:text-emerald-300">
              #{nextSeqPreview || '...'}
            </div>
          </div>

          <!-- Error Alert -->
          {#if incomingError}
            <div class="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 text-xs text-rose-700 dark:text-rose-300 flex items-start gap-2">
              <AlertCircle class="w-4 h-4 shrink-0 mt-0.5" />
              <span>{incomingError}</span>
            </div>
          {/if}

          <!-- Form Fields -->
          <div class="space-y-3.5 text-xs">
            <!-- Nomor Surat Asli dari Pengirim -->
            <div>
              <label for="inc-full-number" class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">
                Nomor Surat Asli dari Pengirim <span class="text-red-500">*</span>
              </label>
              <input
                id="inc-full-number"
                type="text"
                bind:value={incomingForm.fullNumber}
                placeholder="contoh: 045.2/B/TU-KEMENDIKBUD/2026 atau 123/EXT/TEL-U/2026"
                class="w-full px-3.5 py-2 font-mono bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/40"
              />
              <span class="text-[11px] text-slate-400 mt-1 block">
                Ketik nomor persis seperti yang tertera di surat resmi pengirim.
              </span>
            </div>

            <!-- Asal Instansi Pengirim -->
            <div>
              <label for="inc-sender" class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">
                Asal / Instansi Pengirim <span class="text-red-500">*</span>
              </label>
              <input
                id="inc-sender"
                type="text"
                bind:value={incomingForm.sender}
                placeholder="contoh: LLDIKTI Wilayah IV, PT Telkom Indonesia, Rektorat Tel-U"
                class="w-full px-3.5 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/40"
              />
            </div>

            <!-- Grid Tanggal Surat & Tanggal Diterima -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label for="inc-letter-date" class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">
                  Tanggal Surat Pengirim <span class="text-red-500">*</span>
                </label>
                <input
                  id="inc-letter-date"
                  type="date"
                  bind:value={incomingForm.letterDate}
                  class="w-full px-3.5 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/40"
                />
              </div>

              <div>
                <label for="inc-recv-date" class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">
                  Tanggal Diterima di Sekretariat <span class="text-red-500">*</span>
                </label>
                <input
                  id="inc-recv-date"
                  type="date"
                  bind:value={incomingForm.receivedDate}
                  class="w-full px-3.5 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/40"
                />
              </div>
            </div>

            <!-- Perihal -->
            <div>
              <label for="inc-subject" class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">
                Perihal Surat Masuk <span class="text-red-500">*</span>
              </label>
              <input
                id="inc-subject"
                type="text"
                bind:value={incomingForm.subject}
                placeholder="contoh: Undangan Rapat Koordinasi Penjaminan Mutu Nasional"
                class="w-full px-3.5 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/40"
              />
            </div>

            <!-- Ditujukan Kepada (Penerima) -->
            <div>
              <label for="inc-recipient" class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">
                Ditujukan Kepada
              </label>
              <input
                id="inc-recipient"
                type="text"
                bind:value={incomingForm.recipient}
                placeholder="contoh: Dekan Fakultas Ilmu Terapan / Ka. Bagian Akademik"
                class="w-full px-3.5 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/40"
              />
            </div>

            <!-- Grid Unit Disposisi & Kategori -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label for="inc-unit" class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">
                  Unit Tujuan Disposisi <span class="text-red-500">*</span>
                </label>
                <select
                  id="inc-unit"
                  bind:value={incomingForm.unitId}
                  class="w-full px-3.5 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/40"
                >
                  {#each units as u}
                    <option value={u.id}>{u.name}</option>
                  {/each}
                </select>
              </div>

              <div>
                <label for="inc-cat" class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">
                  Kategori Klasifikasi <span class="text-red-500">*</span>
                </label>
                <select
                  id="inc-cat"
                  bind:value={incomingForm.categoryId}
                  class="w-full px-3.5 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/40"
                >
                  {#each categories as c}
                    <option value={c.id}>[{c.code}] {c.name}</option>
                  {/each}
                </select>
              </div>
            </div>

            <!-- Catatan Disposisi -->
            <div>
              <label for="inc-notes" class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">
                Catatan / Instruksi Disposisi (Opsional)
              </label>
              <textarea
                id="inc-notes"
                bind:value={incomingForm.notes}
                rows={2}
                placeholder="Catatan tambahan disposisi pimpinan atau sekretariat..."
                class="w-full px-3.5 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/40"
              ></textarea>
            </div>
          </div>

          <!-- Buttons -->
          <div class="flex gap-3 pt-3 border-t border-slate-100 dark:border-slate-800">
            <button
              type="button"
              onclick={() => incomingModalOpen = false}
              disabled={incomingLoading}
              class="flex-1 py-2.5 px-4 rounded-xl border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 font-bold text-xs cursor-pointer disabled:opacity-50"
            >
              Batal
            </button>
            <button
              type="button"
              onclick={submitIncomingLetter}
              disabled={incomingLoading}
              class="flex-1 py-2.5 px-4 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-bold text-xs shadow-md shadow-emerald-500/20 cursor-pointer disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {#if incomingLoading}
                <RefreshCw class="w-3.5 h-3.5 animate-spin" />
                <span>Menyimpan...</span>
              {:else}
                <Check class="w-4 h-4" />
                <span>Simpan Surat Masuk</span>
              {/if}
            </button>
          </div>
        </div>
      </div>
    {/if}

    <!-- Delete Single Confirmation Modal -->
    {#if deleteLetterId}
      <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-xs">
        <div class="bg-white dark:bg-slate-900 rounded-2xl p-6 max-w-sm w-full shadow-2xl space-y-4 text-center">
          <Trash2 class="w-10 h-10 text-red-500 mx-auto" />
          <h3 class="text-base font-bold text-slate-900 dark:text-white">Konfirmasi Hapus Surat?</h3>
          <p class="text-xs text-slate-500">Tindakan ini akan menghapus riwayat surat dari buku agenda secara permanen.</p>
          <div class="flex gap-2 pt-2">
            <button onclick={() => deleteLetterId = null} class="flex-1 py-2 border rounded-xl text-xs font-semibold cursor-pointer">Batal</button>
            <button onclick={confirmDeleteSingle} disabled={modalLoading} class="flex-1 py-2 bg-red-600 text-white rounded-xl text-xs font-bold cursor-pointer">
              {modalLoading ? 'Menghapus...' : 'Ya, Hapus'}
            </button>
          </div>
        </div>
      </div>
    {/if}

    <!-- Bulk Delete Confirmation Modal -->
    {#if bulkDeleteOpen}
      <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-xs">
        <div class="bg-white dark:bg-slate-900 rounded-2xl p-6 max-w-sm w-full shadow-2xl space-y-4 text-center">
          <Trash2 class="w-10 h-10 text-red-500 mx-auto" />
          <h3 class="text-base font-bold text-slate-900 dark:text-white">Hapus {selectedIds.length} Surat Terpilih?</h3>
          <p class="text-xs text-slate-500">Tindakan ini tidak dapat dibatalkan.</p>
          <div class="flex gap-2 pt-2">
            <button onclick={() => bulkDeleteOpen = false} class="flex-1 py-2 border rounded-xl text-xs font-semibold cursor-pointer">Batal</button>
            <button onclick={confirmBulkDelete} disabled={modalLoading} class="flex-1 py-2 bg-red-600 text-white rounded-xl text-xs font-bold cursor-pointer">
              {modalLoading ? 'Menghapus...' : 'Ya, Hapus Semua'}
            </button>
          </div>
        </div>
      </div>
    {/if}
  </div>
{/if}
