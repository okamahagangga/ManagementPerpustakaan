"""
Script untuk mengisi database dengan data contoh (seed data).
Jalankan sekali saja: python seed.py

Author: Asesi
"""

import sys
import os

# Pastikan bisa import modul dari folder yang sama
sys.path.insert(0, os.path.dirname(__file__))

import database as db
from models import Buku, Anggota, Peminjaman

def seed():
    db.init_database()

    # ── Cek apakah sudah ada data ─────────────────────────────────────────
    existing = db.fetch_all("buku")
    if existing:
        print(f"Database sudah ada {len(existing)} buku. Seed dibatalkan.")
        print("Hapus file 'perpustakaan.db' dulu jika ingin reset.")
        return

    # ── Data Buku ─────────────────────────────────────────────────────────
    buku_list = [
        Buku("Python Programming",        "Guido van Rossum",    2020, 3, "Teknologi"),
        Buku("Laskar Pelangi",            "Andrea Hirata",       2005, 2, "Fiksi"),
        Buku("Sapiens",                   "Yuval Noah Harari",   2011, 5, "Sejarah"),
        Buku("Clean Code",                "Robert C. Martin",    2008, 2, "Teknologi"),
        Buku("Bumi Manusia",              "Pramoedya Ananta",    1980, 4, "Fiksi"),
        Buku("A Brief History of Time",   "Stephen Hawking",     1988, 3, "Sains"),
        Buku("Atomic Habits",             "James Clear",         2018, 6, "Non-Fiksi"),
        Buku("Pemrograman Web dengan PHP","Budi Raharjo",        2016, 2, "Teknologi"),
    ]

    print("Menambahkan data buku...")
    for b in buku_list:
        new_id = db.insert_record("buku", b.to_dict())
        print(f"  ✔ [{new_id}] {b.judul}")

    # ── Data Anggota ──────────────────────────────────────────────────────
    anggota_list = [
        Anggota("Budi Santoso",   "budi@email.com",   "08123456789"),
        Anggota("Siti Rahayu",    "siti@email.com",   "08987654321"),
        Anggota("Andi Wijaya",    "andi@email.com",   "08111222333"),
        Anggota("Dewi Lestari",   "dewi@email.com",   "08444555666"),
    ]

    print("\nMenambahkan data anggota...")
    for a in anggota_list:
        new_id = db.insert_record("anggota", a.to_dict())
        print(f"  ✔ [{new_id}] {a.nama}")

    # ── Data Peminjaman ───────────────────────────────────────────────────
    peminjaman_list = [
        Peminjaman(1, 1, "2026-02-20", status="Dipinjam"),
        Peminjaman(2, 3, "2026-02-25", status="Dipinjam"),
        Peminjaman(3, 5, "2026-02-10", "2026-02-20", status="Dikembalikan"),
    ]

    print("\nMenambahkan data peminjaman...")
    for p in peminjaman_list:
        new_id = db.insert_record("peminjaman", p.to_dict())
        print(f"  ✔ [{new_id}] Anggota#{p.id_anggota} → Buku#{p.id_buku} ({p.status})")

    print("\n✅ Seed data selesai! Sekarang jalankan: python main.py")

if __name__ == "__main__":
    seed()
