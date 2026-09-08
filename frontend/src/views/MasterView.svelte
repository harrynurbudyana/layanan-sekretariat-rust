<script lang="ts">
  import { onMount } from 'svelte';
  import { 
    Database, 
    Building2, 
    Layers, 
    Plus, 
    Edit, 
    Trash2, 
    ShieldCheck, 
    Lock,
    X,
    AlertCircle,
    Check,
    Search
  } from 'lucide-svelte';
  import { admin } from '../lib/admin.svelte';

  let activeTab = $state<'units' | 'categories'>('units');
  let units = $state<any[]>([]);
  let categories = $state<any[]>([]);
  let loading = $state(true);

  // Category Search & Filter State
  let categorySearch = $state('');
  let categoryGroupFilter = $state('ALL');

  let filteredCategories = $derived.by(() => {
    return categories.filter(c => {
      const matchGroup = categoryGroupFilter === 'ALL' || c.group === categoryGroupFilter;
      if (!matchGroup) return false;
      if (!categorySearch.trim()) return true;
      const q = categorySearch.toLowerCase().trim();
      return (
        (c.name && c.name.toLowerCase().includes(q)) ||
        (c.code && c.code.toLowerCase().includes(q)) ||
        (c.group && c.group.toLowerCase().includes(q)) ||
        (c.classification_code && c.classification_code.toLowerCase().includes(q)) ||
        (c.description && c.description.toLowerCase().includes(q))
      );
    });
  });

  let availableGroups = $derived.by(() => {
    const s = new Set<string>();
    for (const c of categories) {
      if (c.group) s.add(c.group);
    }
    return Array.from(s).sort();
  });

  // Unit Modal State
  let unitModalOpen = $state(false);
  let editingUnit = $state<any | null>(null);
  let unitForm = $state({
    name: '',
    code: '',
    signee_code: 'IT-DEK',
    leader_name: '',
    category: 'PRODI'
  });

  // Category Modal State
  let categoryModalOpen = $state(false);
  let editingCategory = $state<any | null>(null);
  let categoryForm = $state({
    name: '',
    code: '',
    group: 'AKD',
    classification_code: '',
    description: ''
  });

  let deleteId = $state<string | null>(null);
  let deleteType = $state<'unit' | 'category'>('unit');
  let modalLoading = $state(false);
  let modalError = $state<string | null>(null);

  async function loadData() {
    loading = true;
    try {
      const [uRes, cRes] = await Promise.all([
        fetch('/api/units').then(r => r.json()),
        fetch('/api/categories').then(r => r.json())
      ]);
      units = uRes;
      categories = cRes;
    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    loadData();
  });

  function openAddUnit() {
    editingUnit = null;
    unitForm = { name: '', code: '', signee_code: 'IT-DEK', leader_name: '', category: 'PRODI' };
    modalError = null;
    unitModalOpen = true;
  }

  function openEditUnit(u: any) {
    editingUnit = u;
    unitForm = {
      name: u.name,
      code: u.code,
      signee_code: u.signee_code,
      leader_name: u.leader_name || '',
      category: u.category
    };
    modalError = null;
    unitModalOpen = true;
  }

  async function saveUnit() {
    if (!unitForm.name.trim() || !unitForm.code.trim()) {
      modalError = 'Nama dan Kode unit wajib diisi.';
      return;
    }
    modalLoading = true;
    modalError = null;

    try {
      const url = editingUnit ? `/api/units/${editingUnit.id}` : '/api/units';
      const method = editingUnit ? 'PUT' : 'POST';
      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(unitForm)
      });
      const data = await res.json();
      if (data.success) {
        unitModalOpen = false;
        loadData();
      } else {
        modalError = data.error || 'Gagal menyimpan unit.';
      }
    } catch (e) {
      modalError = 'Gagal menghubungi server.';
    } finally {
      modalLoading = false;
    }
  }

  function openAddCategory() {
    editingCategory = null;
    categoryForm = { name: '', code: '', group: 'AKD', classification_code: '', description: '' };
    modalError = null;
    categoryModalOpen = true;
  }

  function openEditCategory(c: any) {
    editingCategory = c;
    categoryForm = {
      name: c.name,
      code: c.code,
      group: c.group,
      classification_code: c.classification_code || '',
      description: c.description || ''
    };
    modalError = null;
    categoryModalOpen = true;
  }

  async function saveCategory() {
    if (!categoryForm.name.trim() || !categoryForm.code.trim()) {
      modalError = 'Nama dan Kode kategori wajib diisi.';
      return;
    }
    modalLoading = true;
    modalError = null;

    try {
      const url = editingCategory ? `/api/categories/${editingCategory.id}` : '/api/categories';
      const method = editingCategory ? 'PUT' : 'POST';
      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(categoryForm)
      });
      const data = await res.json();
      if (data.success) {
        categoryModalOpen = false;
        loadData();
      } else {
        modalError = data.error || 'Gagal menyimpan kategori.';
      }
    } catch (e) {
      modalError = 'Gagal menghubungi server.';
    } finally {
      modalLoading = false;
    }
  }

  async function confirmDelete() {
    if (!deleteId) return;
    modalLoading = true;
    modalError = null;
    try {
      const endpoint = deleteType === 'unit' ? `/api/units/${deleteId}` : `/api/categories/${deleteId}`;
      const res = await fetch(endpoint, { method: 'DELETE' });
      const data = await res.json();
      if (data.success) {
        deleteId = null;
        loadData();
      } else {
        modalError = data.error || 'Gagal menghapus data.';
      }
    } catch (e) {
      modalError = 'Gagal menghubungi server.';
    } finally {
      modalLoading = false;
    }
  }
</script>

<div class="space-y-6">
  <!-- Title Bar -->
  <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
    <div>
      <div class="flex items-center gap-2">
        <h1 class="text-xl font-black text-slate-900 dark:text-white tracking-tight">
          Master Data Sistem
        </h1>
        <span class="px-2.5 py-0.5 text-xs font-bold rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
          Konfigurasi Referensi
        </span>
      </div>
      <p class="text-xs text-slate-500 mt-1">
        Pengaturan data referensi Unit Kerja, Program Studi, dan Kategori Klasifikasi Surat.
      </p>
    </div>

    <!-- Tab Selector -->
    <div class="flex items-center gap-1 bg-slate-100 dark:bg-slate-800 p-1 rounded-xl">
      <button
        onclick={() => activeTab = 'units'}
        class="px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer {activeTab === 'units' ? 'bg-white dark:bg-slate-900 text-red-600 dark:text-red-400 shadow-xs' : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'}"
      >
        Unit & Prodi ({units.length})
      </button>
      <button
        onclick={() => activeTab = 'categories'}
        class="px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer {activeTab === 'categories' ? 'bg-white dark:bg-slate-900 text-red-600 dark:text-red-400 shadow-xs' : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'}"
      >
        Kategori Surat ({categories.length})
      </button>
    </div>
  </div>

  <!-- Admin Gate Banner -->
  {#if !admin.isAdmin}
    <div class="p-4 rounded-2xl bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800/60 flex items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <Lock class="w-5 h-5 text-amber-600 dark:text-amber-400 shrink-0" />
        <div class="text-xs text-amber-800 dark:text-amber-300">
          <strong>Mode Hanya-Lihat Aktif.</strong> Masuk sebagai admin sekretariat untuk menambah, mengedit, atau menghapus master data.
        </div>
      </div>
      <button
        onclick={() => admin.openLoginModal()}
        class="px-3.5 py-1.5 bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold rounded-xl shrink-0 cursor-pointer shadow-xs"
      >
        Masuk Admin
      </button>
    </div>
  {/if}

  <!-- TAB 1: UNITS -->
  {#if activeTab === 'units'}
    <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="text-base font-bold text-slate-900 dark:text-white">Daftar Unit Kerja & Program Studi</h2>
        {#if admin.isAdmin}
          <button
            onclick={openAddUnit}
            class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white rounded-xl text-xs font-bold shadow-xs cursor-pointer"
          >
            <Plus class="w-4 h-4" />
            <span>Tambah Unit</span>
          </button>
        {/if}
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {#each units as u}
          <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 flex flex-col justify-between">
            <div>
              <div class="flex items-center justify-between mb-2">
                <span class="font-mono text-xs font-bold text-red-600 dark:text-red-400 px-2 py-0.5 rounded bg-red-50 dark:bg-red-950/60 border border-red-200 dark:border-red-900">
                  {u.code}
                </span>
                <span class="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300">
                  {u.category}
                </span>
              </div>
              <h3 class="text-sm font-bold text-slate-900 dark:text-white mb-1">{u.name}</h3>
              <p class="text-xs text-slate-400">Kode Signee: <strong class="text-slate-700 dark:text-slate-300">{u.signee_code}</strong></p>
              {#if u.leader_name}
                <p class="text-xs text-slate-400 mt-0.5">Pimpinan: {u.leader_name}</p>
              {/if}
            </div>

            {#if admin.isAdmin}
              <div class="flex items-center justify-end gap-1 mt-4 pt-3 border-t border-slate-200 dark:border-slate-700">
                <button
                  onclick={() => openEditUnit(u)}
                  class="p-1 text-slate-400 hover:text-amber-500 cursor-pointer"
                  title="Edit Unit"
                >
                  <Edit class="w-4 h-4" />
                </button>
                <button
                  onclick={() => { deleteId = u.id; deleteType = 'unit'; }}
                  class="p-1 text-slate-400 hover:text-red-500 cursor-pointer"
                  title="Hapus Unit"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
            {/if}
          </div>
        {/each}
      </div>
    </div>

  <!-- TAB 2: CATEGORIES -->
  {:else if activeTab === 'categories'}
    <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-4">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 class="text-base font-bold text-slate-900 dark:text-white">Daftar Kategori & Klasifikasi Surat</h2>
          <p class="text-xs text-slate-500 dark:text-slate-400">
            Menampilkan <strong class="text-slate-700 dark:text-slate-200">{filteredCategories.length}</strong> dari {categories.length} kategori surat
          </p>
        </div>
        {#if admin.isAdmin}
          <button
            onclick={openAddCategory}
            class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white rounded-xl text-xs font-bold shadow-xs cursor-pointer self-start sm:self-auto"
          >
            <Plus class="w-4 h-4" />
            <span>Tambah Kategori</span>
          </button>
        {/if}
      </div>

      <!-- Search & Group Filter Bar -->
      <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5 pt-1">
        <div class="relative flex-1">
          <Search class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            bind:value={categorySearch}
            placeholder="Cari berdasarkan nama atau kode (misal: PRA, SEN, Akademik, Logistik)..."
            class="w-full pl-9 pr-3.5 py-2 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-medium text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500"
          />
        </div>
        <select
          bind:value={categoryGroupFilter}
          class="px-3 py-2 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-semibold text-slate-700 dark:text-slate-300 focus:outline-none focus:ring-2 focus:ring-red-500/20 cursor-pointer"
        >
          <option value="ALL">Semua Grup ({categories.length})</option>
          {#each availableGroups as grp}
            <option value={grp}>Grup {grp} ({categories.filter(c => c.group === grp).length})</option>
          {/each}
        </select>
      </div>

      {#if filteredCategories.length === 0}
        <div class="py-12 text-center text-slate-400 text-xs">
          Tidak ditemukan kategori yang sesuai dengan kata kunci atau filter yang dipilih.
        </div>
      {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {#each filteredCategories as c}
          <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 flex flex-col justify-between">
            <div>
              <div class="flex items-center justify-between mb-2">
                <span class="font-mono text-xs font-bold text-amber-600 dark:text-amber-400 px-2 py-0.5 rounded bg-amber-50 dark:bg-amber-950/60 border border-amber-200 dark:border-amber-900">
                  {c.code}
                </span>
                <span class="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300">
                  {c.group}
                </span>
              </div>
              <h3 class="text-sm font-bold text-slate-900 dark:text-white mb-1">{c.name}</h3>
              {#if c.classification_code}
                <p class="text-xs text-slate-400">Klasifikasi: <strong class="text-slate-700 dark:text-slate-300">{c.classification_code}</strong></p>
              {/if}
              {#if c.description}
                <p class="text-xs text-slate-500 mt-1 line-clamp-2">{c.description}</p>
              {/if}
            </div>

            {#if admin.isAdmin}
              <div class="flex items-center justify-end gap-1 mt-4 pt-3 border-t border-slate-200 dark:border-slate-700">
                <button
                  onclick={() => openEditCategory(c)}
                  class="p-1 text-slate-400 hover:text-amber-500 cursor-pointer"
                  title="Edit Kategori"
                >
                  <Edit class="w-4 h-4" />
                </button>
                <button
                  onclick={() => { deleteId = c.id; deleteType = 'category'; }}
                  class="p-1 text-slate-400 hover:text-red-500 cursor-pointer"
                  title="Hapus Kategori"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
            {/if}
          </div>
        {/each}
      </div>
      {/if}
    </div>
  {/if}

  <!-- Unit Modal -->
  {#if unitModalOpen}
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-xs">
      <div class="bg-white dark:bg-slate-900 rounded-2xl p-6 max-w-md w-full shadow-2xl space-y-4">
        <h3 class="text-base font-bold text-slate-900 dark:text-white">
          {editingUnit ? 'Edit Unit Kerja' : 'Tambah Unit Baru'}
        </h3>

        {#if modalError}
          <div class="p-2.5 rounded-lg bg-red-50 text-red-600 text-xs">{modalError}</div>
        {/if}

        <div class="space-y-3 text-xs">
          <div>
            <label for="unit-name" class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Nama Unit / Prodi *</label>
            <input id="unit-name" type="text" bind:value={unitForm.name} placeholder="Misal: S1 Rekayasa Perangkat Lunak" class="w-full px-3 py-1.5 bg-slate-50 dark:bg-slate-800 border rounded-lg text-xs" />
          </div>
          <div class="grid grid-cols-2 gap-2">
            <div>
              <label for="unit-code" class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Kode Unit *</label>
              <input id="unit-code" type="text" bind:value={unitForm.code} placeholder="RPL" class="w-full px-3 py-1.5 bg-slate-50 dark:bg-slate-800 border rounded-lg text-xs uppercase" />
            </div>
            <div>
              <label for="unit-signee" class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Kode Signee *</label>
              <input id="unit-signee" type="text" bind:value={unitForm.signee_code} placeholder="IT-D3-RPL" class="w-full px-3 py-1.5 bg-slate-50 dark:bg-slate-800 border rounded-lg text-xs uppercase" />
            </div>
          </div>
          <div>
            <label for="unit-leader" class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Nama Pimpinan / Ka. Prodi</label>
            <input id="unit-leader" type="text" bind:value={unitForm.leader_name} placeholder="Nama dosen pimpinan..." class="w-full px-3 py-1.5 bg-slate-50 dark:bg-slate-800 border rounded-lg text-xs" />
          </div>
          <div>
            <label for="unit-category" class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Kategori</label>
            <select id="unit-category" bind:value={unitForm.category} class="w-full px-3 py-1.5 bg-slate-50 dark:bg-slate-800 border rounded-lg text-xs">
              <option value="PRODI">PRODI</option>
              <option value="DEKANAT">DEKANAT</option>
              <option value="BAGIAN">BAGIAN</option>
              <option value="LAB">LAB</option>
              <option value="KK">KELOMPOK KEAHLIAN</option>
            </select>
          </div>
        </div>

        <div class="flex gap-2 pt-2">
          <button onclick={() => unitModalOpen = false} class="flex-1 py-2 border rounded-xl text-xs font-semibold cursor-pointer">Batal</button>
          <button onclick={saveUnit} disabled={modalLoading} class="flex-1 py-2 bg-red-600 text-white rounded-xl text-xs font-bold cursor-pointer">
            {modalLoading ? 'Menyimpan...' : 'Simpan Unit'}
          </button>
        </div>
      </div>
    </div>
  {/if}

  <!-- Category Modal -->
  {#if categoryModalOpen}
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-xs">
      <div class="bg-white dark:bg-slate-900 rounded-2xl p-6 max-w-md w-full shadow-2xl space-y-4">
        <h3 class="text-base font-bold text-slate-900 dark:text-white">
          {editingCategory ? 'Edit Kategori Surat' : 'Tambah Kategori Baru'}
        </h3>

        {#if modalError}
          <div class="p-2.5 rounded-lg bg-red-50 text-red-600 text-xs">{modalError}</div>
        {/if}

        <div class="space-y-3 text-xs">
          <div>
            <label for="cat-name" class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Nama Kategori *</label>
            <input id="cat-name" type="text" bind:value={categoryForm.name} placeholder="Misal: Surat Keterangan Aktif Kuliah" class="w-full px-3 py-1.5 bg-slate-50 dark:bg-slate-800 border rounded-lg text-xs" />
          </div>
          <div class="grid grid-cols-2 gap-2">
            <div>
              <label for="cat-code" class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Kode Singkat *</label>
              <input id="cat-code" type="text" bind:value={categoryForm.code} placeholder="AKD01" class="w-full px-3 py-1.5 bg-slate-50 dark:bg-slate-800 border rounded-lg text-xs uppercase" />
            </div>
            <div>
              <label for="cat-group" class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Grup / Bidang</label>
              <input id="cat-group" type="text" bind:value={categoryForm.group} placeholder="AKD, SKR, PRA..." class="w-full px-3 py-1.5 bg-slate-50 dark:bg-slate-800 border rounded-lg text-xs uppercase" />
            </div>
          </div>
          <div>
            <label for="cat-desc" class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Deskripsi / Peruntukan</label>
            <textarea id="cat-desc" rows="2" bind:value={categoryForm.description} class="w-full px-3 py-1.5 bg-slate-50 dark:bg-slate-800 border rounded-lg text-xs"></textarea>
          </div>
        </div>

        <div class="flex gap-2 pt-2">
          <button onclick={() => categoryModalOpen = false} class="flex-1 py-2 border rounded-xl text-xs font-semibold cursor-pointer">Batal</button>
          <button onclick={saveCategory} disabled={modalLoading} class="flex-1 py-2 bg-red-600 text-white rounded-xl text-xs font-bold cursor-pointer">
            {modalLoading ? 'Menyimpan...' : 'Simpan Kategori'}
          </button>
        </div>
      </div>
    </div>
  {/if}

  <!-- Delete Modal -->
  {#if deleteId}
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-xs">
      <div class="bg-white dark:bg-slate-900 rounded-2xl p-6 max-w-sm w-full shadow-2xl space-y-4 text-center">
        <Trash2 class="w-10 h-10 text-red-500 mx-auto" />
        <h3 class="text-base font-bold text-slate-900 dark:text-white">Konfirmasi Hapus Data?</h3>
        {#if modalError}
          <div class="p-2.5 rounded-lg bg-red-50 text-red-600 text-xs text-left">{modalError}</div>
        {/if}
        <p class="text-xs text-slate-500">Data master yang masih digunakan oleh surat di buku agenda tidak dapat dihapus.</p>
        <div class="flex gap-2 pt-2">
          <button onclick={() => { deleteId = null; modalError = null; }} class="flex-1 py-2 border rounded-xl text-xs font-semibold cursor-pointer">Batal</button>
          <button onclick={confirmDelete} disabled={modalLoading} class="flex-1 py-2 bg-red-600 text-white rounded-xl text-xs font-bold cursor-pointer">
            {modalLoading ? 'Menghapus...' : 'Hapus'}
          </button>
        </div>
      </div>
    </div>
  {/if}
</div>
