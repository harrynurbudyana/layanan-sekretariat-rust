#!/usr/bin/env python3
"""
Seed and synchronize all official letter categories from Universitas Telkom Guideline
(Pedoman Penerbitan Surat dan Penomoran Dokumen di Lingkungan Universitas Telkom).

Total: 284 categories across 25 Bidang + BTP Proyek.
"""

import os
import shutil
import sqlite3
import uuid
import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'dev.db')
BACKUP_PATH = DB_PATH + '.bak'

CATEGORIES = [
  {
    "name": "Umum",
    "code": "SEN01",
    "group": "SEN",
    "classificationCode": "SEN01",
    "description": "Umum (Urusan Senat Universitas)",
    "bidang": "A. Kode Kegiatan SENAT",
    "no": 1
  },
  {
    "name": "Rapat Pleno Senat",
    "code": "SEN02",
    "group": "SEN",
    "classificationCode": "SEN02",
    "description": "Rapat Pleno Senat (Urusan Senat Universitas)",
    "bidang": "A. Kode Kegiatan SENAT",
    "no": 2
  },
  {
    "name": "Berita Acara Pertimbangan/Persetujuan Senat Universitas",
    "code": "SEN03",
    "group": "SEN",
    "classificationCode": "SEN03",
    "description": "Berita Acara Pertimbangan/Persetujuan Senat Universitas (Urusan Senat Universitas)",
    "bidang": "A. Kode Kegiatan SENAT",
    "no": 3
  },
  {
    "name": "Kegiatan Senat",
    "code": "SEN04",
    "group": "SEN",
    "classificationCode": "SEN04",
    "description": "Kegiatan Senat (Urusan Senat Universitas)",
    "bidang": "A. Kode Kegiatan SENAT",
    "no": 4
  },
  {
    "name": "Umum",
    "code": "PRA01",
    "group": "PRA",
    "classificationCode": "PRA01",
    "description": "Umum (Public Relations & Analytics)",
    "bidang": "PUBLIC RELATIONS & ANALYTICS",
    "no": 1
  },
  {
    "name": "Identitas Kelembagaan",
    "code": "PRA02",
    "group": "PRA",
    "classificationCode": "PRA02",
    "description": "Identitas Kelembagaan (Public Relations & Analytics)",
    "bidang": "PUBLIC RELATIONS & ANALYTICS",
    "no": 2
  },
  {
    "name": "Branding",
    "code": "PRA03",
    "group": "PRA",
    "classificationCode": "PRA03",
    "description": "Branding (Public Relations & Analytics)",
    "bidang": "PUBLIC RELATIONS & ANALYTICS",
    "no": 3
  },
  {
    "name": "Pengembangan Konten Website Tel-U",
    "code": "PRA04",
    "group": "PRA",
    "classificationCode": "PRA04",
    "description": "Pengembangan Konten Website Tel-U (Public Relations & Analytics)",
    "bidang": "PUBLIC RELATIONS & ANALYTICS",
    "no": 4
  },
  {
    "name": "Protokoler",
    "code": "PRA05",
    "group": "PRA",
    "classificationCode": "PRA05",
    "description": "Protokoler (Public Relations & Analytics)",
    "bidang": "PUBLIC RELATIONS & ANALYTICS",
    "no": 5
  },
  {
    "name": "Press Release",
    "code": "PRA06",
    "group": "PRA",
    "classificationCode": "PRA06",
    "description": "Press Release (Public Relations & Analytics)",
    "bidang": "PUBLIC RELATIONS & ANALYTICS",
    "no": 6
  },
  {
    "name": "Peliputan dan Laporan Peristiwa",
    "code": "PRA07",
    "group": "PRA",
    "classificationCode": "PRA07",
    "description": "Peliputan dan Laporan Peristiwa (Public Relations & Analytics)",
    "bidang": "PUBLIC RELATIONS & ANALYTICS",
    "no": 7
  },
  {
    "name": "Kunjungan Studi Banding",
    "code": "PRA08",
    "group": "PRA",
    "classificationCode": "PRA08",
    "description": "Kunjungan Studi Banding (Public Relations & Analytics)",
    "bidang": "PUBLIC RELATIONS & ANALYTICS",
    "no": 8
  },
  {
    "name": "Bina Lingkungan",
    "code": "PRA09",
    "group": "PRA",
    "classificationCode": "PRA09",
    "description": "Bina Lingkungan (Public Relations & Analytics)",
    "bidang": "PUBLIC RELATIONS & ANALYTICS",
    "no": 9
  },
  {
    "name": "Komunikasi Eksternal",
    "code": "PRA10",
    "group": "PRA",
    "classificationCode": "PRA10",
    "description": "Komunikasi Eksternal (Public Relations & Analytics)",
    "bidang": "PUBLIC RELATIONS & ANALYTICS",
    "no": 10
  },
  {
    "name": "Laporan Analisa Website dan Media Sosial",
    "code": "PRA11",
    "group": "PRA",
    "classificationCode": "PRA11",
    "description": "Laporan Analisa Website dan Media Sosial (Public Relations & Analytics)",
    "bidang": "PUBLIC RELATIONS & ANALYTICS",
    "no": 11
  },
  {
    "name": "Umum",
    "code": "SAI01",
    "group": "SAI",
    "classificationCode": "SAI01",
    "description": "Umum (Satuan Audit Internal)",
    "bidang": "SATUAN AUDIT INTERNAL",
    "no": 1
  },
  {
    "name": "Sertifikasi",
    "code": "SAI02",
    "group": "SAI",
    "classificationCode": "SAI02",
    "description": "Sertifikasi (Satuan Audit Internal)",
    "bidang": "SATUAN AUDIT INTERNAL",
    "no": 2
  },
  {
    "name": "Audit Mutu Internal",
    "code": "SAI03",
    "group": "SAI",
    "classificationCode": "SAI03",
    "description": "Audit Mutu Internal (Satuan Audit Internal)",
    "bidang": "SATUAN AUDIT INTERNAL",
    "no": 3
  },
  {
    "name": "Audit Mutu Eksternal",
    "code": "SAI04",
    "group": "SAI",
    "classificationCode": "SAI04",
    "description": "Audit Mutu Eksternal (Satuan Audit Internal)",
    "bidang": "SATUAN AUDIT INTERNAL",
    "no": 4
  },
  {
    "name": "Pengawasan dan Pemeriksaan",
    "code": "SAI05",
    "group": "SAI",
    "classificationCode": "SAI05",
    "description": "Pengawasan dan Pemeriksaan (Satuan Audit Internal)",
    "bidang": "SATUAN AUDIT INTERNAL",
    "no": 5
  },
  {
    "name": "Dokumentasi dan Kearsipan",
    "code": "SAI06",
    "group": "SAI",
    "classificationCode": "SAI06",
    "description": "Dokumentasi dan Kearsipan (Satuan Audit Internal)",
    "bidang": "SATUAN AUDIT INTERNAL",
    "no": 6
  },
  {
    "name": "Laporan",
    "code": "SAI07",
    "group": "SAI",
    "classificationCode": "SAI07",
    "description": "Laporan (Satuan Audit Internal)",
    "bidang": "SATUAN AUDIT INTERNAL",
    "no": 7
  },
  {
    "name": "Umum",
    "code": "ORG01",
    "group": "ORG",
    "classificationCode": "ORG01",
    "description": "Umum (Pengembangan Institusi dan Organisasi)",
    "bidang": "PENGEMBANGAN INSTITUSI (ORGANISASI)",
    "no": 1
  },
  {
    "name": "Statuta",
    "code": "ORG02",
    "group": "ORG",
    "classificationCode": "ORG02",
    "description": "Statuta (Pengembangan Institusi dan Organisasi)",
    "bidang": "PENGEMBANGAN INSTITUSI (ORGANISASI)",
    "no": 2
  },
  {
    "name": "Rencana Strategis (RENSTRA)",
    "code": "ORG03",
    "group": "ORG",
    "classificationCode": "ORG03",
    "description": "Rencana Strategis (RENSTRA) (Pengembangan Institusi dan Organisasi)",
    "bidang": "PENGEMBANGAN INSTITUSI (ORGANISASI)",
    "no": 3
  },
  {
    "name": "Rencana Empat Tahun (RENETA)",
    "code": "ORG04",
    "group": "ORG",
    "classificationCode": "ORG04",
    "description": "Rencana Empat Tahun (RENETA) (Pengembangan Institusi dan Organisasi)",
    "bidang": "PENGEMBANGAN INSTITUSI (ORGANISASI)",
    "no": 4
  },
  {
    "name": "Rencana Induk Pengembangan (RENIP)",
    "code": "ORG05",
    "group": "ORG",
    "classificationCode": "ORG05",
    "description": "Rencana Induk Pengembangan (RENIP) (Pengembangan Institusi dan Organisasi)",
    "bidang": "PENGEMBANGAN INSTITUSI (ORGANISASI)",
    "no": 5
  },
  {
    "name": "Struktur Organisasi",
    "code": "ORG06",
    "group": "ORG",
    "classificationCode": "ORG06",
    "description": "Struktur Organisasi (Pengembangan Institusi dan Organisasi)",
    "bidang": "PENGEMBANGAN INSTITUSI (ORGANISASI)",
    "no": 6
  },
  {
    "name": "Kontrak Manajemen",
    "code": "ORG07",
    "group": "ORG",
    "classificationCode": "ORG07",
    "description": "Kontrak Manajemen (Pengembangan Institusi dan Organisasi)",
    "bidang": "PENGEMBANGAN INSTITUSI (ORGANISASI)",
    "no": 7
  },
  {
    "name": "Rencana Kerja Manajerial (RKM)",
    "code": "ORG08",
    "group": "ORG",
    "classificationCode": "ORG08",
    "description": "Rencana Kerja Manajerial (RKM) (Pengembangan Institusi dan Organisasi)",
    "bidang": "PENGEMBANGAN INSTITUSI (ORGANISASI)",
    "no": 8
  },
  {
    "name": "Rencana Kerja Anggaran (RKA)",
    "code": "ORG09",
    "group": "ORG",
    "classificationCode": "ORG09",
    "description": "Rencana Kerja Anggaran (RKA) (Pengembangan Institusi dan Organisasi)",
    "bidang": "PENGEMBANGAN INSTITUSI (ORGANISASI)",
    "no": 9
  },
  {
    "name": "Nilai Kinerja Lembaga",
    "code": "ORG10",
    "group": "ORG",
    "classificationCode": "ORG10",
    "description": "Nilai Kinerja Lembaga (Pengembangan Institusi dan Organisasi)",
    "bidang": "PENGEMBANGAN INSTITUSI (ORGANISASI)",
    "no": 10
  },
  {
    "name": "Dies Natalis/Lustrum",
    "code": "ORG11",
    "group": "ORG",
    "classificationCode": "ORG11",
    "description": "Dies Natalis/Lustrum (Pengembangan Institusi dan Organisasi)",
    "bidang": "PENGEMBANGAN INSTITUSI (ORGANISASI)",
    "no": 11
  },
  {
    "name": "Tata Pamong (Governance System)",
    "code": "ORG12",
    "group": "ORG",
    "classificationCode": "ORG12",
    "description": "Tata Pamong (Governance System) (Pengembangan Institusi dan Organisasi)",
    "bidang": "PENGEMBANGAN INSTITUSI (ORGANISASI)",
    "no": 12
  },
  {
    "name": "Laporan",
    "code": "ORG13",
    "group": "ORG",
    "classificationCode": "ORG13",
    "description": "Laporan (Pengembangan Institusi dan Organisasi)",
    "bidang": "PENGEMBANGAN INSTITUSI (ORGANISASI)",
    "no": 13
  },
  {
    "name": "Umum",
    "code": "SKR01",
    "group": "SKR",
    "classificationCode": "SKR01",
    "description": "Umum (Sekretariat Pimpinan dan Tata Persuratan)",
    "bidang": "SEKRETARIAT PIMPINAN",
    "no": 1
  },
  {
    "name": "Rapat Tinjauan Manajemen/Rapat Pimpinan/Rapat Manajemen",
    "code": "SKR02",
    "group": "SKR",
    "classificationCode": "SKR02",
    "description": "Rapat Tinjauan Manajemen/Rapat Pimpinan/Rapat Manajemen (Sekretariat Pimpinan dan Tata Persuratan)",
    "bidang": "SEKRETARIAT PIMPINAN",
    "no": 2
  },
  {
    "name": "Kegiatan Pimpinan/Kelembagaan",
    "code": "SKR03",
    "group": "SKR",
    "classificationCode": "SKR03",
    "description": "Kegiatan Pimpinan/Kelembagaan (Sekretariat Pimpinan dan Tata Persuratan)",
    "bidang": "SEKRETARIAT PIMPINAN",
    "no": 3
  },
  {
    "name": "Tata Naskah Korespondensi",
    "code": "SKR04",
    "group": "SKR",
    "classificationCode": "SKR04",
    "description": "Tata Naskah Korespondensi (Sekretariat Pimpinan dan Tata Persuratan)",
    "bidang": "SEKRETARIAT PIMPINAN",
    "no": 4
  },
  {
    "name": "Undangan",
    "code": "SKR05",
    "group": "SKR",
    "classificationCode": "SKR05",
    "description": "Undangan (Sekretariat Pimpinan dan Tata Persuratan)",
    "bidang": "SEKRETARIAT PIMPINAN",
    "no": 5
  },
  {
    "name": "Laporan",
    "code": "SKR06",
    "group": "SKR",
    "classificationCode": "SKR06",
    "description": "Laporan (Sekretariat Pimpinan dan Tata Persuratan)",
    "bidang": "SEKRETARIAT PIMPINAN",
    "no": 6
  },
  {
    "name": "Umum",
    "code": "LGL01",
    "group": "LGL",
    "classificationCode": "LGL01",
    "description": "Umum (Legal, Peraturan dan Kebijakan Hukum)",
    "bidang": "LEGAL",
    "no": 1
  },
  {
    "name": "Keputusan dan Kebijakan Eksternal",
    "code": "LGL02",
    "group": "LGL",
    "classificationCode": "LGL02",
    "description": "Keputusan dan Kebijakan Eksternal (Legal, Peraturan dan Kebijakan Hukum)",
    "bidang": "LEGAL",
    "no": 2
  },
  {
    "name": "Keputusan dan Kebijakan dari Internal",
    "code": "LGL03",
    "group": "LGL",
    "classificationCode": "LGL03",
    "description": "Keputusan dan Kebijakan dari Internal (Legal, Peraturan dan Kebijakan Hukum)",
    "bidang": "LEGAL",
    "no": 3
  },
  {
    "name": "Penyelesaian Hukum",
    "code": "LGL04",
    "group": "LGL",
    "classificationCode": "LGL04",
    "description": "Penyelesaian Hukum (Legal, Peraturan dan Kebijakan Hukum)",
    "bidang": "LEGAL",
    "no": 4
  },
  {
    "name": "Pelanggaran & Tindakan Hukum",
    "code": "LGL05",
    "group": "LGL",
    "classificationCode": "LGL05",
    "description": "Pelanggaran & Tindakan Hukum (Legal, Peraturan dan Kebijakan Hukum)",
    "bidang": "LEGAL",
    "no": 5
  },
  {
    "name": "Bantuan Hukum",
    "code": "LGL06",
    "group": "LGL",
    "classificationCode": "LGL06",
    "description": "Bantuan Hukum (Legal, Peraturan dan Kebijakan Hukum)",
    "bidang": "LEGAL",
    "no": 6
  },
  {
    "name": "Peraturan",
    "code": "LGL07",
    "group": "LGL",
    "classificationCode": "LGL07",
    "description": "Peraturan (Legal, Peraturan dan Kebijakan Hukum)",
    "bidang": "LEGAL",
    "no": 7
  },
  {
    "name": "Laporan",
    "code": "LGL08",
    "group": "LGL",
    "classificationCode": "LGL08",
    "description": "Laporan (Legal, Peraturan dan Kebijakan Hukum)",
    "bidang": "LEGAL",
    "no": 8
  },
  {
    "name": "Umum",
    "code": "SPM01",
    "group": "SPM",
    "classificationCode": "SPM01",
    "description": "Umum (Satuan Penjaminan Mutu)",
    "bidang": "SATUAN PENJAMINAN MUTU",
    "no": 1
  },
  {
    "name": "Kebijakan/Pedoman Mutu",
    "code": "SPM02",
    "group": "SPM",
    "classificationCode": "SPM02",
    "description": "Kebijakan/Pedoman Mutu (Satuan Penjaminan Mutu)",
    "bidang": "SATUAN PENJAMINAN MUTU",
    "no": 2
  },
  {
    "name": "Standar/Sasaran Mutu",
    "code": "SPM03",
    "group": "SPM",
    "classificationCode": "SPM03",
    "description": "Standar/Sasaran Mutu (Satuan Penjaminan Mutu)",
    "bidang": "SATUAN PENJAMINAN MUTU",
    "no": 3
  },
  {
    "name": "Proses Bisnis/Prosedur/Instruksi Kerja",
    "code": "SPM04",
    "group": "SPM",
    "classificationCode": "SPM04",
    "description": "Proses Bisnis/Prosedur/Instruksi Kerja (Satuan Penjaminan Mutu)",
    "bidang": "SATUAN PENJAMINAN MUTU",
    "no": 4
  },
  {
    "name": "Dokumen/Formulir/Rekaman Mutu",
    "code": "SPM05",
    "group": "SPM",
    "classificationCode": "SPM05",
    "description": "Dokumen/Formulir/Rekaman Mutu (Satuan Penjaminan Mutu)",
    "bidang": "SATUAN PENJAMINAN MUTU",
    "no": 5
  },
  {
    "name": "Kinerja/Capaian Mutu",
    "code": "SPM06",
    "group": "SPM",
    "classificationCode": "SPM06",
    "description": "Kinerja/Capaian Mutu (Satuan Penjaminan Mutu)",
    "bidang": "SATUAN PENJAMINAN MUTU",
    "no": 6
  },
  {
    "name": "Akreditasi/Sertifikasi",
    "code": "SPM07",
    "group": "SPM",
    "classificationCode": "SPM07",
    "description": "Akreditasi/Sertifikasi (Satuan Penjaminan Mutu)",
    "bidang": "SATUAN PENJAMINAN MUTU",
    "no": 7
  },
  {
    "name": "Ijin Pembukaan Program Studi",
    "code": "SPM08",
    "group": "SPM",
    "classificationCode": "SPM08",
    "description": "Ijin Pembukaan Program Studi (Satuan Penjaminan Mutu)",
    "bidang": "SATUAN PENJAMINAN MUTU",
    "no": 8
  },
  {
    "name": "QMR/GKM",
    "code": "SPM09",
    "group": "SPM",
    "classificationCode": "SPM09",
    "description": "QMR/GKM (Satuan Penjaminan Mutu)",
    "bidang": "SATUAN PENJAMINAN MUTU",
    "no": 9
  },
  {
    "name": "Laporan",
    "code": "SPM10",
    "group": "SPM",
    "classificationCode": "SPM10",
    "description": "Laporan (Satuan Penjaminan Mutu)",
    "bidang": "SATUAN PENJAMINAN MUTU",
    "no": 10
  },
  {
    "name": "Umum",
    "code": "PTI01",
    "group": "PTI",
    "classificationCode": "PTI01",
    "description": "Umum (Pusat Teknologi Informasi)",
    "bidang": "PUSAT TEKNOLOGI INFORMASI",
    "no": 1
  },
  {
    "name": "Pengelolaan Perangkat Keras",
    "code": "PTI02",
    "group": "PTI",
    "classificationCode": "PTI02",
    "description": "Pengelolaan Perangkat Keras (Pusat Teknologi Informasi)",
    "bidang": "PUSAT TEKNOLOGI INFORMASI",
    "no": 2
  },
  {
    "name": "Pengelolaan Perangkat Lunak",
    "code": "PTI03",
    "group": "PTI",
    "classificationCode": "PTI03",
    "description": "Pengelolaan Perangkat Lunak (Pusat Teknologi Informasi)",
    "bidang": "PUSAT TEKNOLOGI INFORMASI",
    "no": 3
  },
  {
    "name": "Pengelolaan Layanan Teknologi Informasi",
    "code": "PTI04",
    "group": "PTI",
    "classificationCode": "PTI04",
    "description": "Pengelolaan Layanan Teknologi Informasi (Pusat Teknologi Informasi)",
    "bidang": "PUSAT TEKNOLOGI INFORMASI",
    "no": 4
  },
  {
    "name": "Pengelolaan Riset Kebutuhan Teknologi Informasi",
    "code": "PTI05",
    "group": "PTI",
    "classificationCode": "PTI05",
    "description": "Pengelolaan Riset Kebutuhan Teknologi Informasi (Pusat Teknologi Informasi)",
    "bidang": "PUSAT TEKNOLOGI INFORMASI",
    "no": 5
  },
  {
    "name": "Pengembangan Produk Teknologi Informasi",
    "code": "PTI06",
    "group": "PTI",
    "classificationCode": "PTI06",
    "description": "Pengembangan Produk Teknologi Informasi (Pusat Teknologi Informasi)",
    "bidang": "PUSAT TEKNOLOGI INFORMASI",
    "no": 6
  },
  {
    "name": "Pemeliharaan Sistem",
    "code": "PTI07",
    "group": "PTI",
    "classificationCode": "PTI07",
    "description": "Pemeliharaan Sistem (Pusat Teknologi Informasi)",
    "bidang": "PUSAT TEKNOLOGI INFORMASI",
    "no": 7
  },
  {
    "name": "Pemeliharaan Infratruktur Teknologi Informasi",
    "code": "PTI08",
    "group": "PTI",
    "classificationCode": "PTI08",
    "description": "Pemeliharaan Infratruktur Teknologi Informasi (Pusat Teknologi Informasi)",
    "bidang": "PUSAT TEKNOLOGI INFORMASI",
    "no": 8
  },
  {
    "name": "Pengembangan Infrastruktur Teknologi Informasi",
    "code": "PTI09",
    "group": "PTI",
    "classificationCode": "PTI09",
    "description": "Pengembangan Infrastruktur Teknologi Informasi (Pusat Teknologi Informasi)",
    "bidang": "PUSAT TEKNOLOGI INFORMASI",
    "no": 9
  },
  {
    "name": "Pengelolaan Database",
    "code": "PTI10",
    "group": "PTI",
    "classificationCode": "PTI10",
    "description": "Pengelolaan Database (Pusat Teknologi Informasi)",
    "bidang": "PUSAT TEKNOLOGI INFORMASI",
    "no": 10
  },
  {
    "name": "Pengadaan Perangkat Keras dan Lunak",
    "code": "PTI11",
    "group": "PTI",
    "classificationCode": "PTI11",
    "description": "Pengadaan Perangkat Keras dan Lunak (Pusat Teknologi Informasi)",
    "bidang": "PUSAT TEKNOLOGI INFORMASI",
    "no": 11
  },
  {
    "name": "Laporan",
    "code": "PTI12",
    "group": "PTI",
    "classificationCode": "PTI12",
    "description": "Laporan (Pusat Teknologi Informasi)",
    "bidang": "PUSAT TEKNOLOGI INFORMASI",
    "no": 12
  },
  {
    "name": "Umum",
    "code": "KTU01",
    "group": "KTU",
    "classificationCode": "KTU01",
    "description": "Umum (Komite Transformasi Universitas)",
    "bidang": "KOMITE TRANSFORMASI UNIVERSITAS",
    "no": 1
  },
  {
    "name": "Perencanaan dan Dukungan Komunikasi Transformasi",
    "code": "KTU02",
    "group": "KTU",
    "classificationCode": "KTU02",
    "description": "Perencanaan dan Dukungan Komunikasi Transformasi (Komite Transformasi Universitas)",
    "bidang": "KOMITE TRANSFORMASI UNIVERSITAS",
    "no": 2
  },
  {
    "name": "Pemantauan dan Laporan Transformasi",
    "code": "KTU03",
    "group": "KTU",
    "classificationCode": "KTU03",
    "description": "Pemantauan dan Laporan Transformasi (Komite Transformasi Universitas)",
    "bidang": "KOMITE TRANSFORMASI UNIVERSITAS",
    "no": 3
  },
  {
    "name": "Umum",
    "code": "AKD01",
    "group": "AKD",
    "classificationCode": "AKD01",
    "description": "Umum (Akademik, Kurikulum dan Pembelajaran)",
    "bidang": "AKADEMIK",
    "no": 1
  },
  {
    "name": "Informasi & Laporan Akademik/ PDDIKTI",
    "code": "AKD02",
    "group": "AKD",
    "classificationCode": "AKD02",
    "description": "Informasi & Laporan Akademik/ PDDIKTI (Akademik, Kurikulum dan Pembelajaran)",
    "bidang": "AKADEMIK",
    "no": 2
  },
  {
    "name": "Perencanaan Akademik",
    "code": "AKD03",
    "group": "AKD",
    "classificationCode": "AKD03",
    "description": "Perencanaan Akademik (Akademik, Kurikulum dan Pembelajaran)",
    "bidang": "AKADEMIK",
    "no": 3
  },
  {
    "name": "Penerimaan Mahasiswa Baru (PMB)",
    "code": "AKD04",
    "group": "AKD",
    "classificationCode": "AKD04",
    "description": "Penerimaan Mahasiswa Baru (PMB) (Akademik, Kurikulum dan Pembelajaran)",
    "bidang": "AKADEMIK",
    "no": 4
  },
  {
    "name": "Program Studi",
    "code": "AKD05",
    "group": "AKD",
    "classificationCode": "AKD05",
    "description": "Program Studi (Akademik, Kurikulum dan Pembelajaran)",
    "bidang": "AKADEMIK",
    "no": 5
  },
  {
    "name": "Kurikulum dan Silabus",
    "code": "AKD06",
    "group": "AKD",
    "classificationCode": "AKD06",
    "description": "Kurikulum dan Silabus (Akademik, Kurikulum dan Pembelajaran)",
    "bidang": "AKADEMIK",
    "no": 6
  },
  {
    "name": "Pindah Jurusan/Program Studi",
    "code": "AKD07",
    "group": "AKD",
    "classificationCode": "AKD07",
    "description": "Pindah Jurusan/Program Studi (Akademik, Kurikulum dan Pembelajaran)",
    "bidang": "AKADEMIK",
    "no": 7
  },
  {
    "name": "Perkuliahan",
    "code": "AKD08",
    "group": "AKD",
    "classificationCode": "AKD08",
    "description": "Perkuliahan (Akademik, Kurikulum dan Pembelajaran)",
    "bidang": "AKADEMIK",
    "no": 8
  },
  {
    "name": "Praktikum",
    "code": "AKD09",
    "group": "AKD",
    "classificationCode": "AKD09",
    "description": "Praktikum (Akademik, Kurikulum dan Pembelajaran)",
    "bidang": "AKADEMIK",
    "no": 9
  },
  {
    "name": "Ujian dan Evaluasi",
    "code": "AKD10",
    "group": "AKD",
    "classificationCode": "AKD10",
    "description": "Ujian dan Evaluasi (Akademik, Kurikulum dan Pembelajaran)",
    "bidang": "AKADEMIK",
    "no": 10
  },
  {
    "name": "Tugas Akhir/Proyek Akhir/Thesis",
    "code": "AKD11",
    "group": "AKD",
    "classificationCode": "AKD11",
    "description": "Tugas Akhir/Proyek Akhir/Thesis (Akademik, Kurikulum dan Pembelajaran)",
    "bidang": "AKADEMIK",
    "no": 11
  },
  {
    "name": "Coop dan Geladi",
    "code": "AKD12",
    "group": "AKD",
    "classificationCode": "AKD12",
    "description": "Coop dan Geladi (Akademik, Kurikulum dan Pembelajaran)",
    "bidang": "AKADEMIK",
    "no": 12
  },
  {
    "name": "Kerja Praktek",
    "code": "AKD13",
    "group": "AKD",
    "classificationCode": "AKD13",
    "description": "Kerja Praktek (Akademik, Kurikulum dan Pembelajaran)",
    "bidang": "AKADEMIK",
    "no": 13
  },
  {
    "name": "Nilai Ujian dan Nilai Mata Kuliah",
    "code": "AKD14",
    "group": "AKD",
    "classificationCode": "AKD14",
    "description": "Nilai Ujian dan Nilai Mata Kuliah (Akademik, Kurikulum dan Pembelajaran)",
    "bidang": "AKADEMIK",
    "no": 14
  },
  {
    "name": "Rapat/Sidang Akademik",
    "code": "AKD15",
    "group": "AKD",
    "classificationCode": "AKD15",
    "description": "Rapat/Sidang Akademik (Akademik, Kurikulum dan Pembelajaran)",
    "bidang": "AKADEMIK",
    "no": 15
  },
  {
    "name": "Transkrip",
    "code": "AKD16",
    "group": "AKD",
    "classificationCode": "AKD16",
    "description": "Transkrip (Akademik, Kurikulum dan Pembelajaran)",
    "bidang": "AKADEMIK",
    "no": 16
  },
  {
    "name": "Ijazah",
    "code": "AKD17",
    "group": "AKD",
    "classificationCode": "AKD17",
    "description": "Ijazah (Akademik, Kurikulum dan Pembelajaran)",
    "bidang": "AKADEMIK",
    "no": 17
  },
  {
    "name": "Wisuda",
    "code": "AKD18",
    "group": "AKD",
    "classificationCode": "AKD18",
    "description": "Wisuda (Akademik, Kurikulum dan Pembelajaran)",
    "bidang": "AKADEMIK",
    "no": 18
  },
  {
    "name": "Kalendar Akademik",
    "code": "AKD19",
    "group": "AKD",
    "classificationCode": "AKD19",
    "description": "Kalendar Akademik (Akademik, Kurikulum dan Pembelajaran)",
    "bidang": "AKADEMIK",
    "no": 19
  },
  {
    "name": "Status Mahasiswa/Surat Keterangan Lulus/Cuti Akademik",
    "code": "AKD20",
    "group": "AKD",
    "classificationCode": "AKD20",
    "description": "Status Mahasiswa/Surat Keterangan Lulus/Cuti Akademik (Akademik, Kurikulum dan Pembelajaran)",
    "bidang": "AKADEMIK",
    "no": 20
  },
  {
    "name": "Pendaftaran Ulang",
    "code": "AKD21",
    "group": "AKD",
    "classificationCode": "AKD21",
    "description": "Pendaftaran Ulang (Akademik, Kurikulum dan Pembelajaran)",
    "bidang": "AKADEMIK",
    "no": 21
  },
  {
    "name": "Perubahan Rencana Studi (PRS)",
    "code": "AKD22",
    "group": "AKD",
    "classificationCode": "AKD22",
    "description": "Perubahan Rencana Studi (PRS) (Akademik, Kurikulum dan Pembelajaran)",
    "bidang": "AKADEMIK",
    "no": 22
  },
  {
    "name": "Perwalian dan Bimbingan",
    "code": "AKD23",
    "group": "AKD",
    "classificationCode": "AKD23",
    "description": "Perwalian dan Bimbingan (Akademik, Kurikulum dan Pembelajaran)",
    "bidang": "AKADEMIK",
    "no": 23
  },
  {
    "name": "Dispensasi",
    "code": "AKD24",
    "group": "AKD",
    "classificationCode": "AKD24",
    "description": "Dispensasi (Akademik, Kurikulum dan Pembelajaran)",
    "bidang": "AKADEMIK",
    "no": 24
  },
  {
    "name": "Lulusan Berprestasi",
    "code": "AKD25",
    "group": "AKD",
    "classificationCode": "AKD25",
    "description": "Lulusan Berprestasi (Akademik, Kurikulum dan Pembelajaran)",
    "bidang": "AKADEMIK",
    "no": 25
  },
  {
    "name": "Rapat dan Koordinasi Akademik",
    "code": "AKD26",
    "group": "AKD",
    "classificationCode": "AKD26",
    "description": "Rapat dan Koordinasi Akademik (Akademik, Kurikulum dan Pembelajaran)",
    "bidang": "AKADEMIK",
    "no": 26
  },
  {
    "name": "Studi Banding/Kunjungan Industri",
    "code": "AKD27",
    "group": "AKD",
    "classificationCode": "AKD27",
    "description": "Studi Banding/Kunjungan Industri (Akademik, Kurikulum dan Pembelajaran)",
    "bidang": "AKADEMIK",
    "no": 27
  },
  {
    "name": "Laporan",
    "code": "AKD28",
    "group": "AKD",
    "classificationCode": "AKD28",
    "description": "Laporan (Akademik, Kurikulum dan Pembelajaran)",
    "bidang": "AKADEMIK",
    "no": 28
  },
  {
    "name": "Umum",
    "code": "LIB01",
    "group": "LIB",
    "classificationCode": "LIB01",
    "description": "Umum (Perpustakaan dan Bahan Pustaka)",
    "bidang": "PERPUSTAKAAN",
    "no": 1
  },
  {
    "name": "Koleksi dan Bahan Pustaka",
    "code": "LIB02",
    "group": "LIB",
    "classificationCode": "LIB02",
    "description": "Koleksi dan Bahan Pustaka (Perpustakaan dan Bahan Pustaka)",
    "bidang": "PERPUSTAKAAN",
    "no": 2
  },
  {
    "name": "Layanan Pustaka",
    "code": "LIB03",
    "group": "LIB",
    "classificationCode": "LIB03",
    "description": "Layanan Pustaka (Perpustakaan dan Bahan Pustaka)",
    "bidang": "PERPUSTAKAAN",
    "no": 3
  },
  {
    "name": "Umum",
    "code": "PSL01",
    "group": "PSL",
    "classificationCode": "PSL01",
    "description": "Umum (Pasca Sarjana, CeLoE dan Pembelajaran Terbuka)",
    "bidang": "PASCA SARJANA & ADVANCED LEARNING",
    "no": 1
  },
  {
    "name": "Layanan CeLoE",
    "code": "PSL02",
    "group": "PSL",
    "classificationCode": "PSL02",
    "description": "Layanan CeLoE (Pasca Sarjana, CeLoE dan Pembelajaran Terbuka)",
    "bidang": "PASCA SARJANA & ADVANCED LEARNING",
    "no": 2
  },
  {
    "name": "Pengembangan CeLoE",
    "code": "PSL03",
    "group": "PSL",
    "classificationCode": "PSL03",
    "description": "Pengembangan CeLoE (Pasca Sarjana, CeLoE dan Pembelajaran Terbuka)",
    "bidang": "PASCA SARJANA & ADVANCED LEARNING",
    "no": 3
  },
  {
    "name": "Pendidikan Jarak Jauh",
    "code": "PSL04",
    "group": "PSL",
    "classificationCode": "PSL04",
    "description": "Pendidikan Jarak Jauh (Pasca Sarjana, CeLoE dan Pembelajaran Terbuka)",
    "bidang": "PASCA SARJANA & ADVANCED LEARNING",
    "no": 4
  },
  {
    "name": "Pengelolaan Pasca Sarjana",
    "code": "PSL05",
    "group": "PSL",
    "classificationCode": "PSL05",
    "description": "Pengelolaan Pasca Sarjana (Pasca Sarjana, CeLoE dan Pembelajaran Terbuka)",
    "bidang": "PASCA SARJANA & ADVANCED LEARNING",
    "no": 5
  },
  {
    "name": "Kelas Internasional",
    "code": "PSL06",
    "group": "PSL",
    "classificationCode": "PSL06",
    "description": "Kelas Internasional (Pasca Sarjana, CeLoE dan Pembelajaran Terbuka)",
    "bidang": "PASCA SARJANA & ADVANCED LEARNING",
    "no": 6
  },
  {
    "name": "Umum",
    "code": "LAC01",
    "group": "LAC",
    "classificationCode": "LAC01",
    "description": "Umum (Pusat Bahasa dan Sertifikasi Bahasa)",
    "bidang": "PUSAT BAHASA",
    "no": 1
  },
  {
    "name": "Layanan Bahasa",
    "code": "LAC02",
    "group": "LAC",
    "classificationCode": "LAC02",
    "description": "Layanan Bahasa (Pusat Bahasa dan Sertifikasi Bahasa)",
    "bidang": "PUSAT BAHASA",
    "no": 2
  },
  {
    "name": "Kolaborasi Eksternal",
    "code": "LAC03",
    "group": "LAC",
    "classificationCode": "LAC03",
    "description": "Kolaborasi Eksternal (Pusat Bahasa dan Sertifikasi Bahasa)",
    "bidang": "PUSAT BAHASA",
    "no": 3
  },
  {
    "name": "Sertifikat Kompetensi Bahasa",
    "code": "LAC04",
    "group": "LAC",
    "classificationCode": "LAC04",
    "description": "Sertifikat Kompetensi Bahasa (Pusat Bahasa dan Sertifikasi Bahasa)",
    "bidang": "PUSAT BAHASA",
    "no": 4
  },
  {
    "name": "Laporan",
    "code": "LAC05",
    "group": "LAC",
    "classificationCode": "LAC05",
    "description": "Laporan (Pusat Bahasa dan Sertifikasi Bahasa)",
    "bidang": "PUSAT BAHASA",
    "no": 5
  },
  {
    "name": "Umum",
    "code": "AST01",
    "group": "AST",
    "classificationCode": "AST01",
    "description": "Umum (Aset, Logistik dan Pengadaan)",
    "bidang": "ASET DAN SUSTAINABILITY",
    "no": 1
  },
  {
    "name": "Permintaan Barang/ Jasa",
    "code": "AST02",
    "group": "AST",
    "classificationCode": "AST02",
    "description": "Permintaan Barang/ Jasa (Aset, Logistik dan Pengadaan)",
    "bidang": "ASET DAN SUSTAINABILITY",
    "no": 2
  },
  {
    "name": "Justifikasi Kebutuhan",
    "code": "AST03",
    "group": "AST",
    "classificationCode": "AST03",
    "description": "Justifikasi Kebutuhan (Aset, Logistik dan Pengadaan)",
    "bidang": "ASET DAN SUSTAINABILITY",
    "no": 3
  },
  {
    "name": "Justifikasi Pengadaan",
    "code": "AST04",
    "group": "AST",
    "classificationCode": "AST04",
    "description": "Justifikasi Pengadaan (Aset, Logistik dan Pengadaan)",
    "bidang": "ASET DAN SUSTAINABILITY",
    "no": 4
  },
  {
    "name": "Harga Standar dan Perkiraan",
    "code": "AST05",
    "group": "AST",
    "classificationCode": "AST05",
    "description": "Harga Standar dan Perkiraan (Aset, Logistik dan Pengadaan)",
    "bidang": "ASET DAN SUSTAINABILITY",
    "no": 5
  },
  {
    "name": "Surat Permintaan Penawaran Harga",
    "code": "AST06",
    "group": "AST",
    "classificationCode": "AST06",
    "description": "Surat Permintaan Penawaran Harga (Aset, Logistik dan Pengadaan)",
    "bidang": "ASET DAN SUSTAINABILITY",
    "no": 6
  },
  {
    "name": "Surat Penawaran Harga",
    "code": "AST07",
    "group": "AST",
    "classificationCode": "AST07",
    "description": "Surat Penawaran Harga (Aset, Logistik dan Pengadaan)",
    "bidang": "ASET DAN SUSTAINABILITY",
    "no": 7
  },
  {
    "name": "Negosiasi dan Tender/Lelang",
    "code": "AST08",
    "group": "AST",
    "classificationCode": "AST08",
    "description": "Negosiasi dan Tender/Lelang (Aset, Logistik dan Pengadaan)",
    "bidang": "ASET DAN SUSTAINABILITY",
    "no": 8
  },
  {
    "name": "Penetapan Pemenang",
    "code": "AST09",
    "group": "AST",
    "classificationCode": "AST09",
    "description": "Penetapan Pemenang (Aset, Logistik dan Pengadaan)",
    "bidang": "ASET DAN SUSTAINABILITY",
    "no": 9
  },
  {
    "name": "Penunjukan/Pembelian Langsung",
    "code": "AST10",
    "group": "AST",
    "classificationCode": "AST10",
    "description": "Penunjukan/Pembelian Langsung (Aset, Logistik dan Pengadaan)",
    "bidang": "ASET DAN SUSTAINABILITY",
    "no": 10
  },
  {
    "name": "Surat Penunjukan Kerja",
    "code": "AST11",
    "group": "AST",
    "classificationCode": "AST11",
    "description": "Surat Penunjukan Kerja (Aset, Logistik dan Pengadaan)",
    "bidang": "ASET DAN SUSTAINABILITY",
    "no": 11
  },
  {
    "name": "Berita Acara Uji Terima dan Pemeriksaan",
    "code": "AST12",
    "group": "AST",
    "classificationCode": "AST12",
    "description": "Berita Acara Uji Terima dan Pemeriksaan (Aset, Logistik dan Pengadaan)",
    "bidang": "ASET DAN SUSTAINABILITY",
    "no": 12
  },
  {
    "name": "Berita Acara Serah Terima",
    "code": "AST13",
    "group": "AST",
    "classificationCode": "AST13",
    "description": "Berita Acara Serah Terima (Aset, Logistik dan Pengadaan)",
    "bidang": "ASET DAN SUSTAINABILITY",
    "no": 13
  },
  {
    "name": "Surat Tugas Logistik",
    "code": "AST14",
    "group": "AST",
    "classificationCode": "AST14",
    "description": "Surat Tugas Logistik (Aset, Logistik dan Pengadaan)",
    "bidang": "ASET DAN SUSTAINABILITY",
    "no": 14
  },
  {
    "name": "Pergudangan",
    "code": "AST15",
    "group": "AST",
    "classificationCode": "AST15",
    "description": "Pergudangan (Aset, Logistik dan Pengadaan)",
    "bidang": "ASET DAN SUSTAINABILITY",
    "no": 15
  },
  {
    "name": "Distribusi/Pengiriman",
    "code": "AST16",
    "group": "AST",
    "classificationCode": "AST16",
    "description": "Distribusi/Pengiriman (Aset, Logistik dan Pengadaan)",
    "bidang": "ASET DAN SUSTAINABILITY",
    "no": 16
  },
  {
    "name": "Peminjaman Aset",
    "code": "AST17",
    "group": "AST",
    "classificationCode": "AST17",
    "description": "Peminjaman Aset (Aset, Logistik dan Pengadaan)",
    "bidang": "ASET DAN SUSTAINABILITY",
    "no": 17
  },
  {
    "name": "Peminjaman Ruangan",
    "code": "AST18",
    "group": "AST",
    "classificationCode": "AST18",
    "description": "Peminjaman Ruangan (Aset, Logistik dan Pengadaan)",
    "bidang": "ASET DAN SUSTAINABILITY",
    "no": 18
  },
  {
    "name": "Pemanfaatan aset",
    "code": "AST19",
    "group": "AST",
    "classificationCode": "AST19",
    "description": "Pemanfaatan aset (Aset, Logistik dan Pengadaan)",
    "bidang": "ASET DAN SUSTAINABILITY",
    "no": 19
  },
  {
    "name": "Pemeliharaan Aset",
    "code": "AST20",
    "group": "AST",
    "classificationCode": "AST20",
    "description": "Pemeliharaan Aset (Aset, Logistik dan Pengadaan)",
    "bidang": "ASET DAN SUSTAINABILITY",
    "no": 20
  },
  {
    "name": "Mutasi & Penghapusan Aset",
    "code": "AST21",
    "group": "AST",
    "classificationCode": "AST21",
    "description": "Mutasi & Penghapusan Aset (Aset, Logistik dan Pengadaan)",
    "bidang": "ASET DAN SUSTAINABILITY",
    "no": 21
  },
  {
    "name": "Kodifikasi Data Aset",
    "code": "AST22",
    "group": "AST",
    "classificationCode": "AST22",
    "description": "Kodifikasi Data Aset (Aset, Logistik dan Pengadaan)",
    "bidang": "ASET DAN SUSTAINABILITY",
    "no": 22
  },
  {
    "name": "Pengelolaan Bukti Kepemilikan Aset",
    "code": "AST23",
    "group": "AST",
    "classificationCode": "AST23",
    "description": "Pengelolaan Bukti Kepemilikan Aset (Aset, Logistik dan Pengadaan)",
    "bidang": "ASET DAN SUSTAINABILITY",
    "no": 23
  },
  {
    "name": "Persediaan Aset",
    "code": "AST24",
    "group": "AST",
    "classificationCode": "AST24",
    "description": "Persediaan Aset (Aset, Logistik dan Pengadaan)",
    "bidang": "ASET DAN SUSTAINABILITY",
    "no": 24
  },
  {
    "name": "Pemeriksaan/lnventarisasi Aset",
    "code": "AST25",
    "group": "AST",
    "classificationCode": "AST25",
    "description": "Pemeriksaan/lnventarisasi Aset (Aset, Logistik dan Pengadaan)",
    "bidang": "ASET DAN SUSTAINABILITY",
    "no": 25
  },
  {
    "name": "Laporan Inventarisasi Aset",
    "code": "AST26",
    "group": "AST",
    "classificationCode": "AST26",
    "description": "Laporan Inventarisasi Aset (Aset, Logistik dan Pengadaan)",
    "bidang": "ASET DAN SUSTAINABILITY",
    "no": 26
  },
  {
    "name": "Umum",
    "code": "KUG01",
    "group": "KUG",
    "classificationCode": "KUG01",
    "description": "Umum (Keuangan, Anggaran dan Perbendaharaan)",
    "bidang": "KEUANGAN",
    "no": 1
  },
  {
    "name": "Administrasi Keuangan",
    "code": "KUG02",
    "group": "KUG",
    "classificationCode": "KUG02",
    "description": "Administrasi Keuangan (Keuangan, Anggaran dan Perbendaharaan)",
    "bidang": "KEUANGAN",
    "no": 2
  },
  {
    "name": "Pelaporan",
    "code": "KUG03",
    "group": "KUG",
    "classificationCode": "KUG03",
    "description": "Pelaporan (Keuangan, Anggaran dan Perbendaharaan)",
    "bidang": "KEUANGAN",
    "no": 3
  },
  {
    "name": "Perbankan",
    "code": "KUG04",
    "group": "KUG",
    "classificationCode": "KUG04",
    "description": "Perbankan (Keuangan, Anggaran dan Perbendaharaan)",
    "bidang": "KEUANGAN",
    "no": 4
  },
  {
    "name": "Anggaran",
    "code": "KUG05",
    "group": "KUG",
    "classificationCode": "KUG05",
    "description": "Anggaran (Keuangan, Anggaran dan Perbendaharaan)",
    "bidang": "KEUANGAN",
    "no": 5
  },
  {
    "name": "Perbendaharaan",
    "code": "KUG06",
    "group": "KUG",
    "classificationCode": "KUG06",
    "description": "Perbendaharaan (Keuangan, Anggaran dan Perbendaharaan)",
    "bidang": "KEUANGAN",
    "no": 6
  },
  {
    "name": "Pendapatan",
    "code": "KUG07",
    "group": "KUG",
    "classificationCode": "KUG07",
    "description": "Pendapatan (Keuangan, Anggaran dan Perbendaharaan)",
    "bidang": "KEUANGAN",
    "no": 7
  },
  {
    "name": "Pembayaran / Pembiayaan",
    "code": "KUG08",
    "group": "KUG",
    "classificationCode": "KUG08",
    "description": "Pembayaran / Pembiayaan (Keuangan, Anggaran dan Perbendaharaan)",
    "bidang": "KEUANGAN",
    "no": 8
  },
  {
    "name": "Akuntansi",
    "code": "KUG09",
    "group": "KUG",
    "classificationCode": "KUG09",
    "description": "Akuntansi (Keuangan, Anggaran dan Perbendaharaan)",
    "bidang": "KEUANGAN",
    "no": 9
  },
  {
    "name": "Perpajakan",
    "code": "KUG10",
    "group": "KUG",
    "classificationCode": "KUG10",
    "description": "Perpajakan (Keuangan, Anggaran dan Perbendaharaan)",
    "bidang": "KEUANGAN",
    "no": 10
  },
  {
    "name": "Sistem Keuangan",
    "code": "KUG11",
    "group": "KUG",
    "classificationCode": "KUG11",
    "description": "Sistem Keuangan (Keuangan, Anggaran dan Perbendaharaan)",
    "bidang": "KEUANGAN",
    "no": 11
  },
  {
    "name": "Audit",
    "code": "KUG12",
    "group": "KUG",
    "classificationCode": "KUG12",
    "description": "Audit (Keuangan, Anggaran dan Perbendaharaan)",
    "bidang": "KEUANGAN",
    "no": 12
  },
  {
    "name": "Bisnis Proses Keuangan",
    "code": "KUG13",
    "group": "KUG",
    "classificationCode": "KUG13",
    "description": "Bisnis Proses Keuangan (Keuangan, Anggaran dan Perbendaharaan)",
    "bidang": "KEUANGAN",
    "no": 13
  },
  {
    "name": "Bisnis Analisis",
    "code": "KUG14",
    "group": "KUG",
    "classificationCode": "KUG14",
    "description": "Bisnis Analisis (Keuangan, Anggaran dan Perbendaharaan)",
    "bidang": "KEUANGAN",
    "no": 14
  },
  {
    "name": "Standar Tarif",
    "code": "KUG15",
    "group": "KUG",
    "classificationCode": "KUG15",
    "description": "Standar Tarif (Keuangan, Anggaran dan Perbendaharaan)",
    "bidang": "KEUANGAN",
    "no": 15
  },
  {
    "name": "Umum",
    "code": "SDM01",
    "group": "SDM",
    "classificationCode": "SDM01",
    "description": "Umum (Sumber Daya Manusia dan Kepegawaian)",
    "bidang": "SUMBER DAYA MANUSIA",
    "no": 1
  },
  {
    "name": "Perencanaan SDM",
    "code": "SDM02",
    "group": "SDM",
    "classificationCode": "SDM02",
    "description": "Perencanaan SDM (Sumber Daya Manusia dan Kepegawaian)",
    "bidang": "SUMBER DAYA MANUSIA",
    "no": 2
  },
  {
    "name": "Rekrutasi",
    "code": "SDM03",
    "group": "SDM",
    "classificationCode": "SDM03",
    "description": "Rekrutasi (Sumber Daya Manusia dan Kepegawaian)",
    "bidang": "SUMBER DAYA MANUSIA",
    "no": 3
  },
  {
    "name": "Pengembangan Karir",
    "code": "SDM04",
    "group": "SDM",
    "classificationCode": "SDM04",
    "description": "Pengembangan Karir (Sumber Daya Manusia dan Kepegawaian)",
    "bidang": "SUMBER DAYA MANUSIA",
    "no": 4
  },
  {
    "name": "Studi Lanjut",
    "code": "SDM05",
    "group": "SDM",
    "classificationCode": "SDM05",
    "description": "Studi Lanjut (Sumber Daya Manusia dan Kepegawaian)",
    "bidang": "SUMBER DAYA MANUSIA",
    "no": 5
  },
  {
    "name": "Training dan Sertifikasi",
    "code": "SDM06",
    "group": "SDM",
    "classificationCode": "SDM06",
    "description": "Training dan Sertifikasi (Sumber Daya Manusia dan Kepegawaian)",
    "bidang": "SUMBER DAYA MANUSIA",
    "no": 6
  },
  {
    "name": "Data SDM",
    "code": "SDM07",
    "group": "SDM",
    "classificationCode": "SDM07",
    "description": "Data SDM (Sumber Daya Manusia dan Kepegawaian)",
    "bidang": "SUMBER DAYA MANUSIA",
    "no": 7
  },
  {
    "name": "Budaya Organisasi",
    "code": "SDM08",
    "group": "SDM",
    "classificationCode": "SDM08",
    "description": "Budaya Organisasi (Sumber Daya Manusia dan Kepegawaian)",
    "bidang": "SUMBER DAYA MANUSIA",
    "no": 8
  },
  {
    "name": "Performansi Pegawai",
    "code": "SDM09",
    "group": "SDM",
    "classificationCode": "SDM09",
    "description": "Performansi Pegawai (Sumber Daya Manusia dan Kepegawaian)",
    "bidang": "SUMBER DAYA MANUSIA",
    "no": 9
  },
  {
    "name": "Kompensasi dan Benefit",
    "code": "SDM10",
    "group": "SDM",
    "classificationCode": "SDM10",
    "description": "Kompensasi dan Benefit (Sumber Daya Manusia dan Kepegawaian)",
    "bidang": "SUMBER DAYA MANUSIA",
    "no": 10
  },
  {
    "name": "Perjalanan Dinas",
    "code": "SDM11",
    "group": "SDM",
    "classificationCode": "SDM11",
    "description": "Perjalanan Dinas (Sumber Daya Manusia dan Kepegawaian)",
    "bidang": "SUMBER DAYA MANUSIA",
    "no": 11
  },
  {
    "name": "Cuti Pegawai",
    "code": "SDM12",
    "group": "SDM",
    "classificationCode": "SDM12",
    "description": "Cuti Pegawai (Sumber Daya Manusia dan Kepegawaian)",
    "bidang": "SUMBER DAYA MANUSIA",
    "no": 12
  },
  {
    "name": "Beasiswa Pegawai",
    "code": "SDM13",
    "group": "SDM",
    "classificationCode": "SDM13",
    "description": "Beasiswa Pegawai (Sumber Daya Manusia dan Kepegawaian)",
    "bidang": "SUMBER DAYA MANUSIA",
    "no": 13
  },
  {
    "name": "Kinerja Pegawai",
    "code": "SDM14",
    "group": "SDM",
    "classificationCode": "SDM14",
    "description": "Kinerja Pegawai (Sumber Daya Manusia dan Kepegawaian)",
    "bidang": "SUMBER DAYA MANUSIA",
    "no": 14
  },
  {
    "name": "Pemberhentian Pegawai",
    "code": "SDM15",
    "group": "SDM",
    "classificationCode": "SDM15",
    "description": "Pemberhentian Pegawai (Sumber Daya Manusia dan Kepegawaian)",
    "bidang": "SUMBER DAYA MANUSIA",
    "no": 15
  },
  {
    "name": "Bantuan Sosial dan Kesejahteraan Lainnya",
    "code": "SDM16",
    "group": "SDM",
    "classificationCode": "SDM16",
    "description": "Bantuan Sosial dan Kesejahteraan Lainnya (Sumber Daya Manusia dan Kepegawaian)",
    "bidang": "SUMBER DAYA MANUSIA",
    "no": 16
  },
  {
    "name": "Penghargaan Pegawai",
    "code": "SDM17",
    "group": "SDM",
    "classificationCode": "SDM17",
    "description": "Penghargaan Pegawai (Sumber Daya Manusia dan Kepegawaian)",
    "bidang": "SUMBER DAYA MANUSIA",
    "no": 17
  },
  {
    "name": "Pelanggaran Disiplin",
    "code": "SDM18",
    "group": "SDM",
    "classificationCode": "SDM18",
    "description": "Pelanggaran Disiplin (Sumber Daya Manusia dan Kepegawaian)",
    "bidang": "SUMBER DAYA MANUSIA",
    "no": 18
  },
  {
    "name": "Dengar Keterangan",
    "code": "SDM19",
    "group": "SDM",
    "classificationCode": "SDM19",
    "description": "Dengar Keterangan (Sumber Daya Manusia dan Kepegawaian)",
    "bidang": "SUMBER DAYA MANUSIA",
    "no": 19
  },
  {
    "name": "Tindakan Administrasi",
    "code": "SDM20",
    "group": "SDM",
    "classificationCode": "SDM20",
    "description": "Tindakan Administrasi (Sumber Daya Manusia dan Kepegawaian)",
    "bidang": "SUMBER DAYA MANUSIA",
    "no": 20
  },
  {
    "name": "Laporan",
    "code": "SDM21",
    "group": "SDM",
    "classificationCode": "SDM21",
    "description": "Laporan (Sumber Daya Manusia dan Kepegawaian)",
    "bidang": "SUMBER DAYA MANUSIA",
    "no": 21
  },
  {
    "name": "Umum",
    "code": "PAD01",
    "group": "PAD",
    "classificationCode": "PAD01",
    "description": "Umum (Pemasaran dan Admisi (PMB))",
    "bidang": "PEMASARAN & ADMISI",
    "no": 1
  },
  {
    "name": "Kegiatan Pemasaran",
    "code": "PAD02",
    "group": "PAD",
    "classificationCode": "PAD02",
    "description": "Kegiatan Pemasaran (Pemasaran dan Admisi (PMB))",
    "bidang": "PEMASARAN & ADMISI",
    "no": 2
  },
  {
    "name": "Media Pemasaran",
    "code": "PAD03",
    "group": "PAD",
    "classificationCode": "PAD03",
    "description": "Media Pemasaran (Pemasaran dan Admisi (PMB))",
    "bidang": "PEMASARAN & ADMISI",
    "no": 3
  },
  {
    "name": "Tim Pemasaran",
    "code": "PAD04",
    "group": "PAD",
    "classificationCode": "PAD04",
    "description": "Tim Pemasaran (Pemasaran dan Admisi (PMB))",
    "bidang": "PEMASARAN & ADMISI",
    "no": 4
  },
  {
    "name": "Riset dan Analisis Pemasaran",
    "code": "PAD05",
    "group": "PAD",
    "classificationCode": "PAD05",
    "description": "Riset dan Analisis Pemasaran (Pemasaran dan Admisi (PMB))",
    "bidang": "PEMASARAN & ADMISI",
    "no": 5
  },
  {
    "name": "Kerjasama Pemasaran",
    "code": "PAD06",
    "group": "PAD",
    "classificationCode": "PAD06",
    "description": "Kerjasama Pemasaran (Pemasaran dan Admisi (PMB))",
    "bidang": "PEMASARAN & ADMISI",
    "no": 6
  },
  {
    "name": "Laporan",
    "code": "PAD07",
    "group": "PAD",
    "classificationCode": "PAD07",
    "description": "Laporan (Pemasaran dan Admisi (PMB))",
    "bidang": "PEMASARAN & ADMISI",
    "no": 7
  },
  {
    "name": "Umum",
    "code": "KMH01",
    "group": "KMH",
    "classificationCode": "KMH01",
    "description": "Umum (Kemahasiswaan, Ormawa dan Karakter)",
    "bidang": "KEMAHASISWAAN",
    "no": 1
  },
  {
    "name": "Penghargaan Mahasiswa",
    "code": "KMH02",
    "group": "KMH",
    "classificationCode": "KMH02",
    "description": "Penghargaan Mahasiswa (Kemahasiswaan, Ormawa dan Karakter)",
    "bidang": "KEMAHASISWAAN",
    "no": 2
  },
  {
    "name": "Komisi Displin Mahasiswa",
    "code": "KMH03",
    "group": "KMH",
    "classificationCode": "KMH03",
    "description": "Komisi Displin Mahasiswa (Kemahasiswaan, Ormawa dan Karakter)",
    "bidang": "KEMAHASISWAAN",
    "no": 3
  },
  {
    "name": "Kompetisi Mahasiswa",
    "code": "KMH04",
    "group": "KMH",
    "classificationCode": "KMH04",
    "description": "Kompetisi Mahasiswa (Kemahasiswaan, Ormawa dan Karakter)",
    "bidang": "KEMAHASISWAAN",
    "no": 4
  },
  {
    "name": "Pendidikan dan Pelatihan Mahasiswa",
    "code": "KMH05",
    "group": "KMH",
    "classificationCode": "KMH05",
    "description": "Pendidikan dan Pelatihan Mahasiswa (Kemahasiswaan, Ormawa dan Karakter)",
    "bidang": "KEMAHASISWAAN",
    "no": 5
  },
  {
    "name": "Pembinaan Karakter",
    "code": "KMH06",
    "group": "KMH",
    "classificationCode": "KMH06",
    "description": "Pembinaan Karakter (Kemahasiswaan, Ormawa dan Karakter)",
    "bidang": "KEMAHASISWAAN",
    "no": 6
  },
  {
    "name": "Konseling Mahasiswa",
    "code": "KMH07",
    "group": "KMH",
    "classificationCode": "KMH07",
    "description": "Konseling Mahasiswa (Kemahasiswaan, Ormawa dan Karakter)",
    "bidang": "KEMAHASISWAAN",
    "no": 7
  },
  {
    "name": "Kegiatan Mahasiswa",
    "code": "KMH08",
    "group": "KMH",
    "classificationCode": "KMH08",
    "description": "Kegiatan Mahasiswa (Kemahasiswaan, Ormawa dan Karakter)",
    "bidang": "KEMAHASISWAAN",
    "no": 8
  },
  {
    "name": "Organisasi Mahasiswa",
    "code": "KMH09",
    "group": "KMH",
    "classificationCode": "KMH09",
    "description": "Organisasi Mahasiswa (Kemahasiswaan, Ormawa dan Karakter)",
    "bidang": "KEMAHASISWAAN",
    "no": 9
  },
  {
    "name": "Orientasi Mahasiswa Baru",
    "code": "KMH10",
    "group": "KMH",
    "classificationCode": "KMH10",
    "description": "Orientasi Mahasiswa Baru (Kemahasiswaan, Ormawa dan Karakter)",
    "bidang": "KEMAHASISWAAN",
    "no": 10
  },
  {
    "name": "Ikatan Orangtua Mahasiswa (IOM)",
    "code": "KMH11",
    "group": "KMH",
    "classificationCode": "KMH11",
    "description": "Ikatan Orangtua Mahasiswa (IOM) (Kemahasiswaan, Ormawa dan Karakter)",
    "bidang": "KEMAHASISWAAN",
    "no": 11
  },
  {
    "name": "Beasiswa",
    "code": "KMH12",
    "group": "KMH",
    "classificationCode": "KMH12",
    "description": "Beasiswa (Kemahasiswaan, Ormawa dan Karakter)",
    "bidang": "KEMAHASISWAAN",
    "no": 12
  },
  {
    "name": "Asrama",
    "code": "KMH13",
    "group": "KMH",
    "classificationCode": "KMH13",
    "description": "Asrama (Kemahasiswaan, Ormawa dan Karakter)",
    "bidang": "KEMAHASISWAAN",
    "no": 13
  },
  {
    "name": "Asuransi/Kesehatan Mahasiswa",
    "code": "KMH14",
    "group": "KMH",
    "classificationCode": "KMH14",
    "description": "Asuransi/Kesehatan Mahasiswa (Kemahasiswaan, Ormawa dan Karakter)",
    "bidang": "KEMAHASISWAAN",
    "no": 14
  },
  {
    "name": "Laporan",
    "code": "KMH15",
    "group": "KMH",
    "classificationCode": "KMH15",
    "description": "Laporan (Kemahasiswaan, Ormawa dan Karakter)",
    "bidang": "KEMAHASISWAAN",
    "no": 15
  },
  {
    "name": "Umum",
    "code": "CAE01",
    "group": "CAE",
    "classificationCode": "CAE01",
    "description": "Umum (Karir, Hubungan Alumni dan Endowment)",
    "bidang": "KARIR, ALUMNI, DAN ENDOWMENT",
    "no": 1
  },
  {
    "name": "Informasi dan Penyaluran Kerja",
    "code": "CAE02",
    "group": "CAE",
    "classificationCode": "CAE02",
    "description": "Informasi dan Penyaluran Kerja (Karir, Hubungan Alumni dan Endowment)",
    "bidang": "KARIR, ALUMNI, DAN ENDOWMENT",
    "no": 2
  },
  {
    "name": "Industrial Gathering",
    "code": "CAE03",
    "group": "CAE",
    "classificationCode": "CAE03",
    "description": "Industrial Gathering (Karir, Hubungan Alumni dan Endowment)",
    "bidang": "KARIR, ALUMNI, DAN ENDOWMENT",
    "no": 3
  },
  {
    "name": "Konseling Karir",
    "code": "CAE04",
    "group": "CAE",
    "classificationCode": "CAE04",
    "description": "Konseling Karir (Karir, Hubungan Alumni dan Endowment)",
    "bidang": "KARIR, ALUMNI, DAN ENDOWMENT",
    "no": 4
  },
  {
    "name": "Tracer Study",
    "code": "CAE05",
    "group": "CAE",
    "classificationCode": "CAE05",
    "description": "Tracer Study (Karir, Hubungan Alumni dan Endowment)",
    "bidang": "KARIR, ALUMNI, DAN ENDOWMENT",
    "no": 5
  },
  {
    "name": "Kerjasama Alumni Sharing & Gathering",
    "code": "CAE06",
    "group": "CAE",
    "classificationCode": "CAE06",
    "description": "Kerjasama Alumni Sharing & Gathering (Karir, Hubungan Alumni dan Endowment)",
    "bidang": "KARIR, ALUMNI, DAN ENDOWMENT",
    "no": 6
  },
  {
    "name": "Kegiatan Alumni Visit",
    "code": "CAE07",
    "group": "CAE",
    "classificationCode": "CAE07",
    "description": "Kegiatan Alumni Visit (Karir, Hubungan Alumni dan Endowment)",
    "bidang": "KARIR, ALUMNI, DAN ENDOWMENT",
    "no": 7
  },
  {
    "name": "Database Alumni",
    "code": "CAE08",
    "group": "CAE",
    "classificationCode": "CAE08",
    "description": "Database Alumni (Karir, Hubungan Alumni dan Endowment)",
    "bidang": "KARIR, ALUMNI, DAN ENDOWMENT",
    "no": 8
  },
  {
    "name": "Permohonan Donasi Endowment",
    "code": "CAE09",
    "group": "CAE",
    "classificationCode": "CAE09",
    "description": "Permohonan Donasi Endowment (Karir, Hubungan Alumni dan Endowment)",
    "bidang": "KARIR, ALUMNI, DAN ENDOWMENT",
    "no": 9
  },
  {
    "name": "Permohonan Kerjasama Endowment",
    "code": "CAE10",
    "group": "CAE",
    "classificationCode": "CAE10",
    "description": "Permohonan Kerjasama Endowment (Karir, Hubungan Alumni dan Endowment)",
    "bidang": "KARIR, ALUMNI, DAN ENDOWMENT",
    "no": 10
  },
  {
    "name": "Umum",
    "code": "LIT01",
    "group": "LIT",
    "classificationCode": "LIT01",
    "description": "Umum (Penelitian dan Publikasi Ilmiah)",
    "bidang": "PENELITIAN",
    "no": 1
  },
  {
    "name": "Rencana Induk Penelitian",
    "code": "LIT02",
    "group": "LIT",
    "classificationCode": "LIT02",
    "description": "Rencana Induk Penelitian (Penelitian dan Publikasi Ilmiah)",
    "bidang": "PENELITIAN",
    "no": 2
  },
  {
    "name": "Perencanaan Penelitian",
    "code": "LIT03",
    "group": "LIT",
    "classificationCode": "LIT03",
    "description": "Perencanaan Penelitian (Penelitian dan Publikasi Ilmiah)",
    "bidang": "PENELITIAN",
    "no": 3
  },
  {
    "name": "Kerjasama Penelitian",
    "code": "LIT04",
    "group": "LIT",
    "classificationCode": "LIT04",
    "description": "Kerjasama Penelitian (Penelitian dan Publikasi Ilmiah)",
    "bidang": "PENELITIAN",
    "no": 4
  },
  {
    "name": "Pelaksanaan & Laporan Penelitian",
    "code": "LIT05",
    "group": "LIT",
    "classificationCode": "LIT05",
    "description": "Pelaksanaan & Laporan Penelitian (Penelitian dan Publikasi Ilmiah)",
    "bidang": "PENELITIAN",
    "no": 5
  },
  {
    "name": "Penelitian Internal",
    "code": "LIT06",
    "group": "LIT",
    "classificationCode": "LIT06",
    "description": "Penelitian Internal (Penelitian dan Publikasi Ilmiah)",
    "bidang": "PENELITIAN",
    "no": 6
  },
  {
    "name": "Penelitian Eksternal",
    "code": "LIT07",
    "group": "LIT",
    "classificationCode": "LIT07",
    "description": "Penelitian Eksternal (Penelitian dan Publikasi Ilmiah)",
    "bidang": "PENELITIAN",
    "no": 7
  },
  {
    "name": "Publikasi Hasil Penelitian",
    "code": "LIT08",
    "group": "LIT",
    "classificationCode": "LIT08",
    "description": "Publikasi Hasil Penelitian (Penelitian dan Publikasi Ilmiah)",
    "bidang": "PENELITIAN",
    "no": 8
  },
  {
    "name": "Konferensi",
    "code": "LIT09",
    "group": "LIT",
    "classificationCode": "LIT09",
    "description": "Konferensi (Penelitian dan Publikasi Ilmiah)",
    "bidang": "PENELITIAN",
    "no": 9
  },
  {
    "name": "Laporan",
    "code": "LIT10",
    "group": "LIT",
    "classificationCode": "LIT10",
    "description": "Laporan (Penelitian dan Publikasi Ilmiah)",
    "bidang": "PENELITIAN",
    "no": 10
  },
  {
    "name": "Umum",
    "code": "ABD01",
    "group": "ABD",
    "classificationCode": "ABD01",
    "description": "Umum (Pengabdian kepada Masyarakat (Abdimas))",
    "bidang": "PENGABDIAN MASYARAKAT",
    "no": 1
  },
  {
    "name": "Perencanaan Pengabdian Masyarakat",
    "code": "ABD02",
    "group": "ABD",
    "classificationCode": "ABD02",
    "description": "Perencanaan Pengabdian Masyarakat (Pengabdian kepada Masyarakat (Abdimas))",
    "bidang": "PENGABDIAN MASYARAKAT",
    "no": 2
  },
  {
    "name": "Kerjasama Pengabdian Masyarakat",
    "code": "ABD03",
    "group": "ABD",
    "classificationCode": "ABD03",
    "description": "Kerjasama Pengabdian Masyarakat (Pengabdian kepada Masyarakat (Abdimas))",
    "bidang": "PENGABDIAN MASYARAKAT",
    "no": 3
  },
  {
    "name": "Pengabdian Masyarakat Internal",
    "code": "ABD04",
    "group": "ABD",
    "classificationCode": "ABD04",
    "description": "Pengabdian Masyarakat Internal (Pengabdian kepada Masyarakat (Abdimas))",
    "bidang": "PENGABDIAN MASYARAKAT",
    "no": 4
  },
  {
    "name": "Pengabdian Masyarakat Eksternal",
    "code": "ABD05",
    "group": "ABD",
    "classificationCode": "ABD05",
    "description": "Pengabdian Masyarakat Eksternal (Pengabdian kepada Masyarakat (Abdimas))",
    "bidang": "PENGABDIAN MASYARAKAT",
    "no": 5
  },
  {
    "name": "Pelaksanaan & Laporan Pengabdian Masyarakat",
    "code": "ABD06",
    "group": "ABD",
    "classificationCode": "ABD06",
    "description": "Pelaksanaan & Laporan Pengabdian Masyarakat (Pengabdian kepada Masyarakat (Abdimas))",
    "bidang": "PENGABDIAN MASYARAKAT",
    "no": 6
  },
  {
    "name": "Umum",
    "code": "HBH01",
    "group": "HBH",
    "classificationCode": "HBH01",
    "description": "Umum (Hibah Institusi Dalam dan Luar Negeri)",
    "bidang": "HIBAH",
    "no": 1
  },
  {
    "name": "Hibah Badan Usaha Dalam Negeri",
    "code": "HBH02",
    "group": "HBH",
    "classificationCode": "HBH02",
    "description": "Hibah Badan Usaha Dalam Negeri (Hibah Institusi Dalam dan Luar Negeri)",
    "bidang": "HIBAH",
    "no": 2
  },
  {
    "name": "Hibah Badan Usaha Luar Negeri",
    "code": "HBH03",
    "group": "HBH",
    "classificationCode": "HBH03",
    "description": "Hibah Badan Usaha Luar Negeri (Hibah Institusi Dalam dan Luar Negeri)",
    "bidang": "HIBAH",
    "no": 3
  },
  {
    "name": "Hibah Perguruan Tinggi Dalam Negeri",
    "code": "HBH04",
    "group": "HBH",
    "classificationCode": "HBH04",
    "description": "Hibah Perguruan Tinggi Dalam Negeri (Hibah Institusi Dalam dan Luar Negeri)",
    "bidang": "HIBAH",
    "no": 4
  },
  {
    "name": "Hibah Perguruan Tinggi Luar Negeri",
    "code": "HBH05",
    "group": "HBH",
    "classificationCode": "HBH05",
    "description": "Hibah Perguruan Tinggi Luar Negeri (Hibah Institusi Dalam dan Luar Negeri)",
    "bidang": "HIBAH",
    "no": 5
  },
  {
    "name": "Hibah Pusat/Pemerintahan",
    "code": "HBH06",
    "group": "HBH",
    "classificationCode": "HBH06",
    "description": "Hibah Pusat/Pemerintahan (Hibah Institusi Dalam dan Luar Negeri)",
    "bidang": "HIBAH",
    "no": 6
  },
  {
    "name": "Hibah Provinsi",
    "code": "HBH07",
    "group": "HBH",
    "classificationCode": "HBH07",
    "description": "Hibah Provinsi (Hibah Institusi Dalam dan Luar Negeri)",
    "bidang": "HIBAH",
    "no": 7
  },
  {
    "name": "Hibah Kabupaten/Kota Madya",
    "code": "HBH08",
    "group": "HBH",
    "classificationCode": "HBH08",
    "description": "Hibah Kabupaten/Kota Madya (Hibah Institusi Dalam dan Luar Negeri)",
    "bidang": "HIBAH",
    "no": 8
  },
  {
    "name": "Hibah Asosiasi Dalam Negeri",
    "code": "HBH09",
    "group": "HBH",
    "classificationCode": "HBH09",
    "description": "Hibah Asosiasi Dalam Negeri (Hibah Institusi Dalam dan Luar Negeri)",
    "bidang": "HIBAH",
    "no": 9
  },
  {
    "name": "Hibah Asosiasi Luar Negeri",
    "code": "HBH10",
    "group": "HBH",
    "classificationCode": "HBH10",
    "description": "Hibah Asosiasi Luar Negeri (Hibah Institusi Dalam dan Luar Negeri)",
    "bidang": "HIBAH",
    "no": 10
  },
  {
    "name": "Hibah Media Dalam Negeri",
    "code": "HBH11",
    "group": "HBH",
    "classificationCode": "HBH11",
    "description": "Hibah Media Dalam Negeri (Hibah Institusi Dalam dan Luar Negeri)",
    "bidang": "HIBAH",
    "no": 11
  },
  {
    "name": "Hibah Media Luar Negeri",
    "code": "HBH12",
    "group": "HBH",
    "classificationCode": "HBH12",
    "description": "Hibah Media Luar Negeri (Hibah Institusi Dalam dan Luar Negeri)",
    "bidang": "HIBAH",
    "no": 12
  },
  {
    "name": "Hibah Non-Govermental Organization (NGO)",
    "code": "HBH13",
    "group": "HBH",
    "classificationCode": "HBH13",
    "description": "Hibah Non-Govermental Organization (NGO) (Hibah Institusi Dalam dan Luar Negeri)",
    "bidang": "HIBAH",
    "no": 13
  },
  {
    "name": "Umum",
    "code": "SAM01",
    "group": "SAM",
    "classificationCode": "SAM01",
    "description": "Umum (Kerjasama, Kemitraan Strategis, MoU & MoA)",
    "bidang": "KERJASAMA",
    "no": 1
  },
  {
    "name": "Penjajakan Kerjasama",
    "code": "SAM02",
    "group": "SAM",
    "classificationCode": "SAM02",
    "description": "Penjajakan Kerjasama (Kerjasama, Kemitraan Strategis, MoU & MoA)",
    "bidang": "KERJASAMA",
    "no": 2
  },
  {
    "name": "MoU (Memorandum of Understanding)",
    "code": "SAM03",
    "group": "SAM",
    "classificationCode": "SAM03",
    "description": "MoU (Memorandum of Understanding) (Kerjasama, Kemitraan Strategis, MoU & MoA)",
    "bidang": "KERJASAMA",
    "no": 3
  },
  {
    "name": "MoA (Memorandum of Agreement)",
    "code": "SAM04",
    "group": "SAM",
    "classificationCode": "SAM04",
    "description": "MoA (Memorandum of Agreement) (Kerjasama, Kemitraan Strategis, MoU & MoA)",
    "bidang": "KERJASAMA",
    "no": 4
  },
  {
    "name": "IA (Implementation Arrangement)",
    "code": "SAM05",
    "group": "SAM",
    "classificationCode": "SAM05",
    "description": "IA (Implementation Arrangement) (Kerjasama, Kemitraan Strategis, MoU & MoA)",
    "bidang": "KERJASAMA",
    "no": 5
  },
  {
    "name": "Proposal",
    "code": "SAM06",
    "group": "SAM",
    "classificationCode": "SAM06",
    "description": "Proposal (Kerjasama, Kemitraan Strategis, MoU & MoA)",
    "bidang": "KERJASAMA",
    "no": 6
  },
  {
    "name": "Laporan",
    "code": "SAM07",
    "group": "SAM",
    "classificationCode": "SAM07",
    "description": "Laporan (Kerjasama, Kemitraan Strategis, MoU & MoA)",
    "bidang": "KERJASAMA",
    "no": 7
  },
  {
    "name": "Partners Gathering",
    "code": "SAM08",
    "group": "SAM",
    "classificationCode": "SAM08",
    "description": "Partners Gathering (Kerjasama, Kemitraan Strategis, MoU & MoA)",
    "bidang": "KERJASAMA",
    "no": 8
  },
  {
    "name": "Lembaga Sertifikasi Profesi",
    "code": "LSP01",
    "group": "SAM",
    "classificationCode": "LSP01",
    "description": "Lembaga Sertifikasi Profesi (Kerjasama, Kemitraan Strategis, MoU & MoA)",
    "bidang": "KERJASAMA",
    "no": 9
  },
  {
    "name": "Training Project",
    "code": "TRN01",
    "group": "SAM",
    "classificationCode": "TRN01",
    "description": "Training Project (Kerjasama, Kemitraan Strategis, MoU & MoA)",
    "bidang": "KERJASAMA",
    "no": 10
  },
  {
    "name": "Certification Project",
    "code": "STF01",
    "group": "SAM",
    "classificationCode": "STF01",
    "description": "Certification Project (Kerjasama, Kemitraan Strategis, MoU & MoA)",
    "bidang": "KERJASAMA",
    "no": 11
  },
  {
    "name": "Telcom Infra Project",
    "code": "TIP01",
    "group": "SAM",
    "classificationCode": "TIP01",
    "description": "Telcom Infra Project (Kerjasama, Kemitraan Strategis, MoU & MoA)",
    "bidang": "KERJASAMA",
    "no": 12
  },
  {
    "name": "Advancing Business Education",
    "code": "ABE01",
    "group": "SAM",
    "classificationCode": "ABE01",
    "description": "Advancing Business Education (Kerjasama, Kemitraan Strategis, MoU & MoA)",
    "bidang": "KERJASAMA",
    "no": 13
  },
  {
    "name": "Umum",
    "code": "IOF01",
    "group": "IOF",
    "classificationCode": "IOF01",
    "description": "Umum (International Office dan Kerjasama Luar Negeri)",
    "bidang": "INTERNATIONAL OFFICE",
    "no": 1
  },
  {
    "name": "Visa",
    "code": "IOF02",
    "group": "IOF",
    "classificationCode": "IOF02",
    "description": "Visa (International Office dan Kerjasama Luar Negeri)",
    "bidang": "INTERNATIONAL OFFICE",
    "no": 2
  },
  {
    "name": "Passport",
    "code": "IOF03",
    "group": "IOF",
    "classificationCode": "IOF03",
    "description": "Passport (International Office dan Kerjasama Luar Negeri)",
    "bidang": "INTERNATIONAL OFFICE",
    "no": 3
  },
  {
    "name": "Ijin Belajar",
    "code": "IOF04",
    "group": "IOF",
    "classificationCode": "IOF04",
    "description": "Ijin Belajar (International Office dan Kerjasama Luar Negeri)",
    "bidang": "INTERNATIONAL OFFICE",
    "no": 4
  },
  {
    "name": "Ijin Tinggal",
    "code": "IOF05",
    "group": "IOF",
    "classificationCode": "IOF05",
    "description": "Ijin Tinggal (International Office dan Kerjasama Luar Negeri)",
    "bidang": "INTERNATIONAL OFFICE",
    "no": 5
  },
  {
    "name": "Inbound Mobility",
    "code": "IOF06",
    "group": "IOF",
    "classificationCode": "IOF06",
    "description": "Inbound Mobility (International Office dan Kerjasama Luar Negeri)",
    "bidang": "INTERNATIONAL OFFICE",
    "no": 6
  },
  {
    "name": "Outbound Mobility",
    "code": "IOF07",
    "group": "IOF",
    "classificationCode": "IOF07",
    "description": "Outbound Mobility (International Office dan Kerjasama Luar Negeri)",
    "bidang": "INTERNATIONAL OFFICE",
    "no": 7
  },
  {
    "name": "Umum",
    "code": "BTP01",
    "group": "BTP",
    "classificationCode": "BTP01",
    "description": "Umum (Bandung Techno Park, HAKI dan Tenant)",
    "bidang": "BANDUNG TECHNO PARK",
    "no": 1
  },
  {
    "name": "HAKI & Hak Cipta",
    "code": "BTP02",
    "group": "BTP",
    "classificationCode": "BTP02",
    "description": "HAKI & Hak Cipta (Bandung Techno Park, HAKI dan Tenant)",
    "bidang": "BANDUNG TECHNO PARK",
    "no": 2
  },
  {
    "name": "Layanan Inkubasi Bisnis",
    "code": "BTP03",
    "group": "BTP",
    "classificationCode": "BTP03",
    "description": "Layanan Inkubasi Bisnis (Bandung Techno Park, HAKI dan Tenant)",
    "bidang": "BANDUNG TECHNO PARK",
    "no": 3
  },
  {
    "name": "Proyek",
    "code": "BTP04",
    "group": "BTP",
    "classificationCode": "BTP04",
    "description": "Proyek (Bandung Techno Park, HAKI dan Tenant)",
    "bidang": "BANDUNG TECHNO PARK",
    "no": 4
  },
  {
    "name": "Laporan",
    "code": "BTP05",
    "group": "BTP",
    "classificationCode": "BTP05",
    "description": "Laporan (Bandung Techno Park, HAKI dan Tenant)",
    "bidang": "BANDUNG TECHNO PARK",
    "no": 5
  },
  {
    "name": "Form Sewa Tenant",
    "code": "TNT01",
    "group": "BTP",
    "classificationCode": "TNT01",
    "description": "Form Sewa Tenant (Bandung Techno Park, HAKI dan Tenant)",
    "bidang": "BANDUNG TECHNO PARK",
    "no": 6
  },
  {
    "name": "Pemberitahuan Jatuh Tempo Penggunaan Office Space",
    "code": "TNT02",
    "group": "BTP",
    "classificationCode": "TNT02",
    "description": "Pemberitahuan Jatuh Tempo Penggunaan Office Space (Bandung Techno Park, HAKI dan Tenant)",
    "bidang": "BANDUNG TECHNO PARK",
    "no": 7
  },
  {
    "name": "Surat Peringatan Pembayaran Tagihan",
    "code": "TNT03",
    "group": "BTP",
    "classificationCode": "TNT03",
    "description": "Surat Peringatan Pembayaran Tagihan (Bandung Techno Park, HAKI dan Tenant)",
    "bidang": "BANDUNG TECHNO PARK",
    "no": 8
  },
  {
    "name": "Berita Acara Penutupan Fasilitas Office Space",
    "code": "TNT04",
    "group": "BTP",
    "classificationCode": "TNT04",
    "description": "Berita Acara Penutupan Fasilitas Office Space (Bandung Techno Park, HAKI dan Tenant)",
    "bidang": "BANDUNG TECHNO PARK",
    "no": 9
  },
  {
    "name": "Invoice Tenant BTP",
    "code": "TNT05",
    "group": "BTP",
    "classificationCode": "TNT05",
    "description": "Invoice Tenant BTP (Bandung Techno Park, HAKI dan Tenant)",
    "bidang": "BANDUNG TECHNO PARK",
    "no": 10
  },
  {
    "name": "Proposal",
    "code": "(KODE MITRA)01",
    "group": "PRJ",
    "classificationCode": "(KODE MITRA)01",
    "description": "Proposal (Proyek Kemitraan Bandung Techno Park)",
    "bidang": "PROYEK (BTP)",
    "no": 1
  },
  {
    "name": "BoQ",
    "code": "(KODE MITRA)02",
    "group": "PRJ",
    "classificationCode": "(KODE MITRA)02",
    "description": "BoQ (Proyek Kemitraan Bandung Techno Park)",
    "bidang": "PROYEK (BTP)",
    "no": 2
  },
  {
    "name": "Berita Acara Klarifikasi dan Negosiasi Proyek",
    "code": "(KODE MITRA)03",
    "group": "PRJ",
    "classificationCode": "(KODE MITRA)03",
    "description": "Berita Acara Klarifikasi dan Negosiasi Proyek (Proyek Kemitraan Bandung Techno Park)",
    "bidang": "PROYEK (BTP)",
    "no": 3
  },
  {
    "name": "Surat Penawaran Harga Proyek",
    "code": "(KODE MITRA)04",
    "group": "PRJ",
    "classificationCode": "(KODE MITRA)04",
    "description": "Surat Penawaran Harga Proyek (Proyek Kemitraan Bandung Techno Park)",
    "bidang": "PROYEK (BTP)",
    "no": 4
  },
  {
    "name": "Surat Permintaan Penawaran Harga Proyek",
    "code": "(KODE MITRA)05",
    "group": "PRJ",
    "classificationCode": "(KODE MITRA)05",
    "description": "Surat Permintaan Penawaran Harga Proyek (Proyek Kemitraan Bandung Techno Park)",
    "bidang": "PROYEK (BTP)",
    "no": 5
  },
  {
    "name": "Purchase Order",
    "code": "(KODE MITRA)06",
    "group": "PRJ",
    "classificationCode": "(KODE MITRA)06",
    "description": "Purchase Order (Proyek Kemitraan Bandung Techno Park)",
    "bidang": "PROYEK (BTP)",
    "no": 6
  },
  {
    "name": "Surat Penunjukan Kerja/Surat Perintah Kerja",
    "code": "(KODE MITRA)07",
    "group": "PRJ",
    "classificationCode": "(KODE MITRA)07",
    "description": "Surat Penunjukan Kerja/Surat Perintah Kerja (Proyek Kemitraan Bandung Techno Park)",
    "bidang": "PROYEK (BTP)",
    "no": 7
  },
  {
    "name": "Perjanjian Kerja Sama/MoA",
    "code": "(KODE MITRA)08",
    "group": "PRJ",
    "classificationCode": "(KODE MITRA)08",
    "description": "Perjanjian Kerja Sama/MoA (Proyek Kemitraan Bandung Techno Park)",
    "bidang": "PROYEK (BTP)",
    "no": 8
  },
  {
    "name": "Surat Kesanggupan Kerja",
    "code": "(KODE MITRA)09",
    "group": "PRJ",
    "classificationCode": "(KODE MITRA)09",
    "description": "Surat Kesanggupan Kerja (Proyek Kemitraan Bandung Techno Park)",
    "bidang": "PROYEK (BTP)",
    "no": 9
  },
  {
    "name": "Form User Acceptance Test (UAT)",
    "code": "(KODE MITRA)10",
    "group": "PRJ",
    "classificationCode": "(KODE MITRA)10",
    "description": "Form User Acceptance Test (UAT) (Proyek Kemitraan Bandung Techno Park)",
    "bidang": "PROYEK (BTP)",
    "no": 10
  },
  {
    "name": "Berita Acara Uji Terima Proyek",
    "code": "(KODE MITRA)11",
    "group": "PRJ",
    "classificationCode": "(KODE MITRA)11",
    "description": "Berita Acara Uji Terima Proyek (Proyek Kemitraan Bandung Techno Park)",
    "bidang": "PROYEK (BTP)",
    "no": 11
  },
  {
    "name": "Berita Acara Serah Terima Proyek",
    "code": "(KODE MITRA)12",
    "group": "PRJ",
    "classificationCode": "(KODE MITRA)12",
    "description": "Berita Acara Serah Terima Proyek (Proyek Kemitraan Bandung Techno Park)",
    "bidang": "PROYEK (BTP)",
    "no": 12
  },
  {
    "name": "Berita Acara Pemeriksaan Produk",
    "code": "(KODE MITRA)13",
    "group": "PRJ",
    "classificationCode": "(KODE MITRA)13",
    "description": "Berita Acara Pemeriksaan Produk (Proyek Kemitraan Bandung Techno Park)",
    "bidang": "PROYEK (BTP)",
    "no": 13
  },
  {
    "name": "Invoice",
    "code": "(KODE MITRA)14",
    "group": "PRJ",
    "classificationCode": "(KODE MITRA)14",
    "description": "Invoice (Proyek Kemitraan Bandung Techno Park)",
    "bidang": "PROYEK (BTP)",
    "no": 14
  },
  {
    "name": "Faktur Pajak",
    "code": "(KODE MITRA)15",
    "group": "PRJ",
    "classificationCode": "(KODE MITRA)15",
    "description": "Faktur Pajak (Proyek Kemitraan Bandung Techno Park)",
    "bidang": "PROYEK (BTP)",
    "no": 15
  }
]

def generate_cuid():
    return 'cmt_' + uuid.uuid4().hex[:25]

def main():
    abs_db_path = os.path.abspath(DB_PATH)
    if not os.path.exists(abs_db_path):
        print(f"Database not found at {abs_db_path}!")
        return

    # 1. Backup DB
    print(f"1. Backing up database to {BACKUP_PATH}...")
    shutil.copyfile(abs_db_path, BACKUP_PATH)
    print("Backup completed.")

    # 2. Connect
    conn = sqlite3.connect(abs_db_path)
    c = conn.cursor()

    # Query existing categories
    c.execute('SELECT code, id, name FROM LetterCategory')
    existing = {row[0]: {'id': row[1], 'name': row[2]} for row in c.fetchall()}
    print(f"Existing categories in DB: {len(existing)}")

    updated_count = 0
    inserted_count = 0
    now_str = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    for cat in CATEGORIES:
        code = cat['code'].strip()
        name = cat['name'].strip()
        grp = cat['group'].strip()
        classification = cat.get('classificationCode', code)
        desc = cat.get('description', f"{name} ({grp})")

        if code in existing:
            orig_id = existing[code]['id']
            c.execute("""
                UPDATE "LetterCategory"
                SET name = ?,
                    "group" = ?,
                    classificationCode = ?,
                    description = ?,
                    updatedAt = ?
                WHERE id = ?
            """, (name, grp, classification, desc, now_str, orig_id))
            updated_count += 1
        else:
            new_id = generate_cuid()
            c.execute("""
                INSERT INTO "LetterCategory"
                (id, name, code, "group", classificationCode, description, isActive, createdAt, updatedAt)
                VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
            """, (new_id, name, code, grp, classification, desc, now_str, now_str))
            inserted_count += 1

    # 3. Clean up obsolete legacy categories in AKD that have 0 usage in LetterRequest
    OBSOLETE_AKD = ['IZIN', 'ND', 'REK', 'SK', 'SKET', 'SPENG', 'ST', 'UND']
    for obs_code in OBSOLETE_AKD:
        c.execute("""
            DELETE FROM "LetterCategory" 
            WHERE code = ? AND "group" = 'AKD' 
              AND id NOT IN (SELECT DISTINCT categoryId FROM "LetterRequest")
        """, (obs_code,))

    conn.commit()

    # 3. Verification
    c.execute('SELECT count(*) FROM LetterCategory')
    total_cats = c.fetchone()[0]
    c.execute('SELECT count(*) FROM LetterCategory WHERE isActive = 1')
    active_cats = c.fetchone()[0]

    c.execute('SELECT count(*) FROM LetterRequest WHERE categoryId NOT IN (SELECT id FROM LetterCategory)')
    broken_fk = c.fetchone()[0]

    print(f"Updated {updated_count} existing categories.")
    print(f"Inserted {inserted_count} new categories.")
    print(f"Total categories now in DB: {total_cats} (Active: {active_cats}).")
    print(f"Orphaned LetterRequest categoryId: {broken_fk} (must be 0).")

    conn.close()

    if broken_fk == 0:
        print("SUCCESS: All categories seeded with 100% data integrity!")
    else:
        print("WARNING: Broken foreign key detected! Please check.")

if __name__ == '__main__':
    main()
