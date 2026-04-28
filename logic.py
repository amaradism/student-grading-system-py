def hitung_total(tugas, uts, uas):
    """Menghitung nilai total: Tugas 20% + UTS 30% + UAS 50%"""
    return tugas * 0.2 + uts * 0.3 + uas * 0.5


def hitung_huruf(total):
    """Mengkonversi nilai total ke nilai huruf."""
    if total > 80:
        return "A"
    elif total > 66:
        return "B"
    elif total > 56:
        return "C"
    elif total > 45:
        return "D"
    else:
        return "E"
