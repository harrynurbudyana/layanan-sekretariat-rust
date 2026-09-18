#!/usr/bin/env python3
"""
Sync and update the official letter agenda database (backend/data/dev.db)
with the latest Buku Agenda FIT CSV export.

Tasks performed:
1. Backup dev.db to dev.db.bak
2. Map units and categories accurately
3. Remove test/stale records not present in the official agenda
4. Insert missing records (up to sequence 1728)
5. Update LetterCounter for FIT (currentNumber = max sequence number)
6. Verify database integrity and foreign key constraints
"""

import os
import shutil
import sqlite3
import csv
import re
import uuid
import datetime

MONTH_NAMES = {
    'januari': 1, 'februari': 2, 'maret': 3, 'april': 4,
    'mei': 5, 'juni': 6, 'juli': 7, 'agustus': 8,
    'september': 9, 'oktober': 10, 'november': 11, 'desember': 12
}

SHORT_MONTHS = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
    'mei': 5, 'jun': 6, 'jul': 7, 'agu': 8, 'agt': 8,
    'sep': 9, 'okt': 10, 'nov': 11, 'des': 12
}

ROMAN_MONTHS = {
    1: 'I', 2: 'II', 3: 'III', 4: 'IV',
    5: 'V', 6: 'VI', 7: 'VII', 8: 'VIII',
    9: 'IX', 10: 'X', 11: 'XI', 12: 'XII'
}

WIB = datetime.timezone(datetime.timedelta(hours=7))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
DB_PATH = os.path.join(DATA_DIR, 'dev.db')
BACKUP_PATH = os.path.join(DATA_DIR, 'dev.db.bak')
CSV_PATH = os.path.join(DATA_DIR, 'buku_agenda_fit_2026-09-18.csv')

def parse_letter_date(date_str):
    parts = date_str.strip().split()
    day = int(parts[0])
    month = MONTH_NAMES[parts[1].lower()]
    year = int(parts[2])
    dt = datetime.datetime(year, month, day, 0, 0, 0, tzinfo=WIB)
    ts = int(dt.timestamp() * 1000)
    return day, month, year, ts

def parse_created_at(wp_str):
    m = re.match(r'(\d+)\s+([A-Za-z]+)\s+(\d{4}),?\s+(\d{1,2})[.:](\d{2})', wp_str.strip())
    if not m:
        now = datetime.datetime.now(tz=WIB)
        return int(now.timestamp() * 1000)
    day = int(m.group(1))
    month = SHORT_MONTHS.get(m.group(2).lower()[:3], 9)
    year = int(m.group(3))
    hour = int(m.group(4))
    minute = int(m.group(5))
    dt = datetime.datetime(year, month, day, hour, minute, 0, tzinfo=WIB)
    return int(dt.timestamp() * 1000)

def main():
    print("=== Synchronizing dev.db with Buku Agenda FIT (2026-09-18) ===")
    
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"CSV file not found: {CSV_PATH}")
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database file not found: {DB_PATH}")

    # 1. Backup
    print(f"Creating backup: {BACKUP_PATH}")
    shutil.copy2(DB_PATH, BACKUP_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    # Load lookup tables
    cur.execute("SELECT code, id FROM Unit")
    units_by_code = {r[0]: r[1] for r in cur.fetchall()}
    cur.execute("SELECT name, id FROM Unit")
    units_by_name = {r[0]: r[1] for r in cur.fetchall()}

    cur.execute("SELECT code, id FROM LetterCategory")
    cats_by_code = {r[0]: r[1] for r in cur.fetchall()}

    def find_unit_id(unit_str):
        if not unit_str:
            return None
        m = re.search(r'\(([^)]+)\)$', unit_str.strip())
        if m:
            code = m.group(1).strip()
            if code in units_by_code:
                return units_by_code[code]
        return units_by_name.get(unit_str.strip())

    # Read CSV
    with open(CSV_PATH, encoding='utf-8-sig') as f:
        csv_rows = list(csv.DictReader(f))

    print(f"Loaded {len(csv_rows)} rows from CSV.")

    # Find existing records in DB
    cur.execute('SELECT fullNumber, id, sequenceNumber FROM "LetterRequest"')
    db_records = {r[0]: {'id': r[1], 'seq': r[2]} for r in cur.fetchall()}
    print(f"Existing records in DB: {len(db_records)}")

    # 2. Identify records in DB that are not in CSV (stale 2025 rows or dev test rows)
    csv_full_numbers = set(r['Nomor Surat Lengkap'] for r in csv_rows)
    to_delete = [fn for fn in db_records if fn not in csv_full_numbers]
    if to_delete:
        print(f"Removing {len(to_delete)} stale/test records from DB: {to_delete}")
        cur.executemany('DELETE FROM "LetterRequest" WHERE fullNumber = ?', [(fn,) for fn in to_delete])

    # 3. Identify and insert new records
    inserted_count = 0
    max_seq = 0

    for r in csv_rows:
        full_number = r['Nomor Surat Lengkap'].strip()
        seq_raw = r['No. Urut'].strip()
        seq = int(seq_raw) if seq_raw.isdigit() else 0
        if seq > max_seq:
            max_seq = seq

        classification_code = r['Klasifikasi Perihal'].strip()
        signee_code = r['Penandatangan'].strip()
        unit_name_raw = r['Program Studi / Unit'].strip()
        subject = r['Perihal'].strip()
        applicant_name = r['Nama Pemohon'].strip()
        applicant_contact = r['No. Kontak'].strip() or None
        recipient = r['Tujuan / Penerima'].strip() or None
        is_manual = 1 if r['Metode Input'].strip().lower() == 'manual' else 0
        notes = r['Catatan'].strip() or None
        
        day, month, year, letter_date_ts = parse_letter_date(r['Tanggal Surat'])
        month_romawi = ROMAN_MONTHS.get(month, 'I')
        created_at_ts = parse_created_at(r['Waktu Pencatatan'])
        
        unit_id = find_unit_id(unit_name_raw)
        if not unit_id:
            raise ValueError(f"Could not map unit for: {unit_name_raw}")

        category_id = cats_by_code.get(classification_code)
        if not category_id:
            raise ValueError(f"Could not map category for: {classification_code}")

        if full_number not in db_records:
            # Insert new letter
            letter_id = f"cmt_{uuid.uuid4().hex}"
            cur.execute(r'''
                INSERT INTO "LetterRequest" (
                    id, sequenceNumber, monthRomawi, month, year, fullNumber,
                    classificationCode, signeeCode, subject, recipient,
                    applicantName, applicantContact, applicantEmail, letterDate, notes, isManual, status,
                    unitId, categoryId, createdAt, updatedAt, letterType, sender, receivedDate
                ) VALUES (
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, NULL, ?, ?, ?, 'ISSUED',
                    ?, ?, ?, ?, 'OUTGOING', NULL, NULL
                )
            ''', (
                letter_id, seq, month_romawi, month, year, full_number,
                classification_code, signee_code, subject, recipient,
                applicant_name, applicant_contact, letter_date_ts, notes, is_manual,
                unit_id, category_id, created_at_ts, created_at_ts
            ))
            inserted_count += 1

    print(f"Inserted {inserted_count} new records.")

    # 4. Update LetterCounter
    print(f"Updating LetterCounter to currentNumber = {max_seq} (Year 2026, Scope FIT)...")
    cnt_id = f"cnt_2026_{uuid.uuid4().hex[:16]}"
    cur.execute(r'''
        INSERT INTO "LetterCounter" (id, year, scope, currentNumber, updatedAt)
        VALUES (?, 2026, 'FIT', ?, datetime('now'))
        ON CONFLICT(year, scope) DO UPDATE SET
            currentNumber = max(currentNumber, excluded.currentNumber),
            updatedAt = datetime('now')
    ''', (cnt_id, max_seq))

    conn.commit()

    # 5. Integrity checks
    cur.execute('SELECT count(*) FROM "LetterRequest"')
    total_in_db = cur.fetchone()[0]
    print(f"Total letters in DB now: {total_in_db}")

    cur.execute('SELECT currentNumber FROM "LetterCounter" WHERE year = 2026 AND scope = "FIT"')
    curr_counter = cur.fetchone()[0]
    print(f"LetterCounter FIT 2026: {curr_counter}")

    cur.execute("PRAGMA foreign_key_check")
    fk_errors = cur.fetchall()
    if fk_errors:
        print(f"WARNING: Foreign key errors found: {fk_errors}")
    else:
        print("Foreign key check passed (no errors).")

    cur.execute("PRAGMA integrity_check")
    integrity = cur.fetchone()[0]
    print(f"Integrity check: {integrity}")

    conn.close()
    print("=== Sync completed successfully! ===")

if __name__ == '__main__':
    main()
