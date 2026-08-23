import re  # Modul regex untuk membersihkan karakter saat membuat nama file

import sys  # Modul sys untuk exit code program (sys.exit)

from pathlib import Path  # Path untuk mengelola path folder/file secara aman lintas OS

import agent_rpp  # Modul utama berisi logika pembuatan RPP (diimport untuk dipakai nanti)

import ollama_client as oc  # Client Ollama, di-alias "oc" agar penulisan lebih pendek

OUTPUT_DIR = Path("output")  # Folder output tempat file RPP hasil generate disimpan


def tanya(label, default):  # Fungsi utilitas untuk bertanya ke user via terminal
    jawab = input(f"{label} [{default}] :").strip()  # Tampilkan label + nilai default, baca jawaban, buang spasi
    return jawab or default  # Jika user kosongkan (Enter saja), kembalikan nilai default


def nama_file(mapel, topik):  # Fungsi membentuk nama file dari mapel + topik
    slug = re.sub(r"[^a-z0-9]+", "-", f"{mapel} {topik}".lower()).strip("-")  # Lowercase, ganti non-alphanumeric jadi "-", buang "-" di ujung
    return OUTPUT_DIR / f"rpp-{slug[:60]}.md"  # Hasil: output/rpp-{slug maksimal 60 karakter}.md


def main():  # Fungsi titik masuk (entry point) program
    try:  # Coba cek koneksi ke server Ollama
        oc.ping()  # Panggil ping(); jika sukses akan print "[OK] Koneksi berhasil..."
    except oc.OllamaError as exc:  # Jika server Ollama tidak bisa dihubungi
        print(f"[GAGAL] {exc}")  # Tampilkan pesan error yang informatif
        return 1  # Exit code 1 = program berhenti dengan error
    
    print("=== PENYUSUNAN RPP ===\n")  # Judul program di terminal (\n = baris kosong ekstra)
    mapel = tanya("Mata pelajaran", "Matematika")  # Tanya mata pelajaran; Enter = pakai default
    kelas = tanya("Kelas", "VII SMP")  # Tanya jenjang/kelas sasaran
    topik = tanya("Topik", "Bilangan Bulat")  # Tanya topik materi yang akan diajarkan
    waktu = tanya("Alokasi waktu", "2 x 40 menit")  # Tanya alokasi waktu pembelajaran
    
    print("\nMenyusun RPP...\n" + "-" * 60)  # Info mulai proses + garis pemisah 60 karakter
    potongan = []  # List penampung setiap potongan teks hasil streaming
    
    try:
        for teks in agent_rpp.susun_rpp(mapel, kelas, topik, waktu, stream=True):  # Generate RPP streaming (teks muncul bertahap)
            print(teks, end="", flush=True)  # Cetak potongan tanpa newline; flush agar langsung tampil real-time
            potongan.append(teks)  # Simpan potongan agar bisa digabung jadi satu dokumen nanti
    except oc.OllamaError as exc:
        print(f"\n[GAGAL] {exc}")  # Gagal saat generate (server mati/model tidak ada) → berhenti
        return 1
        
    OUTPUT_DIR.mkdir(exist_ok=True)  # Buat folder output/ jika belum ada (tanpa error jika sudah ada)
    berkas = nama_file(mapel, topik)  # Bentuk path file tujuan dari mapel + topik
    berkas.write_text("".join(potongan), encoding="utf-8")  # Gabungkan semua potongan, simpan sebagai file Markdown
    print("\n" + "-" * 60)  # Garis pemisah penutup
    print(f"Tersimpan di: {berkas}")  # Info lokasi file RPP hasil generate
    return 0  # Exit code 0 = program sukses

if __name__ == "__main__":  # Hanya jalan jika file dieksekusi langsung (python main.py), bukan diimport
    sys.exit(main())  # Jalankan main() dan jadikan return value sebagai exit code program