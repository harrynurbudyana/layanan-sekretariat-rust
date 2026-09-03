<script lang="ts">
  import { onMount } from 'svelte';
  import { 
    FilePlus2, 
    Sparkles, 
    Check, 
    Copy, 
    AlertCircle, 
    ArrowRight, 
    Calendar, 
    Building2, 
    Layers, 
    User, 
    Phone, 
    FileText, 
    Info, 
    Lock,
    Clock
  } from 'lucide-svelte';
  import { admin } from '../lib/admin.svelte';
  import { router } from '../lib/router.svelte';
  import { getRomanMonth } from '../lib/utils';

  let units = $state<any[]>([]);
  let categories = $state<any[]>([]);
  let loadingMeta = $state(true);

  // Form State
  let isManual = $state(false);
  let manualSequence = $state<number | null>(null);
  let manualFullNumber = $state('');
  let unitId = $state('');
  let categoryId = $state('');
  let subject = $state('');
  let recipient = $state('');
  let applicantName = $state('');
  let applicantContact = $state('');
  let letterDate = $state(new Date().toISOString().slice(0, 10));
  let notes = $state('');

  // UI State
  let submitting = $state(false);
  let errorMsg = $state<string | null>(null);
  let successResult = $state<any | null>(null);
  let copied = $state(false);

  async function loadMetadata() {
    loadingMeta = true;
    try {
      const [uRes, cRes] = await Promise.all([
        fetch('/api/units').then(r => r.json()),
        fetch('/api/categories').then(r => r.json())
      ]);
      units = uRes;
      categories = cRes;
      if (units.length > 0) unitId = units[0].id;
      if (categories.length > 0) categoryId = categories[0].id;
    } catch (e) {
      console.error(e);
    } finally {
      loadingMeta = false;
    }
  }

  onMount(() => {
    loadMetadata();
  });

  // Selected details
  let selectedUnit = $derived(units.find(u => u.id === unitId));
  let selectedCategory = $derived(categories.find(c => c.id === categoryId));

  let previewNumber = $derived.by(() => {
    const year = letterDate ? new Date(letterDate).getFullYear() : new Date().getFullYear();
    const classCode = selectedCategory?.code || 'AKD01';
    const signee = selectedUnit?.signee_code || 'IT-DEK';

    if (isManual) {
      if (manualFullNumber.trim()) return manualFullNumber.trim();
      const seq = manualSequence || '...';
      return `${seq}/${classCode}/${signee}/${year}`;
    }
    return `[Auto-Increment]/${classCode}/${signee}/${year}`;
  });

  async function handleSubmit(e: Event) {
    e.preventDefault();
    if (!unitId || !categoryId || !subject.trim() || !applicantName.trim()) {
      errorMsg = 'Harap lengkapi semua field wajib bertanda bintang (*).';
      return;
    }

    submitting = true;
    errorMsg = null;

    try {
      const res = await fetch('/api/letters/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          is_manual: isManual,
          manual_sequence_number: isManual ? manualSequence : null,
          manual_full_number: isManual && manualFullNumber.trim() ? manualFullNumber.trim() : null,
          unit_id: unitId,
          category_id: categoryId,
          classification_code: selectedCategory?.code,
          signee_code: selectedUnit?.signee_code,
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
      } else {
        errorMsg = data.error || 'Gagal membuat nomor surat.';
      }
    } catch (e: any) {
      errorMsg = 'Gagal menghubungi server Rust.';
    } finally {
      submitting = false;
    }
  }

  function copyToClipboard(text: string) {
    navigator.clipboard.writeText(text);
    copied = true;
    setTimeout(() => copied = false, 2500);
  }

  function resetForm() {
    successResult = null;
    subject = '';
    recipient = '';
    applicantName = '';
    applicantContact = '';
    notes = '';
    manualFullNumber = '';
    manualSequence = null;
    errorMsg = null;
  }
</script>

<div class="max-w-4xl mx-auto space-y-6">
  <!-- Header -->
  <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <div class="flex items-center gap-2">
          <h1 class="text-xl font-black text-slate-900 dark:text-white tracking-tight">
            Generator Nomor Surat Keluar
          </h1>
          <span class="px-2 py-0.5 text-[10px] font-bold uppercase rounded-full bg-red-100 dark:bg-red-950/60 text-red-600 dark:text-red-400 border border-red-200 dark:border-red-800">
            FIT Otomasi
          </span>
        </div>
        <p class="text-xs text-slate-500 mt-1">
          Dapatkan nomor surat dinas resmi secara instan dengan penomoran sequence terpusat.
        </p>
      </div>

      <!-- Mode Toggle -->
      <div class="flex items-center gap-2 bg-slate-100 dark:bg-slate-800 p-1 rounded-xl">
        <button
          type="button"
          onclick={() => isManual = false}
          class="px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer {!isManual ? 'bg-white dark:bg-slate-900 text-red-600 dark:text-red-400 shadow-xs' : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'}"
        >
          Otomatis
        </button>
        <button
          type="button"
          onclick={() => {
            if (!admin.isAdmin) {
              admin.openLoginModal();
            } else {
              isManual = true;
            }
          }}
          class="px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1 transition-all cursor-pointer {isManual ? 'bg-white dark:bg-slate-900 text-red-600 dark:text-red-400 shadow-xs' : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'}"
        >
          {#if !admin.isAdmin}
            <Lock class="w-3 h-3 text-slate-400" />
          {/if}
          <span>Manual (Admin)</span>
        </button>
      </div>
    </div>
  </div>

  <!-- Form & Preview Grid -->
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <!-- Form (2 cols) -->
    <div class="lg:col-span-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm">
      {#if errorMsg}
        <div class="mb-5 p-3.5 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 text-xs text-red-600 dark:text-red-300 flex items-center gap-2">
          <AlertCircle class="w-4 h-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      {/if}

      <form onsubmit={handleSubmit} class="space-y-4">
        {#if isManual}
          <div class="p-3.5 rounded-xl bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 text-xs text-amber-800 dark:text-amber-300 space-y-2">
            <div class="font-bold flex items-center gap-1.5">
              <Info class="w-4 h-4" />
              <span>Mode Penomoran Manual Aktif</span>
            </div>
            <p>Gunakan mode ini hanya untuk mencatat surat fisik masa lampau atau nomor khusus yang telah disetujui pimpinan.</p>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
              <div>
                <label for="manual-seq-input" class="block text-[11px] font-semibold text-amber-900 dark:text-amber-200 mb-1">Nomor Urut Custom</label>
                <input
                  id="manual-seq-input"
                  type="number"
                  bind:value={manualSequence}
                  placeholder="Misal: 1540"
                  class="w-full px-3 py-1.5 bg-white dark:bg-slate-800 border border-amber-300 dark:border-amber-700 rounded-lg text-xs"
                />
              </div>
              <div>
                <label for="manual-full-input" class="block text-[11px] font-semibold text-amber-900 dark:text-amber-200 mb-1">Nomor Lengkap Custom (Opsional)</label>
                <input
                  id="manual-full-input"
                  type="text"
                  bind:value={manualFullNumber}
                  placeholder="Format lengkap..."
                  class="w-full px-3 py-1.5 bg-white dark:bg-slate-800 border border-amber-300 dark:border-amber-700 rounded-lg text-xs"
                />
              </div>
            </div>
          </div>
        {/if}

        <!-- Unit & Category -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label for="unit-select" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
              Unit / Prodi Pengaju *
            </label>
            <select
              id="unit-select"
              bind:value={unitId}
              class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-red-500/30"
            >
              {#each units as u}
                <option value={u.id}>{u.name} ({u.code})</option>
              {/each}
            </select>
          </div>

          <div>
            <label for="category-select" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
              Kategori / Perihal Surat *
            </label>
            <select
              id="category-select"
              bind:value={categoryId}
              class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-red-500/30"
            >
              {#each categories as c}
                <option value={c.id}>[{c.code}] {c.name}</option>
              {/each}
            </select>
          </div>
        </div>

        <!-- Subject -->
        <div>
          <label for="subject-input" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
            Perihal / Isi Ringkas Surat *
          </label>
          <textarea
            id="subject-input"
            rows="2"
            bind:value={subject}
            placeholder="Contoh: Permohonan Izin Kunjungan Industri Mahasiswa D3 Sistem Informasi"
            class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-red-500/30"
          ></textarea>
        </div>

        <!-- Recipient -->
        <div>
          <label for="recipient-input" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
            Tujuan / Penerima Surat (Opsional)
          </label>
          <input
            id="recipient-input"
            type="text"
            bind:value={recipient}
            placeholder="Contoh: Direktur PT Telkom Indonesia"
            class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-red-500/30"
          />
        </div>

        <!-- Applicant Name & Contact -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label for="applicant-name-input" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
              Nama Pemohon / PIC *
            </label>
            <input
              id="applicant-name-input"
              type="text"
              bind:value={applicantName}
              placeholder="Nama staf atau dosen pengaju..."
              class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-red-500/30"
            />
          </div>
          <div>
            <label for="applicant-contact-input" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
              No WhatsApp / Kontak PIC
            </label>
            <input
              id="applicant-contact-input"
              type="text"
              bind:value={applicantContact}
              placeholder="081234567890"
              class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-red-500/30"
            />
          </div>
        </div>

        <!-- Date & Notes -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label for="letter-date-input" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
              Tanggal Surat *
            </label>
            <input
              id="letter-date-input"
              type="date"
              bind:value={letterDate}
              class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-red-500/30"
            />
          </div>
          <div>
            <label for="notes-input" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
              Catatan Internal (Opsional)
            </label>
            <input
              id="notes-input"
              type="text"
              bind:value={notes}
              placeholder="Keterangan tambahan jika ada..."
              class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-red-500/30"
            />
          </div>
        </div>

        <div class="pt-4">
          <button
            type="submit"
            disabled={submitting}
            class="w-full py-3 px-4 bg-red-600 hover:bg-red-700 disabled:opacity-50 text-white font-bold text-sm rounded-xl shadow-md shadow-red-600/30 transition-all active:scale-[0.99] flex items-center justify-center gap-2 cursor-pointer"
          >
            <Sparkles class="w-4 h-4 {submitting ? 'animate-spin' : ''}" />
            <span>{submitting ? 'Memproses Nomor Surat...' : 'Generate & Catat ke Buku Agenda'}</span>
          </button>
        </div>
      </form>
    </div>

    <!-- Live Preview Sidebar (1 col) -->
    <div class="space-y-4">
      <div class="bg-gradient-to-br from-slate-900 to-slate-800 text-white rounded-2xl p-5 border border-slate-700 shadow-md space-y-4">
        <div class="flex items-center gap-2 text-red-400">
          <Sparkles class="w-4 h-4" />
          <span class="text-xs font-bold uppercase tracking-wider">Live Preview Format</span>
        </div>

        <div>
          <span class="text-[10px] text-slate-400 uppercase font-semibold">Estimasi Nomor Surat:</span>
          <div class="font-mono text-sm font-bold text-amber-300 bg-slate-950/60 p-3 rounded-xl border border-slate-700/60 mt-1 break-all select-all">
            {previewNumber}
          </div>
        </div>

        <div class="space-y-2 text-xs text-slate-300 border-t border-slate-700 pt-3">
          <div class="flex justify-between">
            <span class="text-slate-400">Penandatangan:</span>
            <span class="font-semibold text-white">{selectedUnit?.signee_code || 'IT-DEK'}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-400">Kode Klasifikasi:</span>
            <span class="font-semibold text-white">{selectedCategory?.code || '-'}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-400">Pimpinan Unit:</span>
            <span class="text-slate-200">{selectedUnit?.leader_name || '-'}</span>
          </div>
        </div>
      </div>

      <div class="bg-slate-50 dark:bg-slate-800/40 rounded-2xl p-4 border border-slate-200 dark:border-slate-800 text-xs text-slate-500 dark:text-slate-400 space-y-2">
        <div class="font-semibold text-slate-700 dark:text-slate-200 flex items-center gap-1.5">
          <Info class="w-3.5 h-3.5 text-blue-500" />
          <span>Informasi Alur</span>
        </div>
        <p class="leading-relaxed">
          Setelah nomor surat digenerate, nomor akan otomatis tercatat di <strong>Buku Agenda Digital</strong> dan urutan sequence terkunci secara atomic pada database fakultas.
        </p>
      </div>
    </div>
  </div>

  <!-- Success Modal -->
  {#if successResult}
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-xs animate-in fade-in duration-200">
      <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 sm:p-8 max-w-lg w-full shadow-2xl space-y-5 text-center">
        <div class="w-16 h-16 rounded-2xl bg-emerald-100 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 mx-auto flex items-center justify-center">
          <Check class="w-8 h-8" />
        </div>

        <div>
          <span class="text-xs font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">Berhasil Diterbitkan</span>
          <h2 class="text-xl font-black text-slate-900 dark:text-white mt-1">Nomor Surat Resmi Anda</h2>
          <p class="text-xs text-slate-500 mt-1">Telah tersimpan di Buku Agenda Sekretariat FIT</p>
        </div>

        <div class="bg-slate-100 dark:bg-slate-800/80 p-4 rounded-2xl border border-slate-200 dark:border-slate-700 relative group">
          <div class="font-mono text-base sm:text-lg font-black text-red-600 dark:text-red-400 break-all select-all">
            {successResult.fullNumber}
          </div>
          <button
            onclick={() => copyToClipboard(successResult.fullNumber)}
            class="mt-3 inline-flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-white dark:bg-slate-700 hover:bg-slate-50 dark:hover:bg-slate-600 text-slate-700 dark:text-white text-xs font-semibold border border-slate-200 dark:border-slate-600 shadow-xs cursor-pointer"
          >
            {#if copied}
              <Check class="w-3.5 h-3.5 text-emerald-500" />
              <span class="text-emerald-600 dark:text-emerald-400">Tersalin!</span>
            {:else}
              <Copy class="w-3.5 h-3.5" />
              <span>Salin Nomor Surat</span>
            {/if}
          </button>
        </div>

        <div class="text-left text-xs bg-slate-50 dark:bg-slate-800/40 p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 space-y-1.5 text-slate-600 dark:text-slate-400">
          <div><strong>Perihal:</strong> {successResult.subject}</div>
          <div><strong>Pemohon:</strong> {successResult.applicantName} ({successResult.unitName})</div>
          <div><strong>Tanggal:</strong> {successResult.letterDate}</div>
        </div>

        <div class="flex flex-col sm:flex-row gap-2 pt-2">
          <button
            onclick={resetForm}
            class="flex-1 py-2.5 px-4 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 cursor-pointer"
          >
            Buat Nomor Lain
          </button>
          <button
            onclick={() => router.navigate('/agenda')}
            class="flex-1 py-2.5 px-4 bg-red-600 hover:bg-red-700 text-white rounded-xl text-xs font-bold shadow-md shadow-red-600/25 flex items-center justify-center gap-1.5 cursor-pointer"
          >
            <span>Buka Buku Agenda</span>
            <ArrowRight class="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  {/if}
</div>
