<script lang="ts">
  import { onMount } from 'svelte';
  import { 
    Mail, 
    DoorOpen, 
    CalendarCheck, 
    Building2, 
    Search, 
    RefreshCw, 
    CheckCircle2, 
    Clock, 
    Sparkles,
    ShieldCheck
  } from 'lucide-svelte';

  interface Letter {
    id: string;
    sequence_number: number;
    full_number: string;
    subject: string;
    recipient: string | null;
    applicant_name: string;
    status: string;
    year: number;
    unit_name: string | null;
    category_name: string | null;
  }

  interface Room {
    id: string;
    name: string;
    code: string;
    capacity: number;
    location: string;
    facilities: string;
    is_combo: boolean;
    is_active: boolean;
  }

  interface Booking {
    id: string;
    booking_number: string;
    room_id: string;
    date_str: string;
    start_time: string;
    end_time: string;
    purpose: string;
    unit_name: string;
    applicant_name: string;
    applicant_phone: string;
    status: string;
    room_name: string | null;
  }

  interface Unit {
    id: string;
    name: string;
    code: string;
    category: string;
  }

  let activeTab = $state<'letters' | 'rooms' | 'bookings' | 'units'>('letters');
  let letters = $state<Letter[]>([]);
  let rooms = $state<Room[]>([]);
  let bookings = $state<Booking[]>([]);
  let units = $state<Unit[]>([]);
  let search = $state('');
  let loading = $state(true);
  let errorMsg = $state<string | null>(null);

  async function loadData() {
    loading = true;
    errorMsg = null;
    try {
      const [lRes, rRes, bRes, uRes] = await Promise.all([
        fetch('/api/letters').then(r => r.json()),
        fetch('/api/rooms').then(r => r.json()),
        fetch('/api/rooms/bookings').then(r => r.json()),
        fetch('/api/units').then(r => r.json())
      ]);
      letters = lRes;
      rooms = rRes;
      bookings = bRes;
      units = uRes;
    } catch (e: any) {
      console.error(e);
      errorMsg = 'Gagal memuat data dari server Rust. Pastikan backend aktif di port 8080.';
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    loadData();
  });

  let filteredLetters = $derived(
    letters.filter(l => 
      l.full_number.toLowerCase().includes(search.toLowerCase()) ||
      l.subject.toLowerCase().includes(search.toLowerCase()) ||
      l.applicant_name.toLowerCase().includes(search.toLowerCase()) ||
      (l.unit_name && l.unit_name.toLowerCase().includes(search.toLowerCase()))
    )
  );

  let filteredRooms = $derived(
    rooms.filter(r => 
      r.name.toLowerCase().includes(search.toLowerCase()) ||
      r.code.toLowerCase().includes(search.toLowerCase())
    )
  );

  let filteredBookings = $derived(
    bookings.filter(b => 
      b.booking_number.toLowerCase().includes(search.toLowerCase()) ||
      b.purpose.toLowerCase().includes(search.toLowerCase()) ||
      b.applicant_name.toLowerCase().includes(search.toLowerCase()) ||
      (b.room_name && b.room_name.toLowerCase().includes(search.toLowerCase()))
    )
  );
</script>

<div class="min-h-screen bg-slate-900 text-slate-100 flex flex-col font-sans selection:bg-red-600 selection:text-white">
  <!-- Header -->
  <header class="border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-30">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-red-700 to-rose-500 flex items-center justify-center shadow-lg shadow-red-600/30 ring-1 ring-red-500/50">
          <Sparkles class="w-5 h-5 text-white" />
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h1 class="text-base font-bold tracking-tight text-white">FIT E-OFFICE</h1>
            <span class="px-2 py-0.5 text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-full">
              Rust + Svelte 5 Edition
            </span>
          </div>
          <p class="text-xs text-slate-400">Layanan Sekretariat Fakultas Ilmu Terapan</p>
        </div>
      </div>

      <button 
        onclick={loadData}
        class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300 transition-colors cursor-pointer border border-slate-700"
      >
        <RefreshCw class="w-3.5 h-3.5 {loading ? 'animate-spin' : ''}" />
        <span>Refresh Data</span>
      </button>
    </div>
  </header>

  <!-- Navigation Tabs -->
  <div class="border-b border-slate-800 bg-slate-900/50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex space-x-1 sm:space-x-4 py-2 overflow-x-auto">
      <button 
        onclick={() => activeTab = 'letters'}
        class="flex items-center gap-2 px-4 py-2 rounded-lg text-xs sm:text-sm font-semibold transition-all cursor-pointer {activeTab === 'letters' ? 'bg-red-600 text-white shadow-md shadow-red-600/25' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'}"
      >
        <Mail class="w-4 h-4" />
        <span>Agenda Surat</span>
        <span class="ml-1 px-1.5 py-0.5 rounded text-[10px] {activeTab === 'letters' ? 'bg-red-800 text-red-100' : 'bg-slate-800 text-slate-400'}">{letters.length}</span>
      </button>

      <button 
        onclick={() => activeTab = 'rooms'}
        class="flex items-center gap-2 px-4 py-2 rounded-lg text-xs sm:text-sm font-semibold transition-all cursor-pointer {activeTab === 'rooms' ? 'bg-red-600 text-white shadow-md shadow-red-600/25' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'}"
      >
        <DoorOpen class="w-4 h-4" />
        <span>Ruangan</span>
        <span class="ml-1 px-1.5 py-0.5 rounded text-[10px] {activeTab === 'rooms' ? 'bg-red-800 text-red-100' : 'bg-slate-800 text-slate-400'}">{rooms.length}</span>
      </button>

      <button 
        onclick={() => activeTab = 'bookings'}
        class="flex items-center gap-2 px-4 py-2 rounded-lg text-xs sm:text-sm font-semibold transition-all cursor-pointer {activeTab === 'bookings' ? 'bg-red-600 text-white shadow-md shadow-red-600/25' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'}"
      >
        <CalendarCheck class="w-4 h-4" />
        <span>Peminjaman</span>
        <span class="ml-1 px-1.5 py-0.5 rounded text-[10px] {activeTab === 'bookings' ? 'bg-red-800 text-red-100' : 'bg-slate-800 text-slate-400'}">{bookings.length}</span>
      </button>

      <button 
        onclick={() => activeTab = 'units'}
        class="flex items-center gap-2 px-4 py-2 rounded-lg text-xs sm:text-sm font-semibold transition-all cursor-pointer {activeTab === 'units' ? 'bg-red-600 text-white shadow-md shadow-red-600/25' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'}"
      >
        <Building2 class="w-4 h-4" />
        <span>Unit / Bagian</span>
        <span class="ml-1 px-1.5 py-0.5 rounded text-[10px] {activeTab === 'units' ? 'bg-red-800 text-red-100' : 'bg-slate-800 text-slate-400'}">{units.length}</span>
      </button>
    </div>
  </div>

  <!-- Search & Filter Toolbar -->
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 w-full">
    <div class="relative w-full max-w-md">
      <Search class="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
      <input 
        type="text" 
        bind:value={search}
        placeholder="Cari nomor, perihal, atau nama pemohon..."
        class="w-full pl-10 pr-4 py-2 bg-slate-800/80 border border-slate-700/80 rounded-xl text-sm text-slate-200 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-red-500/50 focus:border-red-500 transition-all"
      />
    </div>
  </div>

  <!-- Main Content Area -->
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12 flex-1 w-full">
    {#if errorMsg}
      <div class="p-4 rounded-xl bg-red-950/40 border border-red-800/60 text-red-300 text-sm mb-6 flex items-center gap-3">
        <span class="w-2 h-2 rounded-full bg-red-400 animate-ping"></span>
        <span>{errorMsg}</span>
      </div>
    {/if}

    {#if loading}
      <div class="flex flex-col items-center justify-center py-20 text-slate-400 gap-3">
        <RefreshCw class="w-8 h-8 animate-spin text-red-500" />
        <p class="text-sm font-medium">Memuat data langsung dari SQLite via Rust Backend...</p>
      </div>
    {:else}
      <!-- TAB 1: AGENDA SURAT -->
      {#if activeTab === 'letters'}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {#each filteredLetters as letter (letter.id)}
            <div class="bg-slate-800/40 border border-slate-700/60 rounded-xl p-4 hover:border-slate-600 transition-all hover:shadow-xl hover:shadow-black/20 flex flex-col justify-between group">
              <div>
                <div class="flex items-start justify-between gap-2 mb-2">
                  <span class="px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider bg-slate-700/60 text-slate-300">
                    {letter.category_name || 'Umum'}
                  </span>
                  <span class="text-xs text-slate-400 font-mono">#{letter.sequence_number}</span>
                </div>
                <h3 class="text-sm font-bold text-white group-hover:text-red-400 transition-colors font-mono mb-2">
                  {letter.full_number}
                </h3>
                <p class="text-xs text-slate-300 line-clamp-2 mb-3">
                  {letter.subject}
                </p>
              </div>

              <div class="pt-3 border-t border-slate-700/50 flex items-center justify-between text-[11px] text-slate-400">
                <span class="font-medium text-slate-300">{letter.applicant_name}</span>
                <span>{letter.unit_name || '-'}</span>
              </div>
            </div>
          {/each}
        </div>
        {#if filteredLetters.length === 0}
          <div class="text-center py-16 text-slate-500 text-sm">Tidak ada surat yang sesuai dengan pencarian.</div>
        {/if}

      <!-- TAB 2: RUANGAN -->
      {:else if activeTab === 'rooms'}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {#each filteredRooms as room (room.id)}
            <div class="bg-slate-800/40 border border-slate-700/60 rounded-xl p-5 hover:border-slate-600 transition-all">
              <div class="flex items-center justify-between mb-3">
                <span class="px-2 py-0.5 rounded text-[10px] font-bold tracking-wider uppercase bg-red-950/60 text-red-400 border border-red-800/40">
                  {room.code}
                </span>
                <span class="text-xs text-slate-400 flex items-center gap-1">
                  Kapasitas: <strong class="text-white">{room.capacity} orang</strong>
                </span>
              </div>
              <h3 class="text-base font-bold text-white mb-1">{room.name}</h3>
              <p class="text-xs text-slate-400 mb-3">{room.location}</p>
              <div class="text-xs text-slate-300 bg-slate-900/60 rounded-lg p-2.5 border border-slate-800">
                <span class="font-semibold text-slate-400 block mb-1 text-[10px] uppercase">Fasilitas:</span>
                <span class="text-[11px] leading-relaxed text-slate-300">{room.facilities}</span>
              </div>
            </div>
          {/each}
        </div>

      <!-- TAB 3: PEMINJAMAN RUANGAN -->
      {:else if activeTab === 'bookings'}
        <div class="space-y-3">
          {#each filteredBookings as booking (booking.id)}
            <div class="bg-slate-800/40 border border-slate-700/60 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <div class="flex items-center gap-2 mb-1">
                  <span class="font-mono text-xs font-bold text-red-400">{booking.booking_number}</span>
                  <span class="text-xs px-2 py-0.5 rounded font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px]">
                    {booking.status}
                  </span>
                </div>
                <h4 class="text-sm font-bold text-white mb-0.5">{booking.room_name || 'Ruangan'} - {booking.purpose}</h4>
                <p class="text-xs text-slate-400">
                  PIC: <span class="text-slate-200 font-medium">{booking.applicant_name}</span> ({booking.unit_name})
                </p>
              </div>

              <div class="sm:text-right flex sm:flex-col items-center sm:items-end justify-between border-t sm:border-t-0 pt-2 sm:pt-0 border-slate-700">
                <div class="text-xs font-semibold text-white">{booking.date_str}</div>
                <div class="text-xs text-slate-400 font-mono flex items-center gap-1 mt-0.5">
                  <Clock class="w-3 h-3 text-slate-400" />
                  <span>{booking.start_time} - {booking.end_time} WIB</span>
                </div>
              </div>
            </div>
          {/each}
        </div>

      <!-- TAB 4: MASTER UNIT -->
      {:else if activeTab === 'units'}
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {#each units as unit (unit.id)}
            <div class="bg-slate-800/40 border border-slate-700/60 rounded-xl p-3.5 flex items-center justify-between">
              <div>
                <h4 class="text-xs font-bold text-white leading-tight">{unit.name}</h4>
                <span class="text-[10px] text-slate-400 font-mono mt-0.5 block">Kode: {unit.code}</span>
              </div>
              <span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-700/60 text-slate-300">
                {unit.category}
              </span>
            </div>
          {/each}
        </div>
      {/if}
    {/if}
  </main>

  <!-- Footer -->
  <footer class="border-t border-slate-800 py-6 bg-slate-950 text-center text-xs text-slate-500">
    <p>FIT E-Office • Built with <strong>Rust (Axum + SQLx)</strong> & <strong>Svelte 5</strong></p>
    <p class="mt-1 text-[11px]">Memori backend ~20MB RAM • Direct SQLite Access • Single Embedded Binary Ready</p>
  </footer>
</div>
