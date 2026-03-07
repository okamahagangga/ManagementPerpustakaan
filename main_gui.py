"""
Package: main
Aplikasi Sistem Manajemen Perpustakaan – antarmuka GUI berbasis Tkinter.

Fitur:
- CRUD Buku, Anggota, Peminjaman
- Tampilan bersih dan minimalis
- Database SQLite

Author: Asesi
Version: 2.0.0
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database as db
from models import Buku, Anggota, Peminjaman

# ── Konstanta Warna & Font ────────────────────────────────────────────────────
BG         = "#ffffff"
BG_SIDEBAR = "#f8f9fa"
BG_HEADER  = "#1a3a5c"
BG_ROW_ALT = "#f0f4f8"
BG_BTN_ADD = "#1a3a5c"
BG_BTN_DEL = "#e74c3c"
BG_BTN_EDT = "#2ecc71"
BG_BTN_SAV = "#1a3a5c"

FG_WHITE   = "#ffffff"
FG_DARK    = "#1a1a2e"
FG_MUTED   = "#6c757d"
FG_HEADER  = "#ffffff"

FONT_TITLE  = ("Segoe UI", 18, "bold")
FONT_HEADER = ("Segoe UI", 11, "bold")
FONT_BODY   = ("Segoe UI", 10)
FONT_SMALL  = ("Segoe UI", 9)
FONT_BTN    = ("Segoe UI", 10, "bold")
FONT_SIDEBAR= ("Segoe UI", 11)


class App(tk.Tk):
    """
    Kelas utama aplikasi Tkinter.
    Mengelola window utama, sidebar navigasi, dan frame konten.
    """

    def __init__(self):
        super().__init__()
        self.title("Sistem Manajemen Perpustakaan")
        self.geometry("1050x650")
        self.resizable(True, True)
        self.configure(bg=BG)
        db.init_database()
        self._build_ui()
        self.show_frame("buku")

    def _build_ui(self):
        """Membangun layout utama: sidebar + area konten."""
        # ── Sidebar ──────────────────────────────────────────────────────
        self.sidebar = tk.Frame(self, bg=BG_SIDEBAR, width=200)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo / Title
        tk.Frame(self.sidebar, bg=BG_HEADER, height=64).pack(fill="x")
        tk.Label(self.sidebar, text="📚", font=("Segoe UI", 22),
                 bg=BG_HEADER, fg=FG_WHITE).place(x=16, y=14)
        tk.Label(self.sidebar, text="Perpustakaan", font=("Segoe UI", 12, "bold"),
                 bg=BG_HEADER, fg=FG_WHITE).place(x=50, y=20)

        tk.Frame(self.sidebar, bg=BG_HEADER, height=64).pack(fill="x")

        # Menu buttons
        tk.Frame(self.sidebar, bg=BG_SIDEBAR, height=16).pack()

        self.nav_buttons = {}
        menus = [
            ("buku",     "📖  Buku"),
            ("anggota",  "👤  Anggota"),
            ("pinjam",   "📋  Peminjaman"),
        ]
        for key, label in menus:
            btn = tk.Button(
                self.sidebar, text=label,
                font=FONT_SIDEBAR, anchor="w",
                bg=BG_SIDEBAR, fg=FG_DARK,
                activebackground="#e2e8f0",
                relief="flat", bd=0,
                padx=20, pady=12,
                cursor="hand2",
                command=lambda k=key: self.show_frame(k)
            )
            btn.pack(fill="x")
            self.nav_buttons[key] = btn

        # Footer sidebar
        tk.Label(self.sidebar, text="v2.0.0", font=FONT_SMALL,
                 bg=BG_SIDEBAR, fg=FG_MUTED).pack(side="bottom", pady=12)

        # ── Area Konten ───────────────────────────────────────────────────
        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)

        self.frames = {
            "buku":    BukuFrame(self.content, self),
            "anggota": AnggotaFrame(self.content, self),
            "pinjam":  PeminjamanFrame(self.content, self),
        }

    def show_frame(self, key: str):
        """
        Menampilkan frame yang dipilih dan memperbarui highlight sidebar.

        Args:
            key (str): Key frame yang akan ditampilkan ('buku'/'anggota'/'pinjam').
        """
        for k, f in self.frames.items():
            f.pack_forget()
        self.frames[key].pack(fill="both", expand=True)
        self.frames[key].refresh()

        for k, btn in self.nav_buttons.items():
            btn.configure(
                bg="#dce8f5" if k == key else BG_SIDEBAR,
                fg=BG_HEADER if k == key else FG_DARK,
                font=("Segoe UI", 11, "bold") if k == key else FONT_SIDEBAR
            )


# ── Base Frame ────────────────────────────────────────────────────────────────
class BaseFrame(tk.Frame):
    """
    Kelas dasar frame konten. Menyediakan layout standar:
    header, toolbar, tabel, dan form input.
    Menerapkan inheritance – diwarisi oleh BukuFrame, AnggotaFrame, PeminjamanFrame.
    """

    def __init__(self, parent, app, title, columns):
        super().__init__(parent, bg=BG)
        self.app = app
        self.title_text = title
        self.columns = columns
        self.selected_id = None
        self._build()

    def _build(self):
        """Membangun layout header + toolbar + tabel + form."""
        # Header
        hdr = tk.Frame(self, bg=BG_HEADER, height=56)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text=self.title_text, font=FONT_TITLE,
                 bg=BG_HEADER, fg=FG_WHITE).pack(side="left", padx=24, pady=12)

        # Toolbar
        toolbar = tk.Frame(self, bg=BG, pady=10)
        toolbar.pack(fill="x", padx=20)
        self._build_toolbar(toolbar)

        # Body: tabel kiri + form kanan
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        # Tabel
        tbl_frame = tk.Frame(body, bg=BG)
        tbl_frame.pack(side="left", fill="both", expand=True)
        self._build_table(tbl_frame)

        # Form
        form_frame = tk.Frame(body, bg=BG_SIDEBAR, width=260,
                              padx=16, pady=16,
                              highlightbackground="#dee2e6",
                              highlightthickness=1)
        form_frame.pack(side="right", fill="y", padx=(12, 0))
        form_frame.pack_propagate(False)
        self._build_form(form_frame)

    def _build_toolbar(self, parent):
        """Toolbar dengan tombol Tambah, Edit, Hapus."""
        tk.Button(parent, text="＋  Tambah", font=FONT_BTN,
                  bg=BG_BTN_ADD, fg=FG_WHITE, relief="flat",
                  padx=14, pady=6, cursor="hand2",
                  activebackground="#2c5282",
                  command=self.clear_form).pack(side="left", padx=(0, 8))

        tk.Button(parent, text="✎  Simpan", font=FONT_BTN,
                  bg=BG_BTN_SAV, fg=FG_WHITE, relief="flat",
                  padx=14, pady=6, cursor="hand2",
                  activebackground="#2c5282",
                  command=self.save).pack(side="left", padx=(0, 8))

        tk.Button(parent, text="✕  Hapus", font=FONT_BTN,
                  bg=BG_BTN_DEL, fg=FG_WHITE, relief="flat",
                  padx=14, pady=6, cursor="hand2",
                  activebackground="#c0392b",
                  command=self.delete).pack(side="left")

        # Search
        tk.Label(parent, text="Cari:", font=FONT_BODY,
                 bg=BG, fg=FG_MUTED).pack(side="right", padx=(0, 6))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self.refresh())
        entry = tk.Entry(parent, textvariable=self.search_var,
                         font=FONT_BODY, width=20,
                         relief="solid", bd=1)
        entry.pack(side="right")

    def _build_table(self, parent):
        """Membuat tabel Treeview dengan scrollbar."""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background=BG,
                        foreground=FG_DARK,
                        rowheight=30,
                        fieldbackground=BG,
                        font=FONT_BODY,
                        borderwidth=0)
        style.configure("Treeview.Heading",
                        background=BG_SIDEBAR,
                        foreground=FG_DARK,
                        font=FONT_HEADER,
                        relief="flat")
        style.map("Treeview",
                  background=[("selected", "#dce8f5")],
                  foreground=[("selected", BG_HEADER)])

        cols = [c[0] for c in self.columns]
        self.tree = ttk.Treeview(parent, columns=cols,
                                 show="headings", selectmode="browse")

        for col, width in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="w")

        # Scrollbar
        vsb = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.tree.tag_configure("alt", background=BG_ROW_ALT)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def _build_form(self, parent):
        """Override di subclass untuk membangun form input."""
        pass

    def lbl_entry(self, parent, label, row, is_combo=False, values=None):
        """
        Helper membuat label + entry/combobox dalam form.

        Args:
            parent: Frame induk.
            label (str): Teks label.
            row (int): Baris grid.
            is_combo (bool): Jika True, buat Combobox.
            values (list): Pilihan untuk Combobox.

        Returns:
            tk.StringVar: Variable terikat ke widget input.
        """
        tk.Label(parent, text=label, font=FONT_SMALL,
                 bg=BG_SIDEBAR, fg=FG_MUTED,
                 anchor="w").grid(row=row*2, column=0, sticky="w", pady=(8, 2))
        var = tk.StringVar()
        if is_combo:
            w = ttk.Combobox(parent, textvariable=var, values=values,
                             font=FONT_BODY, state="readonly", width=24)
        else:
            w = tk.Entry(parent, textvariable=var, font=FONT_BODY,
                         relief="solid", bd=1, width=26)
        w.grid(row=row*2+1, column=0, sticky="ew", pady=(0, 2))
        return var

    def form_title(self, parent, text):
        """Judul form di panel kanan."""
        tk.Label(parent, text=text, font=FONT_HEADER,
                 bg=BG_SIDEBAR, fg=BG_HEADER).grid(
            row=0, column=0, sticky="w", pady=(0, 8))

    def refresh(self): pass
    def save(self): pass
    def delete(self): pass
    def clear_form(self): pass
    def on_select(self, event): pass

    def load_tree(self, rows, fields):
        """
        Mengisi tabel dengan data dari database.

        Args:
            rows (list): List dict data.
            fields (list): Field yang ditampilkan di kolom.
        """
        self.tree.delete(*self.tree.get_children())
        keyword = self.search_var.get().lower()
        i = 0
        for row in rows:
            values = [row.get(f, "") for f in fields]
            if keyword and not any(keyword in str(v).lower() for v in values):
                continue
            tag = "alt" if i % 2 == 1 else ""
            self.tree.insert("", "end", iid=row["id"],
                             values=values, tags=(tag,))
            i += 1


# ── Frame Buku ────────────────────────────────────────────────────────────────
class BukuFrame(BaseFrame):
    """Frame manajemen buku. Mewarisi BaseFrame (inheritance)."""

    def __init__(self, parent, app):
        super().__init__(parent, app, "📖  Manajemen Buku", [
            ("ID", 40), ("Judul", 180), ("Pengarang", 140),
            ("Tahun", 60), ("Stok", 50), ("Genre", 90)
        ])

    def _build_form(self, parent):
        self.form_title(parent, "Form Buku")
        self.v_judul     = self.lbl_entry(parent, "Judul", 1)
        self.v_pengarang = self.lbl_entry(parent, "Pengarang", 2)
        self.v_tahun     = self.lbl_entry(parent, "Tahun Terbit", 3)
        self.v_stok      = self.lbl_entry(parent, "Stok", 4)
        self.v_genre     = self.lbl_entry(parent, "Genre", 5,
                                          is_combo=True, values=Buku.GENRE_LIST)
        self.v_genre.set("Teknologi")

    def refresh(self):
        rows = db.fetch_all("buku")
        self.load_tree(rows, ["id", "judul", "pengarang", "tahun", "stok", "genre"])

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        self.selected_id = int(sel[0])
        row = db.fetch_one("buku", self.selected_id)
        if row:
            self.v_judul.set(row["judul"])
            self.v_pengarang.set(row["pengarang"])
            self.v_tahun.set(row["tahun"])
            self.v_stok.set(row["stok"])
            self.v_genre.set(row["genre"])

    def clear_form(self):
        self.selected_id = None
        self.v_judul.set("")
        self.v_pengarang.set("")
        self.v_tahun.set("")
        self.v_stok.set("1")
        self.v_genre.set("Teknologi")
        self.tree.selection_remove(self.tree.selection())

    def save(self):
        judul = self.v_judul.get().strip()
        pengarang = self.v_pengarang.get().strip()
        try:
            tahun = int(self.v_tahun.get())
            stok  = int(self.v_stok.get())
        except ValueError:
            messagebox.showerror("Error", "Tahun dan Stok harus berupa angka!")
            return
        genre = self.v_genre.get()

        buku = Buku(judul, pengarang, tahun, stok, genre)
        if not buku.validate():
            messagebox.showerror("Error", "Judul, pengarang, dan tahun wajib diisi!")
            return

        if self.selected_id:
            db.update_record("buku", self.selected_id, buku.to_dict())
            messagebox.showinfo("Berhasil", "Data buku diperbarui!")
        else:
            db.insert_record("buku", buku.to_dict())
            messagebox.showinfo("Berhasil", "Buku berhasil ditambahkan!")

        self.clear_form()
        self.refresh()

    def delete(self):
        if not self.selected_id:
            messagebox.showwarning("Perhatian", "Pilih buku yang ingin dihapus!")
            return
        if messagebox.askyesno("Konfirmasi", "Yakin hapus buku ini?"):
            db.delete_record("buku", self.selected_id)
            self.clear_form()
            self.refresh()


# ── Frame Anggota ─────────────────────────────────────────────────────────────
class AnggotaFrame(BaseFrame):
    """Frame manajemen anggota. Mewarisi BaseFrame (inheritance)."""

    def __init__(self, parent, app):
        super().__init__(parent, app, "👤  Manajemen Anggota", [
            ("ID", 40), ("Nama", 160), ("Email", 180),
            ("Telepon", 120), ("Status", 80)
        ])

    def _build_form(self, parent):
        self.form_title(parent, "Form Anggota")
        self.v_nama    = self.lbl_entry(parent, "Nama", 1)
        self.v_email   = self.lbl_entry(parent, "Email", 2)
        self.v_telepon = self.lbl_entry(parent, "Telepon", 3)
        self.v_status  = self.lbl_entry(parent, "Status", 4,
                                        is_combo=True, values=Anggota.STATUS_OPTIONS)
        self.v_status.set("Aktif")

    def refresh(self):
        rows = db.fetch_all("anggota")
        self.load_tree(rows, ["id", "nama", "email", "telepon", "status"])

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        self.selected_id = int(sel[0])
        row = db.fetch_one("anggota", self.selected_id)
        if row:
            self.v_nama.set(row["nama"])
            self.v_email.set(row["email"])
            self.v_telepon.set(row["telepon"] or "")
            self.v_status.set(row["status"])

    def clear_form(self):
        self.selected_id = None
        for v in [self.v_nama, self.v_email, self.v_telepon]:
            v.set("")
        self.v_status.set("Aktif")
        self.tree.selection_remove(self.tree.selection())

    def save(self):
        nama   = self.v_nama.get().strip()
        email  = self.v_email.get().strip()
        telp   = self.v_telepon.get().strip()
        status = self.v_status.get()

        anggota = Anggota(nama, email, telp, status)
        if not anggota.validate():
            messagebox.showerror("Error", "Nama dan email valid wajib diisi!")
            return

        if self.selected_id:
            db.update_record("anggota", self.selected_id, anggota.to_dict())
            messagebox.showinfo("Berhasil", "Data anggota diperbarui!")
        else:
            db.insert_record("anggota", anggota.to_dict())
            messagebox.showinfo("Berhasil", "Anggota berhasil ditambahkan!")

        self.clear_form()
        self.refresh()

    def delete(self):
        if not self.selected_id:
            messagebox.showwarning("Perhatian", "Pilih anggota yang ingin dihapus!")
            return
        if messagebox.askyesno("Konfirmasi", "Yakin hapus anggota ini?"):
            db.delete_record("anggota", self.selected_id)
            self.clear_form()
            self.refresh()


# ── Frame Peminjaman ──────────────────────────────────────────────────────────
class PeminjamanFrame(BaseFrame):
    """Frame manajemen peminjaman. Mewarisi BaseFrame (inheritance)."""

    def __init__(self, parent, app):
        super().__init__(parent, app, "📋  Manajemen Peminjaman", [
            ("ID", 40), ("Anggota", 150), ("Buku", 160),
            ("Tgl Pinjam", 100), ("Tgl Kembali", 100), ("Status", 90)
        ])

    def _build_form(self, parent):
        self.form_title(parent, "Form Peminjaman")

        # Dropdown Anggota
        tk.Label(parent, text="Anggota", font=FONT_SMALL,
                 bg=BG_SIDEBAR, fg=FG_MUTED, anchor="w").grid(
            row=2, column=0, sticky="w", pady=(8, 2))
        self.v_anggota = tk.StringVar()
        self.cb_anggota = ttk.Combobox(parent, textvariable=self.v_anggota,
                                       font=FONT_BODY, state="readonly", width=24)
        self.cb_anggota.grid(row=3, column=0, sticky="ew")

        # Dropdown Buku
        tk.Label(parent, text="Buku", font=FONT_SMALL,
                 bg=BG_SIDEBAR, fg=FG_MUTED, anchor="w").grid(
            row=4, column=0, sticky="w", pady=(8, 2))
        self.v_buku = tk.StringVar()
        self.cb_buku = ttk.Combobox(parent, textvariable=self.v_buku,
                                    font=FONT_BODY, state="readonly", width=24)
        self.cb_buku.grid(row=5, column=0, sticky="ew")

        # Tombol Kembalikan
        tk.Frame(parent, bg=BG_SIDEBAR, height=16).grid(row=6, column=0)
        tk.Button(parent, text="↩  Kembalikan Buku",
                  font=FONT_BTN, bg="#2ecc71", fg=FG_WHITE,
                  relief="flat", padx=10, pady=6, cursor="hand2",
                  activebackground="#27ae60",
                  command=self.kembalikan).grid(row=7, column=0, sticky="ew")

    def _load_dropdowns(self):
        """Mengisi dropdown anggota dan buku dari database."""
        anggota_rows = db.fetch_all("anggota", "status = ?", ["Aktif"])
        self.anggota_map = {f"{r['nama']} (ID:{r['id']})": r["id"] for r in anggota_rows}
        self.cb_anggota["values"] = list(self.anggota_map.keys())

        buku_rows = db.fetch_all("buku", "stok > 0")
        self.buku_map = {f"{r['judul']} (ID:{r['id']})": r["id"] for r in buku_rows}
        self.cb_buku["values"] = list(self.buku_map.keys())

    def refresh(self):
        self._load_dropdowns()
        sql = """
            SELECT p.id, a.nama AS anggota, b.judul AS buku,
                   p.tanggal_pinjam, p.tanggal_kembali, p.status,
                   p.id_anggota, p.id_buku
            FROM peminjaman p
            JOIN anggota a ON p.id_anggota = a.id
            JOIN buku    b ON p.id_buku    = b.id
            ORDER BY p.id DESC
        """
        rows = db.execute_query(sql)
        self.tree.delete(*self.tree.get_children())
        keyword = self.search_var.get().lower()
        for i, row in enumerate(rows):
            values = [
                row["id"], row["anggota"], row["buku"],
                row["tanggal_pinjam"],
                row["tanggal_kembali"] or "-",
                row["status"]
            ]
            if keyword and not any(keyword in str(v).lower() for v in values):
                continue
            tag = "alt" if i % 2 == 1 else ""
            # Warnai baris yang masih dipinjam
            if row["status"] == "Dipinjam":
                tag = "dipinjam"
            self.tree.insert("", "end", iid=row["id"], values=values, tags=(tag,))
        self.tree.tag_configure("dipinjam", foreground="#e74c3c")

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        self.selected_id = int(sel[0])

    def clear_form(self):
        self.selected_id = None
        self.v_anggota.set("")
        self.v_buku.set("")
        self.tree.selection_remove(self.tree.selection())

    def save(self):
        """Menyimpan data peminjaman baru."""
        anggota_label = self.v_anggota.get()
        buku_label    = self.v_buku.get()

        if not anggota_label or not buku_label:
            messagebox.showerror("Error", "Pilih anggota dan buku terlebih dahulu!")
            return

        id_anggota = self.anggota_map[anggota_label]
        id_buku    = self.buku_map[buku_label]

        buku_row = db.fetch_one("buku", id_buku)
        if not buku_row or buku_row["stok"] < 1:
            messagebox.showerror("Error", "Stok buku habis!")
            return

        pinjam = Peminjaman(id_anggota, id_buku)
        db.insert_record("peminjaman", pinjam.to_dict())
        db.update_record("buku", id_buku, {"stok": buku_row["stok"] - 1})

        messagebox.showinfo("Berhasil", "Peminjaman berhasil dicatat!")
        self.clear_form()
        self.refresh()

    def kembalikan(self):
        """Memproses pengembalian buku yang dipilih di tabel."""
        if not self.selected_id:
            messagebox.showwarning("Perhatian", "Pilih data peminjaman di tabel!")
            return
        row = db.fetch_one("peminjaman", self.selected_id)
        if not row:
            return
        if row["status"] == "Dikembalikan":
            messagebox.showinfo("Info", "Buku ini sudah dikembalikan.")
            return

        tgl = datetime.now().strftime("%Y-%m-%d")
        db.update_record("peminjaman", self.selected_id, {
            "status": "Dikembalikan", "tanggal_kembali": tgl
        })
        buku_row = db.fetch_one("buku", row["id_buku"])
        if buku_row:
            db.update_record("buku", row["id_buku"], {"stok": buku_row["stok"] + 1})

        messagebox.showinfo("Berhasil", f"Buku dikembalikan pada {tgl}!")
        self.clear_form()
        self.refresh()

    def delete(self):
        if not self.selected_id:
            messagebox.showwarning("Perhatian", "Pilih data peminjaman yang ingin dihapus!")
            return
        if messagebox.askyesno("Konfirmasi", "Yakin hapus data peminjaman ini?"):
            db.delete_record("peminjaman", self.selected_id)
            self.clear_form()
            self.refresh()


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()
