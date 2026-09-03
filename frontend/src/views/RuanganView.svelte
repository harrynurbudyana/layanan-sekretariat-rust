<script lang="ts">
  import { onMount } from 'svelte';
  import { 
    CalendarDays, 
    DoorOpen, 
    Clock, 
    User, 
    Phone, 
    AlertCircle, 
    CheckCircle2, 
    XCircle, 
    HelpCircle, 
    Plus, 
    Calendar as CalendarIcon, 
    Check, 
    X,
    Filter,
    Layers,
    ShieldCheck
  } from 'lucide-svelte';
  import { admin } from '../lib/admin.svelte';
  import { formatDateIndo } from '../lib/utils';

  let rooms = $state<any[]>([]);
  let bookings = $state<any[]>([]);
  let loading = $state(true);

  // Active Tab: 'form' | 'schedule' | 'list'
  let activeTab = $state<'form' | 'schedule' | 'list'>('schedule');

  // Form State
  let formRoomId = $state('');
  let formDateStr = $state(new Date().toISOString().slice(0, 10));
  let formStartTime = $state('09:00');
  let formEndTime = $state('11:00');
  let formPurpose = $state('');
  let formUnitName = $state('');
  let formApplicantName = $state('');
  let formApplicantPhone = $state('');
  let formParticipantCount = $state(15);
  let formFacilityNotes = $state('');

  // Conflict Check
  let checkingAvailability = $state(false);
  let conflictError = $state<string | null>(null);
  let availabilityChecked = $state(false);

  // Submission State
  let submitting = $state(false);
  let submitError = $state<string | null>(null);
  let submitSuccess = $state<any | null>(null);

  // Schedule Timeline Filter
  let timelineDate = $state(new Date().toISOString().slice(0, 10));

  // List Filter
  let statusFilter = $state('ALL');

  async function loadData() {
    loading = true;
    try {
      const [rRes, bRes] = await Promise.all([
        fetch('/api/rooms').then(r => r.json()),
        fetch('/api/rooms/bookings').then(r => r.json())
      ]);
      rooms = rRes;
      bookings = bRes;
      if (rooms.length > 0 && !formRoomId) {
        formRoomId = rooms[0].id;
      }
    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    loadData();
  });

  async function checkConflict() {
    if (!formRoomId || !formDateStr || !formStartTime || !formEndTime) return;
    checkingAvailability = true;
    conflictError = null;
    availabilityChecked = false;

    try {
      const res = await fetch('/api/rooms/check-availability', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          room_id: formRoomId,
          date_str: formDateStr,
          start_time: formStartTime,
          end_time: formEndTime
        })
      });
      const data = await res.json();
      availabilityChecked = true;
      if (!data.available) {
        conflictError = data.error || 'Jadwal ruangan bentrok.';
      }
    } catch (e) {
      conflictError = 'Gagal memeriksa bentrok jadwal.';
    } finally {
      checkingAvailability = false;
    }
  }

  async function handleBookingSubmit(e: Event) {
    e.preventDefault();
    if (!formPurpose.trim() || !formUnitName.trim() || !formApplicantName.trim()) {
      submitError = 'Harap isi semua field bertanda bintang (*).';
      return;
    }

    submitting = true;
    submitError = null;

    try {
      const res = await fetch('/api/rooms/bookings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          room_id: formRoomId,
          date_str: formDateStr,
          start_time: formStartTime,
          end_time: formEndTime,
          purpose: formPurpose.trim(),
          unit_name: formUnitName.trim(),
          applicant_name: formApplicantName.trim(),
          applicant_phone: formApplicantPhone.trim(),
          participant_count: formParticipantCount,
          facility_notes: formFacilityNotes.trim() || null
        })
      });

      const data = await res.json();
      if (data.success) {
        submitSuccess = data.booking;
        loadData();
      } else {
        submitError = data.error || 'Gagal mengajukan peminjaman ruangan.';
      }
    } catch (e) {
      submitError = 'Gagal menghubungi server.';
    } finally {
      submitting = false;
    }
  }

  async function updateStatus(bookingId: string, status: string) {
    try {
      const res = await fetch(`/api/rooms/bookings/${bookingId}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status })
      });
      const data = await res.json();
      if (data.success) {
        loadData();
      }
    } catch (e) {
      console.error(e);
    }
  }

  let filteredBookings = $derived(
    bookings.filter(b => statusFilter === 'ALL' || b.status === statusFilter)
  );

  let selectedFormRoom = $derived(rooms.find(r => r.id === formRoomId));
</script>

<div class="space-y-6">
  <!-- Title Bar -->
  <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
    <div>
      <div class="flex items-center gap-2">
        <h1 class="text-xl font-black text-slate-900 dark:text-white tracking-tight">
          Layanan Peminjaman Ruangan FIT
        </h1>
        <span class="px-2.5 py-0.5 text-xs font-bold rounded-full bg-amber-100 dark:bg-amber-950/60 text-amber-700 dark:text-amber-400">
          Gedung Selaru
        </span>
      </div>
      <p class="text-xs text-slate-500 mt-1">
        Pemesanan ruang rapat, multimedia, dan ruang diskusi dengan deteksi bentrok jadwal otomatis.
      </p>
    </div>

    <!-- Tab Selector -->
    <div class="flex items-center gap-1 bg-slate-100 dark:bg-slate-800 p-1 rounded-xl">
      <button
        onclick={() => activeTab = 'schedule'}
        class="px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer {activeTab === 'schedule' ? 'bg-white dark:bg-slate-900 text-red-600 dark:text-red-400 shadow-xs' : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'}"
      >
        Jadwal Ruangan
      </button>
      <button
        onclick={() => activeTab = 'form'}
        class="px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer {activeTab === 'form' ? 'bg-white dark:bg-slate-900 text-red-600 dark:text-red-400 shadow-xs' : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'}"
      >
        Form Pengajuan
      </button>
      <button
        onclick={() => activeTab = 'list'}
        class="px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer {activeTab === 'list' ? 'bg-white dark:bg-slate-900 text-red-600 dark:text-red-400 shadow-xs' : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'}"
      >
        Daftar Booking ({bookings.length})
      </button>
    </div>
  </div>

  <!-- TAB 1: SCHEDULE TIMELINE -->
  {#if activeTab === 'schedule'}
    <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-6">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 dark:border-slate-800 pb-4">
        <div>
          <h2 class="text-base font-bold text-slate-900 dark:text-white">Ketersediaan Ruangan Harian</h2>
          <p class="text-xs text-slate-500">Pilih tanggal untuk melihat jadwal penggunaan ruangan</p>
        </div>
        <div class="flex items-center gap-2">
          <CalendarIcon class="w-4 h-4 text-slate-400" />
          <input
            type="date"
            bind:value={timelineDate}
            class="px-3 py-1.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white"
          />
        </div>
      </div>

      <!-- Rooms Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {#each rooms as room}
          {@const roomBookings = bookings.filter(b => b.room_id === room.id && b.date_str === timelineDate && b.status === 'CONFIRMED')}
          <div class="bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 rounded-xl p-4 flex flex-col justify-between">
            <div>
              <div class="flex items-center justify-between mb-2">
                <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-amber-100 dark:bg-amber-950/60 text-amber-700 dark:text-amber-400">
                  {room.code}
                </span>
                <span class="text-xs text-slate-500 font-medium">
                  Kapasitas: <strong class="text-slate-800 dark:text-slate-200">{room.capacity} orang</strong>
                </span>
              </div>
              <h3 class="text-sm font-bold text-slate-900 dark:text-white">{room.name}</h3>
              <p class="text-[11px] text-slate-400 mb-3">{room.location}</p>

              <!-- Booked Slots for this day -->
              <div class="space-y-1.5 pt-2 border-t border-slate-200/60 dark:border-slate-700/50">
                <span class="text-[10px] font-bold uppercase text-slate-400 block">Jadwal Terisi:</span>
                {#if roomBookings.length === 0}
                  <span class="text-[11px] text-emerald-600 dark:text-emerald-400 font-semibold flex items-center gap-1">
                    <CheckCircle2 class="w-3.5 h-3.5" />
                    <span>Ruangan kosong seharian</span>
                  </span>
                {:else}
                  {#each roomBookings as bk}
                    <div class="p-2 rounded-lg bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900/40 text-xs">
                      <div class="font-mono font-bold text-red-600 dark:text-red-400 text-[11px]">
                        {bk.start_time} - {bk.end_time} WIB
                      </div>
                      <div class="text-[11px] font-medium text-slate-700 dark:text-slate-300 truncate">
                        {bk.purpose}
                      </div>
                      <div class="text-[10px] text-slate-400">
                        {bk.applicant_name} ({bk.unit_name})
                      </div>
                    </div>
                  {/each}
                {/if}
              </div>
            </div>

            <button
              onclick={() => {
                formRoomId = room.id;
                formDateStr = timelineDate;
                activeTab = 'form';
              }}
              class="mt-4 w-full py-1.5 bg-white dark:bg-slate-700 hover:bg-slate-100 dark:hover:bg-slate-600 border border-slate-200 dark:border-slate-600 rounded-lg text-xs font-semibold text-slate-700 dark:text-white cursor-pointer transition-colors"
            >
              Pinjam Ruangan Ini
            </button>
          </div>
        {/each}
      </div>
    </div>

  <!-- TAB 2: FORM PENGAJUAN -->
  {:else if activeTab === 'form'}
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Booking Form (2 cols) -->
      <div class="lg:col-span-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm">
        {#if submitError}
          <div class="mb-4 p-3 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 text-xs text-red-600 dark:text-red-300 flex items-center gap-2">
            <AlertCircle class="w-4 h-4 shrink-0" />
            <span>{submitError}</span>
          </div>
        {/if}

        <form onsubmit={handleBookingSubmit} class="space-y-4">
          <!-- Room & Date -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Pilih Ruangan *
              </label>
              <select
                bind:value={formRoomId}
                onchange={checkConflict}
                class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-red-500/30"
              >
                {#each rooms as r}
                  <option value={r.id}>[{r.code}] {r.name} ({r.capacity} org)</option>
                {/each}
              </select>
            </div>

            <div>
              <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Tanggal Kegiatan *
              </label>
              <input
                type="date"
                bind:value={formDateStr}
                onchange={checkConflict}
                class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-red-500/30"
              />
            </div>
          </div>

          <!-- Time Range -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Jam Mulai *
              </label>
              <input
                type="time"
                bind:value={formStartTime}
                onchange={checkConflict}
                class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-red-500/30"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Jam Selesai *
              </label>
              <input
                type="time"
                bind:value={formEndTime}
                onchange={checkConflict}
                class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-red-500/30"
              />
            </div>
          </div>

          <!-- Availability indicator -->
          {#if conflictError}
            <div class="p-3 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 text-xs text-red-700 dark:text-red-300 flex items-start gap-2">
              <AlertCircle class="w-4 h-4 shrink-0 mt-0.5 text-red-500" />
              <div>
                <strong>Bentrok Jadwal Terdeteksi!</strong>
                <p class="mt-0.5">{conflictError}</p>
              </div>
            </div>
          {:else if availabilityChecked}
            <div class="p-2.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800 text-xs text-emerald-700 dark:text-emerald-300 flex items-center gap-2">
              <CheckCircle2 class="w-4 h-4 text-emerald-500" />
              <span>Jadwal waktu dan ruangan ini <strong>tersedia (tidak bentrok)</strong>.</span>
            </div>
          {/if}

          <!-- Purpose -->
          <div>
            <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
              Agenda / Keperluan Acara *
            </label>
            <input
              type="text"
              bind:value={formPurpose}
              placeholder="Misal: Rapat Koordinasi Kurikulum D3 Sistem Informasi"
              class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-red-500/30"
            />
          </div>

          <!-- Unit & Applicant -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Unit / Prodi / Bagian *
              </label>
              <input
                type="text"
                bind:value={formUnitName}
                placeholder="Misal: Prodi D3 Sistem Informasi"
                class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-red-500/30"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Nama Pemohon / PIC *
              </label>
              <input
                type="text"
                bind:value={formApplicantName}
                placeholder="Nama staf atau dosen PIC..."
                class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-red-500/30"
              />
            </div>
          </div>

          <!-- Phone & Participant Count -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Nomor WhatsApp PIC
              </label>
              <input
                type="text"
                bind:value={formApplicantPhone}
                placeholder="081234567890"
                class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-red-500/30"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Perkiraan Jumlah Peserta
              </label>
              <input
                type="number"
                bind:value={formParticipantCount}
                class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-red-500/30"
              />
            </div>
          </div>

          <!-- Facilities Notes -->
          <div>
            <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
              Catatan Kebutuhan Fasilitas Tambahan
            </label>
            <textarea
              rows="2"
              bind:value={formFacilityNotes}
              placeholder="Misal: Mohon disiapkan 2 mikrofon wireless dan pointer..."
              class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-red-500/30"
            ></textarea>
          </div>

          <div class="pt-2">
            <button
              type="submit"
              disabled={submitting || !!conflictError}
              class="w-full py-3 px-4 bg-amber-500 hover:bg-amber-600 disabled:opacity-50 text-white font-bold text-sm rounded-xl shadow-md shadow-amber-500/20 transition-all cursor-pointer"
            >
              {submitting ? 'Menyimpan Peminjaman...' : 'Kirim Permohonan Peminjaman'}
            </button>
          </div>
        </form>
      </div>

      <!-- Room Spec Sidebar (1 col) -->
      <div class="space-y-4">
        {#if selectedFormRoom}
          <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm space-y-3">
            <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Informasi Ruangan Dipilih</span>
            <h3 class="text-base font-bold text-slate-900 dark:text-white">{selectedFormRoom.name}</h3>
            <p class="text-xs text-slate-500">{selectedFormRoom.location}</p>

            <div class="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/50 text-xs space-y-1.5">
              <div class="flex justify-between">
                <span class="text-slate-400">Kapasitas Maksimal:</span>
                <strong class="text-slate-800 dark:text-slate-200">{selectedFormRoom.capacity} Orang</strong>
              </div>
              <div class="flex justify-between">
                <span class="text-slate-400">Tipe Partisi:</span>
                <span class="text-slate-700 dark:text-slate-300">{selectedFormRoom.is_combo ? 'Combo (Gabungan)' : 'Reguler'}</span>
              </div>
            </div>

            <div class="text-xs text-slate-600 dark:text-slate-400">
              <span class="font-semibold block mb-1">Fasilitas Tersedia:</span>
              <p class="text-[11px] leading-relaxed bg-slate-50 dark:bg-slate-800/40 p-2.5 rounded-lg border border-slate-100 dark:border-slate-800">
                {selectedFormRoom.facilities}
              </p>
            </div>
          </div>
        {/if}
      </div>
    </div>

  <!-- TAB 3: DAFTAR BOOKING -->
  {:else if activeTab === 'list'}
    <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="text-base font-bold text-slate-900 dark:text-white">Daftar Pengajuan Peminjaman</h2>
        <div class="flex items-center gap-2">
          <Filter class="w-4 h-4 text-slate-400" />
          <select
            bind:value={statusFilter}
            class="px-3 py-1.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-slate-200"
          >
            <option value="ALL">Semua Status</option>
            <option value="CONFIRMED">CONFIRMED (Disetujui)</option>
            <option value="PENDING">PENDING (Menunggu)</option>
            <option value="REJECTED">REJECTED (Ditolak)</option>
            <option value="CANCELLED">CANCELLED (Dibatalkan)</option>
          </select>
        </div>
      </div>

      <div class="space-y-3">
        {#each filteredBookings as booking}
          <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div class="flex items-center gap-2 mb-1">
                <span class="font-mono text-xs font-bold text-amber-600 dark:text-amber-400">{booking.booking_number}</span>
                <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase {booking.status === 'CONFIRMED' ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-400' : booking.status === 'REJECTED' ? 'bg-red-100 text-red-700 dark:bg-red-950/60 dark:text-red-400' : 'bg-slate-200 text-slate-700'}">
                  {booking.status}
                </span>
              </div>
              <h4 class="text-sm font-bold text-slate-900 dark:text-white">{booking.room_name} - {booking.purpose}</h4>
              <p class="text-xs text-slate-500 mt-0.5">
                PIC: <strong class="text-slate-700 dark:text-slate-300">{booking.applicant_name}</strong> ({booking.unit_name}) • {booking.participant_count} Orang
              </p>
            </div>

            <div class="sm:text-right flex flex-col sm:items-end justify-between">
              <div class="text-xs font-semibold text-slate-900 dark:text-white">{formatDateIndo(booking.date_str)}</div>
              <div class="text-xs text-slate-500 font-mono mt-0.5 flex items-center gap-1">
                <Clock class="w-3.5 h-3.5 text-slate-400" />
                <span>{booking.start_time} - {booking.end_time} WIB</span>
              </div>

              {#if admin.isAdmin}
                <div class="flex items-center gap-1 mt-2">
                  {#if booking.status !== 'CONFIRMED'}
                    <button
                      onclick={() => updateStatus(booking.id, 'CONFIRMED')}
                      class="px-2.5 py-1 rounded bg-emerald-600 hover:bg-emerald-700 text-white text-[10px] font-bold cursor-pointer"
                    >
                      Setujui
                    </button>
                  {/if}
                  {#if booking.status !== 'REJECTED'}
                    <button
                      onclick={() => updateStatus(booking.id, 'REJECTED')}
                      class="px-2.5 py-1 rounded bg-red-600 hover:bg-red-700 text-white text-[10px] font-bold cursor-pointer"
                    >
                      Tolak
                    </button>
                  {/if}
                </div>
              {/if}
            </div>
          </div>
        {/each}
        {#if filteredBookings.length === 0}
          <div class="py-12 text-center text-xs text-slate-400">Tidak ada data peminjaman ruangan.</div>
        {/if}
      </div>
    </div>
  {/if}

  <!-- Booking Success Modal -->
  {#if submitSuccess}
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-xs">
      <div class="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 max-w-md w-full text-center space-y-4 shadow-2xl">
        <div class="w-14 h-14 rounded-2xl bg-emerald-100 text-emerald-600 mx-auto flex items-center justify-center">
          <Check class="w-7 h-7" />
        </div>
        <h3 class="text-lg font-black text-slate-900 dark:text-white">Peminjaman Berhasil Diajukan!</h3>
        <p class="text-xs text-slate-500">Nomor Registrasi Booking:</p>
        <div class="font-mono text-base font-black text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/40 p-3 rounded-xl border border-amber-200 dark:border-amber-800">
          {submitSuccess.bookingNumber}
        </div>
        <p class="text-xs text-slate-500">
          Jadwal penggunaan telah terdaftar pada sistem dan slot waktu terkunci.
        </p>
        <div class="pt-2">
          <button
            onclick={() => { submitSuccess = null; activeTab = 'schedule'; }}
            class="w-full py-2.5 bg-amber-500 hover:bg-amber-600 text-white font-bold rounded-xl text-xs cursor-pointer shadow-md shadow-amber-500/20"
          >
            Selesai & Lihat Jadwal
          </button>
        </div>
      </div>
    </div>
  {/if}
</div>
