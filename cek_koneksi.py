import sys

from config import OLLAMA_HOST, OLLAMA_MODEL
import ollama_client as oc


def main():
    print(f"Host   : {OLLAMA_HOST}")
    print(f"Model  : {OLLAMA_MODEL}")

    try:
        print(f"Versi  : {oc.ping()}")
    except oc.OllamaError as exc:
        print(f"\n[GAGAL] {exc}")
        return 1

    models = oc.list_models()
    print(f"Model tersedia: {', '.join(models)}")

    if OLLAMA_MODEL not in models:
        print(
            f"\n[GAGAL] Model '{OLLAMA_MODEL}' belum ada. "
            f"Jalankan: ollama pull {OLLAMA_MODEL}"
        )
        return 1

    print("\nTes generate...")
    jawaban = oc.chat([{"role": "user", "content": "Balas dengan satu kata: OK"}])
    print(f"Jawaban: {jawaban.strip()}")
    print("\n[BERHASIL] API Ollama siap dipakai.")
    return 0


if __name__ == "__main__":
    sys.exit(main())