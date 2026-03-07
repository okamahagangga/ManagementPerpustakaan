"""
Package: models
Modul yang berisi definisi kelas-kelas model untuk Sistem Perpustakaan.
Menerapkan OOP: inheritance, polymorphism, overloading (via default args), dan interface (ABC).

Author: Asesi
Version: 1.0.0
"""

from abc import ABC, abstractmethod
from datetime import datetime


# ── Interface (Abstract Base Class) ──────────────────────────────────────────
class IStorable(ABC):
    """
    Interface yang harus diimplementasikan oleh semua entitas yang bisa disimpan ke database.
    Menerapkan konsep interface pada Python melalui Abstract Base Class.
    """

    @abstractmethod
    def to_dict(self) -> dict:
        """Mengkonversi objek ke dictionary."""
        pass

    @abstractmethod
    def validate(self) -> bool:
        """Memvalidasi data objek sebelum disimpan."""
        pass


# ── Base Class ────────────────────────────────────────────────────────────────
class BaseEntity(IStorable):
    """
    Kelas dasar (parent) untuk semua entitas.
    Menerapkan: encapsulation (private __id), properties, dan inheritance.

    Attributes:
        __id (int): ID unik entitas (private).
        created_at (str): Waktu pembuatan record.
    """

    def __init__(self, id: int = None):
        """
        Constructor BaseEntity.

        Args:
            id (int, optional): ID entitas. Default None (auto dari DB).
        """
        self.__id = id                                  # private attribute
        self.created_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ── Properties ────────────────────────────────────────────────────────────
    @property
    def id(self) -> int:
        """Getter untuk ID (read-only dari luar)."""
        return self.__id

    @id.setter
    def id(self, value: int):
        """Setter untuk ID (hanya boleh diset sekali)."""
        if self.__id is None:
            self.__id = value

    def __str__(self) -> str:
        """String representasi objek – di-override di subclass (polymorphism)."""
        return f"BaseEntity(id={self.__id})"


# ── Subclass: Buku ────────────────────────────────────────────────────────────
class Buku(BaseEntity):
    """
    Kelas Buku – merupakan turunan (inheritance) dari BaseEntity.
    Menerapkan polymorphism pada method __str__ dan validate.

    Attributes:
        judul (str): Judul buku.
        pengarang (str): Nama pengarang.
        tahun (int): Tahun terbit.
        stok (int): Jumlah stok buku.
        genre (str): Genre buku.
    """

    # Array / list konstanta genre yang tersedia
    GENRE_LIST: list = ["Fiksi", "Non-Fiksi", "Sains", "Sejarah", "Teknologi", "Lainnya"]

    def __init__(self, judul: str, pengarang: str, tahun: int,
                 stok: int = 1, genre: str = "Lainnya", id: int = None):
        """
        Constructor Buku dengan default argument (simulasi overloading).

        Args:
            judul (str): Judul buku.
            pengarang (str): Pengarang buku.
            tahun (int): Tahun terbit.
            stok (int, optional): Stok buku. Default 1.
            genre (str, optional): Genre buku. Default 'Lainnya'.
            id (int, optional): ID buku. Default None.
        """
        super().__init__(id)          # memanggil constructor parent
        self.judul: str = judul
        self.pengarang: str = pengarang
        self.tahun: int = tahun
        self.stok: int = stok
        self.genre: str = genre if genre in self.GENRE_LIST else "Lainnya"

    def validate(self) -> bool:
        """
        Validasi data buku (implementasi dari interface IStorable).

        Returns:
            bool: True jika data valid, False jika tidak.
        """
        return bool(self.judul) and bool(self.pengarang) and self.tahun > 0 and self.stok >= 0

    def to_dict(self) -> dict:
        """
        Mengkonversi objek Buku ke dictionary (implementasi IStorable).

        Returns:
            dict: Dictionary representasi buku.
        """
        return {
            "id": self.id,
            "judul": self.judul,
            "pengarang": self.pengarang,
            "tahun": self.tahun,
            "stok": self.stok,
            "genre": self.genre,
            "created_at": self.created_at
        }

    def __str__(self) -> str:
        """Polymorphism: override __str__ dari BaseEntity."""
        return f"[{self.id}] {self.judul} - {self.pengarang} ({self.tahun}) | Stok: {self.stok}"


# ── Subclass: Anggota ─────────────────────────────────────────────────────────
class Anggota(BaseEntity):
    """
    Kelas Anggota – turunan (inheritance) dari BaseEntity.
    Menerapkan polymorphism pada __str__ dan validate.

    Attributes:
        nama (str): Nama anggota.
        email (str): Email anggota.
        telepon (str): Nomor telepon.
        status (str): Status keanggotaan ('Aktif' atau 'Nonaktif').
    """

    STATUS_OPTIONS: list = ["Aktif", "Nonaktif"]   # Array/list konstanta

    def __init__(self, nama: str, email: str, telepon: str = "",
                 status: str = "Aktif", id: int = None):
        """
        Constructor Anggota.

        Args:
            nama (str): Nama anggota.
            email (str): Alamat email.
            telepon (str, optional): Nomor telepon. Default ''.
            status (str, optional): Status anggota. Default 'Aktif'.
            id (int, optional): ID anggota. Default None.
        """
        super().__init__(id)
        self.nama: str = nama
        self.email: str = email
        self.telepon: str = telepon
        self.status: str = status if status in self.STATUS_OPTIONS else "Aktif"

    def validate(self) -> bool:
        """Validasi data anggota."""
        return bool(self.nama) and "@" in self.email

    def to_dict(self) -> dict:
        """Konversi ke dictionary."""
        return {
            "id": self.id,
            "nama": self.nama,
            "email": self.email,
            "telepon": self.telepon,
            "status": self.status,
            "created_at": self.created_at
        }

    def __str__(self) -> str:
        """Polymorphism: override __str__."""
        return f"[{self.id}] {self.nama} | {self.email} | Status: {self.status}"


# ── Subclass: Peminjaman ──────────────────────────────────────────────────────
class Peminjaman(BaseEntity):
    """
    Kelas Peminjaman – turunan BaseEntity.
    Merepresentasikan transaksi peminjaman buku oleh anggota.

    Attributes:
        id_anggota (int): ID anggota peminjam.
        id_buku (int): ID buku yang dipinjam.
        tanggal_pinjam (str): Tanggal peminjaman.
        tanggal_kembali (str): Tanggal pengembalian (None jika belum kembali).
        status (str): Status peminjaman ('Dipinjam' atau 'Dikembalikan').
    """

    def __init__(self, id_anggota: int, id_buku: int,
                 tanggal_pinjam: str = None, tanggal_kembali: str = None,
                 status: str = "Dipinjam", id: int = None):
        super().__init__(id)
        self.id_anggota: int = id_anggota
        self.id_buku: int = id_buku
        self.tanggal_pinjam: str = tanggal_pinjam or datetime.now().strftime("%Y-%m-%d")
        self.tanggal_kembali: str = tanggal_kembali
        self.status: str = status

    def validate(self) -> bool:
        """Validasi peminjaman."""
        return self.id_anggota > 0 and self.id_buku > 0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "id_anggota": self.id_anggota,
            "id_buku": self.id_buku,
            "tanggal_pinjam": self.tanggal_pinjam,
            "tanggal_kembali": self.tanggal_kembali,
            "status": self.status,
            "created_at": self.created_at
        }

    def __str__(self) -> str:
        return (f"[{self.id}] Anggota#{self.id_anggota} meminjam Buku#{self.id_buku} "
                f"| Pinjam: {self.tanggal_pinjam} | Status: {self.status}")
