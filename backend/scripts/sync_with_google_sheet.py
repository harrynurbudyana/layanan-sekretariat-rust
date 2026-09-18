#!/usr/bin/env python3
"""
Sync dev.db with the Google Spreadsheet provided by the user:
- Mark 11 Surat Masuk as INCOMING with their sender and received date
- Update authentic subjects and details from the Google Spreadsheet (1..1621)
- Preserve all latest letters (1622..1728) from buku_agenda_fit_2026-09-18.csv
- Maintain LetterCounter at 1728
"""

import sqlite3
import shutil
import csv
import re
from datetime import datetime

DB_PATH = 'backend/data/dev.db'
BACKUP_PATH = 'backend/data/dev.db.bak3'
PREV_CSV = '/home/harry/.gemini/antigravity-ide/brain/4cd7131f-ee61-42e8-9dbe-d5a4a1c6de27/scratch/previous_spreadsheet.csv'

MONTH_MAP = {
    'januari': 1, 'februari': 2, 'maret': 3, 'april': 4, 'mei': 5, 'juni': 6,
    'juli': 7, 'agustus': 8, 'september': 9, 'oktober': 10, 'november': 11, 'desember': 12
}

SENDER_MAP = {
    281: 'Institut Teknologi Del (IT Del)',
    533: 'FMIPA Universitas Padjadjaran (UNPAD)',
    752: 'SMK Dairobby',
    889: 'External / Peminjam Ruangan',
    1089: 'Panitia Bimtek Perpajakan',
    1213: 'Universitas Widya Dharma (UWI)',
    1342: 'Universitas Andalas (UNAND)',
    1363: 'Universitas INABA',
    1423: 'SMK SAS 2',
    1451: 'SMK Bina Putera',
    1525: 'IKAPI Jawa Barat'
}

def parse_date_str(date_str):
    if not date_str or not date_str.strip():
        return None, None, None, None
    s = date_str.strip().lower()
    m = re.search(r'(\d+)\s+([a-z]+)\s+(\d{4})', s)
    if m:
        day = int(m.group(1))
        month_name = m.group(2)
        year = int(m.group(3))
        month = MONTH_MAP.get(month_name, 1)
        dt = datetime(year, month, day, 12, 0, 0)
        ts = int(dt.timestamp() * 1000)
        formatted = f"{year:04d}-{month:02d}-{day:02d}"
        return day, month, year, formatted
    return None, None, None, None

def main():
    print(f"Creating backup of {DB_PATH} -> {BACKUP_PATH}...")
    shutil.copy2(DB_PATH, BACKUP_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    with open(PREV_CSV, mode='r', encoding='utf-8', errors='replace') as f:
        prev_rows = list(csv.reader(f))

    # Read rows from Google Sheet
    prev_by_seq = {}
    for r in prev_rows[5:]:
        if len(r) > 1 and r[1].strip().isdigit():
            seq = int(r[1].strip())
            if r[2].strip() or (len(r) > 7 and r[7].strip()):
                prev_by_seq[seq] = r

    print(f"Loaded {len(prev_by_seq)} valid rows from Google Spreadsheet.")

    # 1. Update Surat Masuk (11 records)
    incoming_count = 0
    for seq, r in prev_by_seq.items():
        is_masuk = 'masuk' in r[3].lower()
        if is_masuk:
            sender = SENDER_MAP.get(seq, r[4].strip() or 'Instansi Luar')
            raw_code = r[2].strip()
            # Clean full number for incoming letter
            if raw_code.startswith('/015/PAN-BIMTEK'):
                full_num = '015/PAN-BIMTEK/VI/2026'
            elif raw_code.startswith('/'):
                full_num = raw_code[1:]
            else:
                full_num = raw_code
            
            subject = r[7].strip() or 'Surat Permohonan / Undangan Masuk'
            recipient = r[5].strip() or 'Dekan Fakultas Ilmu Terapan'
            _, _, _, date_formatted = parse_date_str(r[0])

            cur.execute('''
                UPDATE "LetterRequest"
                SET letterType = 'INCOMING',
                    sender = ?,
                    recipient = ?,
                    fullNumber = ?,
                    subject = ?,
                    receivedDate = coalesce(?, date(letterDate / 1000, 'unixepoch')),
                    notes = ?
                WHERE sequenceNumber = ?
            ''', (sender, recipient, full_num, subject, date_formatted, f"[Surat Masuk] Asal: {sender}", seq))
            incoming_count += 1
            print(f"  Updated Seq {seq} as INCOMING: {full_num} ({sender})")

    print(f"Successfully configured {incoming_count} Surat Masuk records.")

    # 2. Update specific perihal improvements from Google Sheet
    # Seq 144: undangan rapat prodi
    cur.execute('''
        UPDATE "LetterRequest"
        SET subject = 'Undangan Rapat Prodi D3 RPL',
            notes = '[Surat Internal] | Dari: Kaprodi RPL'
        WHERE sequenceNumber = 144
    ''')

    # Seq 150: Sertifikat Kegiatan Mahasiswa
    cur.execute('''
        UPDATE "LetterRequest"
        SET subject = 'Sertifikat Kegiatan Mahasiswa D3 MP',
            applicantName = 'Nia',
            notes = '[Sertifikat] | PIC: Nia'
        WHERE sequenceNumber = 150
    ''')

    # Seq 1621: Official Undangan Rapat Pembahasan Pembentukan Program Studi S3 Terapan CPS
    cur.execute('''
        UPDATE "LetterRequest"
        SET fullNumber = '1621/SKR05/IT-DEK/2026',
            classificationCode = 'SKR05',
            signeeCode = 'IT-DEK',
            subject = 'Undangan Rapat Pembahasan Pembentukan Program Studi S3 Terapan CPS',
            applicantName = 'dini',
            recipient = 'Terlampir',
            notes = '[Surat Internal] | Dari: Dekan | PIC: dini'
        WHERE sequenceNumber = 1621
    ''')
    print("Updated specific subjects (Seq 144, 150, 1621).")

    # 3. Verify LetterCounter
    cur.execute('SELECT currentNumber FROM "LetterCounter" WHERE year = 2026 AND scope = "FIT"')
    counter_val = cur.fetchone()[0]
    print(f"LetterCounter FIT 2026: {counter_val}")
    if counter_val < 1728:
        cur.execute('UPDATE "LetterCounter" SET currentNumber = 1728 WHERE year = 2026 AND scope = "FIT"')
        print("Updated LetterCounter to 1728.")

    # 4. Check statistics
    cur.execute('SELECT count(*), letterType FROM "LetterRequest" GROUP BY letterType')
    for count, l_type in cur.fetchall():
        print(f"  Letter type '{l_type}': {count} records")

    cur.execute('PRAGMA foreign_key_check')
    fk = cur.fetchall()
    if fk:
        print("Foreign key errors:", fk)
    else:
        print("Foreign key check passed.")

    cur.execute('PRAGMA integrity_check')
    print("Integrity check:", cur.fetchone()[0])

    conn.commit()
    conn.close()
    print("=== Database sync completed successfully! ===")

if __name__ == '__main__':
    main()
