import tkinter as tk
from tkinter import ttk, messagebox
import threading
import repository as db
from logic import hitung_total, hitung_huruf


class AplikasiPenilaian:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistem Penilaian Mahasiswa")
        self.root.geometry("860x520")
        self.root.resizable(True, True)
        self.root.configure(bg="#f0f4f8")

        self.indeks_terpilih = None  # menyimpan indeks baris yang dipilih di tabel

        db.inisialisasi_csv()
        self._bangun_ui()
        self.muat_data_ke_tabel()

    # Pembangunan UI
    def _bangun_ui(self):
        # Judul
        frame_judul = tk.Frame(self.root, bg="#1a73e8", pady=10)
        frame_judul.pack(fill=tk.X)
        tk.Label(
            frame_judul,
            text="Sistem Penilaian Mahasiswa",
            font=("Arial", 16, "bold"),
            bg="#1a73e8", fg="white"
        ).pack()

        # Konten utama (tabel kiri + form kanan)
        frame_konten = tk.Frame(self.root, bg="#f0f4f8")
        frame_konten.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        self._bangun_tabel(frame_konten)
        self._bangun_form(frame_konten)

    def _bangun_tabel(self, parent):
        frame_kiri = tk.Frame(parent, bg="#f0f4f8")
        frame_kiri.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Treeview
        kolom = ("Nama", "Tugas", "UTS", "UAS", "Total", "Huruf")
        self.tabel = ttk.Treeview(frame_kiri, columns=kolom, show="headings", height=15)

        lebar = {"Nama": 160, "Tugas": 70, "UTS": 70, "UAS": 70, "Total": 70, "Huruf": 60}
        for k in kolom:
            self.tabel.heading(k, text=k)
            self.tabel.column(k, width=lebar[k], anchor="center")

        scrollbar = ttk.Scrollbar(frame_kiri, orient=tk.VERTICAL, command=self.tabel.yview)
        self.tabel.configure(yscrollcommand=scrollbar.set)

        self.tabel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind klik baris
        self.tabel.bind("<<TreeviewSelect>>", self._on_pilih_baris)

        # Tombol di bawah tabel
        frame_tombol = tk.Frame(parent, bg="#f0f4f8")
        frame_tombol.pack(side=tk.BOTTOM, fill=tk.X, pady=(6, 0))

        tk.Button(
            frame_tombol, text="🔄 Refresh",
            bg="#1a73e8", fg="white", font=("Arial", 10, "bold"),
            width=12, command=self._refresh_thread
        ).pack(side=tk.LEFT, padx=4)

        tk.Button(
            frame_tombol, text="✏️ Edit",
            bg="#f9a825", fg="white", font=("Arial", 10, "bold"),
            width=12, command=self._edit_data
        ).pack(side=tk.LEFT, padx=4)

        tk.Button(
            frame_tombol, text="🗑️ Hapus",
            bg="#e53935", fg="white", font=("Arial", 10, "bold"),
            width=12, command=self._hapus_data
        ).pack(side=tk.LEFT, padx=4)

    def _bangun_form(self, parent):
        frame_kanan = tk.Frame(parent, bg="#ffffff", bd=1, relief=tk.RIDGE, padx=14, pady=14)
        frame_kanan.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

        tk.Label(
            frame_kanan, text="Input Data Mahasiswa",
            font=("Arial", 12, "bold"), bg="#ffffff", fg="#1a73e8"
        ).grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Field input
        label_field = ["Nama", "Nilai Tugas", "Nilai UTS", "Nilai UAS"]
        self.entry = {}

        for i, teks in enumerate(label_field):
            tk.Label(
                frame_kanan, text=teks + ":",
                bg="#ffffff", font=("Arial", 10)
            ).grid(row=i + 1, column=0, sticky="w", pady=4)

            kunci = teks.split()[-1].lower()  # nama / tugas / uts / uas
            e = tk.Entry(frame_kanan, font=("Arial", 10), width=18)
            e.grid(row=i + 1, column=1, pady=4, padx=(6, 0))
            self.entry[kunci] = e

        # Tombol Tambah & Batal
        tk.Button(
            frame_kanan, text="➕ Tambah Data",
            bg="#43a047", fg="white", font=("Arial", 10, "bold"),
            width=16, command=self._tambah_data_thread
        ).grid(row=6, column=0, columnspan=2, pady=(12, 4))

        tk.Button(
            frame_kanan, text="✖ Batal / Reset",
            bg="#757575", fg="white", font=("Arial", 10),
            width=16, command=self._reset_form
        ).grid(row=7, column=0, columnspan=2, pady=4)

        # Label status
        self.label_status = tk.Label(
            frame_kanan, text="", bg="#ffffff",
            font=("Arial", 9, "italic"), fg="#555"
        )
        self.label_status.grid(row=8, column=0, columnspan=2, pady=(6, 0))

    # Event Helpers
    def _on_pilih_baris(self, event):
        """Menyimpan indeks baris yang diklik pada tabel."""
        seleksi = self.tabel.selection()
        if seleksi:
            self.indeks_terpilih = self.tabel.index(seleksi[0])
        else:
            self.indeks_terpilih = None

    def _set_status(self, pesan, warna="#555"):
        self.label_status.config(text=pesan, fg=warna)

    def _reset_form(self):
        """Mengosongkan semua field input dan hapus seleksi."""
        for e in self.entry.values():
            e.delete(0, tk.END)
        self.indeks_terpilih = None
        self.tabel.selection_remove(self.tabel.selection())
        self._set_status("")

    # Validasi Input
    def _ambil_input(self):
        """
        Mengambil dan memvalidasi input dari form.
        Mengembalikan (nama, tugas, uts, uas) atau raise ValueError.
        """
        nama = self.entry["nama"].get().strip()
        if not nama:
            raise ValueError("Nama tidak boleh kosong.")

        nilai_raw = {
            "Tugas": self.entry["tugas"].get().strip(),
            "UTS": self.entry["uts"].get().strip(),
            "UAS": self.entry["uas"].get().strip(),
        }

        nilai = {}
        for label, raw in nilai_raw.items():
            try:
                angka = float(raw)
            except ValueError:
                raise ValueError(f"Nilai {label} harus berupa angka.")
            if not (0 <= angka <= 100):
                raise ValueError(f"Nilai {label} harus antara 0 – 100.")
            nilai[label] = angka

        return nama, nilai["Tugas"], nilai["UTS"], nilai["UAS"]

    # Muat / Refresh Tabel
    def muat_data_ke_tabel(self):
        """Membersihkan tabel lalu mengisi ulang dari CSV."""
        # Hapus semua baris yang ada di tabel
        for baris in self.tabel.get_children():
            self.tabel.delete(baris)

        data = db.baca_semua_data()

        # Looping untuk mengisi tabel
        for mahasiswa in data:
            self.tabel.insert("", tk.END, values=(
                mahasiswa.get("Nama", ""),
                mahasiswa.get("Tugas", ""),
                mahasiswa.get("UTS", ""),
                mahasiswa.get("UAS", ""),
                mahasiswa.get("Total", ""),
                mahasiswa.get("Huruf", ""),
            ))

    def _refresh_thread(self):
        """Menjalankan muat_data_ke_tabel di thread terpisah."""
        threading.Thread(target=self._refresh_proses, daemon=True).start()

    def _refresh_proses(self):
        self._set_status("Memuat data…")
        self.muat_data_ke_tabel()
        self._set_status("Data berhasil dimuat.", "#43a047")

    # Tambah Data
    def _tambah_data_thread(self):
        threading.Thread(target=self._tambah_data_proses, daemon=True).start()

    def _tambah_data_proses(self):
        try:
            nama, tugas, uts, uas = self._ambil_input()
            db.tambah_baris_csv(nama, tugas, uts, uas)
            self.muat_data_ke_tabel()
            self._reset_form()
            self._set_status(f"Data '{nama}' berhasil ditambahkan.", "#43a047")
        except ValueError as e:
            messagebox.showwarning("Input Tidak Valid", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Hapus Data
    def _hapus_data(self):
        if self.indeks_terpilih is None:
            messagebox.showwarning("Peringatan", "Pilih baris yang ingin dihapus terlebih dahulu.")
            return

        konfirmasi = messagebox.askyesno("Konfirmasi Hapus", "Yakin ingin menghapus data ini?")
        if not konfirmasi:
            return

        threading.Thread(target=self._hapus_data_proses, daemon=True).start()

    def _hapus_data_proses(self):
        try:
            data = db.baca_semua_data()
            if self.indeks_terpilih < len(data):
                data.pop(self.indeks_terpilih)
                db.simpan_semua_data(data)
                self.indeks_terpilih = None
                self.muat_data_ke_tabel()
                self._set_status("Data berhasil dihapus.", "#e53935")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Edit Data
    def _edit_data(self):
        if self.indeks_terpilih is None:
            messagebox.showwarning("Peringatan", "Pilih baris yang ingin diedit terlebih dahulu.")
            return

        data = db.baca_semua_data()
        if self.indeks_terpilih >= len(data):
            return

        mahasiswa = data[self.indeks_terpilih]

        # Isi form dengan data yang dipilih
        self.entry["nama"].delete(0, tk.END)
        self.entry["nama"].insert(0, mahasiswa.get("Nama", ""))
        self.entry["tugas"].delete(0, tk.END)
        self.entry["tugas"].insert(0, mahasiswa.get("Tugas", ""))
        self.entry["uts"].delete(0, tk.END)
        self.entry["uts"].insert(0, mahasiswa.get("UTS", ""))
        self.entry["uas"].delete(0, tk.END)
        self.entry["uas"].insert(0, mahasiswa.get("UAS", ""))

        self._set_status("Edit data lalu klik 'Simpan Perubahan'.", "#f9a825")

        # Ganti tombol Tambah sementara menjadi Simpan Perubahan
        self._tampilkan_mode_edit()

    def _tampilkan_mode_edit(self):
        """Menampilkan tombol 'Simpan Perubahan' menggantikan 'Tambah Data'."""
        # Cari frame_kanan (parent dari label_status)
        frame_kanan = self.label_status.master

        # Hapus tombol lama lalu buat tombol Simpan
        for widget in frame_kanan.grid_slaves(row=6):
            widget.destroy()

        tk.Button(
            frame_kanan, text="💾 Simpan Perubahan",
            bg="#1a73e8", fg="white", font=("Arial", 10, "bold"),
            width=16, command=self._simpan_perubahan_thread
        ).grid(row=6, column=0, columnspan=2, pady=(12, 4))

    def _kembalikan_tombol_tambah(self):
        """Mengembalikan tombol 'Tambah Data' setelah edit selesai."""
        frame_kanan = self.label_status.master
        for widget in frame_kanan.grid_slaves(row=6):
            widget.destroy()
        tk.Button(
            frame_kanan, text="➕ Tambah Data",
            bg="#43a047", fg="white", font=("Arial", 10, "bold"),
            width=16, command=self._tambah_data_thread
        ).grid(row=6, column=0, columnspan=2, pady=(12, 4))

    def _simpan_perubahan_thread(self):
        threading.Thread(target=self._simpan_perubahan_proses, daemon=True).start()

    def _simpan_perubahan_proses(self):
        try:
            nama, tugas, uts, uas = self._ambil_input()
            total = hitung_total(tugas, uts, uas)
            huruf = hitung_huruf(total)

            data = db.baca_semua_data()
            if self.indeks_terpilih is not None and self.indeks_terpilih < len(data):
                data[self.indeks_terpilih] = {
                    "Nama": nama, "Tugas": tugas, "UTS": uts,
                    "UAS": uas, "Total": total, "Huruf": huruf
                }
                db.simpan_semua_data(data)
                self.muat_data_ke_tabel()
                self._reset_form()
                self._kembalikan_tombol_tambah()
                self._set_status(f"Data '{nama}' berhasil diperbarui.", "#1a73e8")
        except ValueError as e:
            messagebox.showwarning("Input Tidak Valid", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))
