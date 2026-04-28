import csv
import os
from logic import hitung_total, hitung_huruf

FILE_CSV = "student_database.csv"
HEADER_CSV = ["Nama", "Tugas", "UTS", "UAS", "Total", "Huruf"]


def inisialisasi_csv():
    """Membuat file CSV dengan header jika belum ada."""
    if not os.path.exists(FILE_CSV):
        with open(FILE_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(HEADER_CSV)


def baca_semua_data():
    """Membaca semua baris data dari file CSV (kecuali header)."""
    data = []
    try:
        with open(FILE_CSV, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for baris in reader:
                data.append(baris)
    except FileNotFoundError:
        pass
    return data


def simpan_semua_data(list_data):
    """Menimpa seluruh isi CSV dengan data baru (dipakai saat edit/hapus)."""
    with open(FILE_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADER_CSV)
        writer.writeheader()
        for baris in list_data:
            writer.writerow(baris)


def tambah_baris_csv(nama, tugas, uts, uas):
    """Menambahkan satu baris baru ke file CSV."""
    total = hitung_total(tugas, uts, uas)
    huruf = hitung_huruf(total)
    with open(FILE_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADER_CSV)
        writer.writerow({
            "Nama": nama,
            "Tugas": tugas,
            "UTS": uts,
            "UAS": uas,
            "Total": total,
            "Huruf": huruf
        })
