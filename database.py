
import sqlite3
import os
from typing import List, Optional

# Konstanta path database (External Library: sqlite3 dari stdlib)
DB_PATH: str = os.path.join(os.path.dirname(__file__), "perpustakaan.db")


def get_connection() -> sqlite3.Connection:
    """
    Membuat dan mengembalikan koneksi ke database SQLite.

    Returns:
        sqlite3.Connection: Objek koneksi database.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # baris dikembalikan sebagai dict-like
    return conn


def init_database() -> None:
    """
    Menginisialisasi database: membuat tabel jika belum ada.
    Dipanggil sekali saat aplikasi pertama dijalankan.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Tabel buku
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS buku (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            judul       TEXT    NOT NULL,
            pengarang   TEXT    NOT NULL,
            tahun       INTEGER NOT NULL,
            stok        INTEGER DEFAULT 1,
            genre       TEXT    DEFAULT 'Lainnya',
            created_at  TEXT
        )
    """)

    # Tabel anggota
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS anggota (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nama        TEXT    NOT NULL,
            email       TEXT    NOT NULL UNIQUE,
            telepon     TEXT,
            status      TEXT    DEFAULT 'Aktif',
            created_at  TEXT
        )
    """)

    # Tabel peminjaman
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS peminjaman (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            id_anggota       INTEGER NOT NULL,
            id_buku          INTEGER NOT NULL,
            tanggal_pinjam   TEXT,
            tanggal_kembali  TEXT,
            status           TEXT    DEFAULT 'Dipinjam',
            created_at       TEXT,
            FOREIGN KEY (id_anggota) REFERENCES anggota(id),
            FOREIGN KEY (id_buku)    REFERENCES buku(id)
        )
    """)

    conn.commit()
    conn.close()


# ── Generic CRUD Functions ────────────────────────────────────────────────────

def insert_record(table: str, data: dict) -> int:
    """
    Menyisipkan satu record ke tabel yang ditentukan.

    Args:
        table (str): Nama tabel tujuan.
        data (dict): Data yang akan disisipkan (key = nama kolom).

    Returns:
        int: ID record yang baru dibuat.
    """
    data.pop("id", None)          # hapus key 'id' agar AUTOINCREMENT berjalan
    columns = ", ".join(data.keys())
    placeholders = ", ".join(["?" for _ in data])
    sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, list(data.values()))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id


def fetch_all(table: str, where: str = "", params: list = None) -> List[dict]:
    """
    Mengambil semua record dari tabel, dengan opsional klausa WHERE.

    Args:
        table (str): Nama tabel.
        where (str, optional): Klausa WHERE tanpa keyword 'WHERE'. Default ''.
        params (list, optional): Parameter untuk prepared statement. Default None.

    Returns:
        List[dict]: Daftar record sebagai dictionary.
    """
    sql = f"SELECT * FROM {table}"
    if where:
        sql += f" WHERE {where}"

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, params or [])
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def fetch_one(table: str, record_id: int) -> Optional[dict]:
    """
    Mengambil satu record berdasarkan ID.

    Args:
        table (str): Nama tabel.
        record_id (int): ID record yang dicari.

    Returns:
        Optional[dict]: Dictionary data record, atau None jika tidak ditemukan.
    """
    rows = fetch_all(table, "id = ?", [record_id])
    return rows[0] if rows else None


def update_record(table: str, record_id: int, data: dict) -> bool:
    """
    Memperbarui record berdasarkan ID.

    Args:
        table (str): Nama tabel.
        record_id (int): ID record yang akan diperbarui.
        data (dict): Data baru (key = nama kolom).

    Returns:
        bool: True jika berhasil, False jika tidak ada record yang diubah.
    """
    data.pop("id", None)
    set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
    sql = f"UPDATE {table} SET {set_clause} WHERE id = ?"

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, list(data.values()) + [record_id])
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def delete_record(table: str, record_id: int) -> bool:
    """
    Menghapus record berdasarkan ID.

    Args:
        table (str): Nama tabel.
        record_id (int): ID record yang akan dihapus.

    Returns:
        bool: True jika berhasil dihapus.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table} WHERE id = ?", [record_id])
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def execute_query(sql: str, params: list = None) -> List[dict]:
    """
    Menjalankan query SQL kustom dan mengembalikan hasilnya.

    Args:
        sql (str): Pernyataan SQL.
        params (list, optional): Parameter. Default None.

    Returns:
        List[dict]: Hasil query sebagai list of dict.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, params or [])
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows
