import json  # Modul json (disiapkan untuk parsing/serialisasi data JSON)

import requests  # Library HTTP untuk mengirim request ke server Ollama

from config import OLLAMA_HOST, OLLAMA_MODEL, OLLAMA_TEMPERATURE, OLLAMA_TIMEOUT  # Ambil konfigurasi dari config.py


class OllamaError(RuntimeError):  # Custom exception khusus error Ollama
    """Dilempar saat server Ollama tidak bisa dihubungi atau menolak permintaan."""


def _url(path):  # Fungsi helper (awalan _ = internal) untuk membentuk URL
    """Membentuk URL lengkap dari alamat host dan path endpoint API."""
    # Gabungkan host + path, contoh: http://localhost:11434/api/version
    return f"{OLLAMA_HOST}{path}"  


def ping():  # Fungsi untuk mengecek apakah server Ollama hidup
    """Cek server hidup. Mengembalikan versi Ollama."""
    try:  # Coba blok berikut; jika gagal akan ditangkap oleh except
        r = requests.get(_url("/api/version"), timeout=5)  # Kirim GET ke endpoint /api/version, maksimal tunggu 5 detik
        r.raise_for_status()  # Jika status HTTP error (4xx/5xx), lempar exception
    except requests.RequestException as exc:  # Tangkap semua error jaringan/HTTP dari requests
        raise OllamaError(  # Bungkus ulang error sebagai OllamaError agar mudah ditangani pemanggil
            f"Tidak bisa menghubungi Ollama di {OLLAMA_HOST}. "  # Pesan error bagian 1: alamat host
            "Pastikan server jalan (`ollama serve` atau buka aplikasi Ollama)."  # Pesan error bagian 2: saran solusi
        ) from exc  # `from exc` menyimpan error asli sebagai penyebab (traceback tetap terlihat)
    version = r.json().get("version", "unknown")  # Parse respons JSON dan ambil field "version" (fallback: "unknown")
    print(f"[OK] Koneksi berhasil ke Ollama di {OLLAMA_HOST} (versi {version})")  # Info sukses koneksi ke terminal
    return version  # Kembalikan versi Ollama ke pemanggil

def chat(messages, model=None, temperature=None, stream=False):  # Fungsi utama kirim percakapan ke model
    """Kirim percakapan ke /api/chat. messages: list of {"role": "system"|"user"|"assistant", "content": str}
    Jika stream=True, mengembalikan generator potongan teks.
    """
    
    payload = {  # Data JSON yang akan dikirim ke API Ollama
        "model": model or OLLAMA_MODEL,  # Pakai parameter `model` jika diberikan, jika None pakai default dari config
        "messages": messages,  # Riwayat percakapan: list dict {"role": ..., "content": ...}
        "stream": stream,  # True = respons dikirim bertahap (streaming), False = sekali utuh
        "options": {
            "temperature": OLLAMA_TEMPERATURE if temperature is None else temperature  # Kreativitas model: parameter atau default config
        }
    }
    
    try:
        r = requests.post(  # Kirim POST berisi payload JSON ke endpoint /api/chat
            _url("/api/chat"), json=payload, timeout=OLLAMA_TIMEOUT, stream=stream
        )
        r.raise_for_status()  # Status HTTP 4xx/5xx → lempar exception
    except requests.HTTPError as exc:  # Server menjawab tapi menolak permintaan (model tidak ada, format salah, dll)
        raise OllamaError(f"Ollama menolak permintaan: {r.status_code} {r.text}") from exc  # Bungkus jadi OllamaError + detail respons
    except requests.RequestException as exc:  # Error jaringan lain: timeout, koneksi putus, DNS gagal, dll
        raise OllamaError(f"Gagal memanggil Ollama: {exc}") from exc  # Bungkus jadi OllamaError
    
    if not stream:
        return r.json()["message"]["content"]  # Mode biasa: ambil jawaban lengkap dari field message.content
    return _iter_stream(r)  # Mode streaming: kembalikan generator yang menghasilkan potongan teks

def _iter_stream(response):  # Helper internal untuk membaca respons streaming baris demi baris
    for line in response.iter_lines():  # Ulangi setiap baris JSON yang dikirim server secara bertahap
        if not line:
            continue  # Lewati baris kosong (keep-alive/pemisah)
        chunk = json.loads(line)  # Parse satu baris JSON menjadi dictionary
        if chunk.get("done"):
            break  # Field "done": true artinya respons selesai → hentikan loop
        yield chunk["message"]["content"]  # `yield` = generator: serahkan potongan teks ke pemanggil tanpa menahan semuanya di memori
