import ollama_client as oc

SYSTEM_PROMPT = """Kamu adalah asisten guru yang menyusun RPP (Rencana Pelaksanaan
Pembelajaran) sesuai Kurikulum Merdeka. Tulis dalam bahasa Indonesia yang baku,
format Markdown, dengan struktur:

1. Identitas (mata pelajaran, kelas/fase, alokasi waktu)
2. Capaian Pembelajaran
3. Tujuan Pembelajaran
4. Profil Pelajar Pancasila yang dikembangkan
5. Materi Pokok
6. Media dan Sumber Belajar
7. Langkah Pembelajaran (Pendahuluan, Inti, Penutup) lengkap dengan alokasi menit
8. Asesmen (diagnostik, formatif, sumatif) beserta rubrik singkat

Isi harus konkret dan langsung bisa dipakai, bukan template kosong."""

def susun_rpp(mata_pelajaran, kelas, topik, alokasi_waktu, stream=True):
    """Hasilkan RPP. Jika stream=True, mengembalikan generator potongan teks."""
    
    permintaan = (
        f"Susun RPP untuk:\n"
        f"- Mata pelajaran: {mata_pelajaran}\n"
        f"- Kelas: {kelas}\n"
        f"- Topik: {topik}\n"
        f"- Alokasi waktu: {alokasi_waktu}"
    )
    
    return oc.chat(
        [
            {"role" : "system", "content" : SYSTEM_PROMPT},
            {"role" : "user", "content" : permintaan},
        ],
        stream = stream
    )