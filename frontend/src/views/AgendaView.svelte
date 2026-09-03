<script lang="ts">
  import { onMount } from 'svelte';
  import { 
    BookOpenCheck, 
    Search, 
    Download, 
    Trash2, 
    Edit, 
    Eye, 
    Filter, 
    RefreshCw, 
    Check, 
    Copy, 
    AlertCircle, 
    ChevronLeft, 
    ChevronRight,
    X,
    FileSpreadsheet
  } from 'lucide-svelte';
  import { admin } from '../lib/admin.svelte';
  import { formatDateIndo, getCategoryBadgeClass } from '../lib/utils';

  let letters = $state<any[]>([]);
  let total = $state(0);
  let units = $state<any[]>([]);
  let categories = $state<any[]>([]);
  let loading = $state(true);

  // Filters
  let search = $state('');
  let selectedYear = $state<number | null>(new Date().getFullYear());
  let selectedMonth = $state<number | null>(null);
  let selectedUnit = $state('ALL');
  let selectedCategory = $state('ALL');
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
    notes: ''
  });
  let modalLoading = $state(false);
  let copied = $state(false);

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

      const res = await fetch(`/api/letters?${params.toString()}`);
      const data = await res.json();
      letters = data.letters;
      total = data.total;
    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    fetchMetadata();
    fetchLetters();
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
      selectedIds = selectedIds.filter(i => i !== id);
    } else {
      selectedIds = [...selectedIds, id];
    }
  }

  function openEdit(letter: any) {
    editLetter = letter;
    editForm = {
      subject: letter.subject,
      recipient: letter.recipient || '',
      applicantName: letter.applicant_name,
      applicantContact: letter.applicant_contact || '',
      status: letter.status || 'ISSUED',
      notes: letter.notes || ''
    };
  }

  async function saveEdit() {
    if (!editLetter) return;
    modalLoading = true;
    try {
      const res = await fetch(`/api/letters/${editLetter.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subject: editForm.subject,
          recipient: editForm.recipient || null,
          applicant_name: editForm.applicantName,
          applicant_contact: editForm.applicantContact || null,
          status: editForm.status,
          notes: editForm.notes || null
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
      const res = await fetch(`/api/letters/${deleteLetterId}`, { method: 'DELETE' });
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
        headers: { 'Content-Type': 'application/json' },
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
    const headers = ["No Urut", "Nomor Surat", "Perihal", "Kategori", "Pemohon", "Unit", "Tanggal", "Status"];
    const rows = letters.map(l => [
      l.sequence_number,
      `"${l.full_number}"`,
      `"${(l.subject || '').replace(/"/g, '""')}"`,
      `"${l.category_name || ''}"`,
      `"${l.applicant_name || ''}"`,
      `"${l.unit_name || ''}"`,
      l.letter_date,
      l.status
    ]);
    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `buku_agenda_fit_${selectedYear || 'all'}.csv`);
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

<div class="space-y-6">
  <!-- Title & Action Bar -->
  <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
    <div>
      <div class="flex items-center gap-2">
        <h1 class="text-xl font-black text-slate-900 dark:text-white tracking-tight">
          Buku Agenda Surat Keluar
        </h1>
        <span class="px-2.5 py-0.5 text-xs font-bold rounded-full bg-red-100 dark:bg-red-950/60 text-red-600 dark:text-red-400">
          {total} Dokumen
        </span>
      </div>
      <p class="text-xs text-slate-500 mt-1">
        Daftar seluruh nomor surat resmi Fakultas Ilmu Terapan yang terbit secara resmi.
      </p>
    </div>

    <div class="flex items-center gap-2">
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
    </div>
  </div>

  <!-- Filter Toolbar -->
  <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 shadow-sm space-y-3">
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
      <!-- Search Input -->
      <div class="lg:col-span-2 relative">
        <Search class="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
        <input
          type="text"
          bind:value={search}
          oninput={handleFilterChange}
          placeholder="Cari nomor surat, perihal, pemohon..."
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
              <th class="p-3.5">Nomor Surat Lengkap</th>
              <th class="p-3.5">Perihal Surat</th>
              <th class="p-3.5">Pemohon & Unit</th>
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
                <td class="p-3.5">
                  <div class="font-mono font-bold text-slate-900 dark:text-red-400">{letter.full_number}</div>
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
                  <div class="font-semibold text-slate-800 dark:text-slate-200">{letter.applicant_name}</div>
                  <div class="text-[11px] text-slate-400">{letter.unit_name || '-'}</div>
                </td>
                <td class="p-3.5 text-slate-500 whitespace-nowrap">
                  {formatDateIndo(letter.letter_date)}
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
          <h3 class="text-base font-bold text-slate-900 dark:text-white">Detail Nomor Surat</h3>
        </div>

        <div class="bg-slate-50 dark:bg-slate-800/60 p-4 rounded-2xl border border-slate-200 dark:border-slate-700 space-y-2">
          <span class="text-[10px] uppercase font-bold text-slate-400">Nomor Registrasi Resmi</span>
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
          {#if detailLetter.recipient}
            <div><strong class="text-slate-900 dark:text-slate-200">Penerima:</strong> {detailLetter.recipient}</div>
          {/if}
          <div><strong class="text-slate-900 dark:text-slate-200">Unit Pengaju:</strong> {detailLetter.unit_name}</div>
          <div><strong class="text-slate-900 dark:text-slate-200">Nama Pemohon:</strong> {detailLetter.applicant_name} ({detailLetter.applicant_contact || 'Tanpa Kontak'})</div>
          <div><strong class="text-slate-900 dark:text-slate-200">Tanggal Surat:</strong> {formatDateIndo(detailLetter.letter_date)}</div>
          <div><strong class="text-slate-900 dark:text-slate-200">Kategori:</strong> {detailLetter.category_name} ({detailLetter.classification_code})</div>
          {#if detailLetter.notes}
            <div><strong class="text-slate-900 dark:text-slate-200">Catatan:</strong> {detailLetter.notes}</div>
          {/if}
        </div>

        <div class="pt-2">
          <button
            onclick={() => detailLetter = null}
            class="w-full py-2 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 rounded-xl text-xs font-bold cursor-pointer"
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
          <div>
            <label class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Perihal</label>
            <input type="text" bind:value={editForm.subject} class="w-full px-3 py-1.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs" />
          </div>
          <div>
            <label class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Penerima</label>
            <input type="text" bind:value={editForm.recipient} class="w-full px-3 py-1.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs" />
          </div>
          <div>
            <label class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Nama Pemohon</label>
            <input type="text" bind:value={editForm.applicantName} class="w-full px-3 py-1.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs" />
          </div>
          <div>
            <label class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Catatan</label>
            <input type="text" bind:value={editForm.notes} class="w-full px-3 py-1.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs" />
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
