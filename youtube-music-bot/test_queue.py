"""
4 kanalın kısa test videolarını sırayla üretir ve private yükler.
Kullanım: python test_queue.py
"""
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

CHANNELS = ["neonpulse", "sleepwave", "healingflow", "binauralmind"]
LOG_DIR = Path("logs")


def run_test(slug: str) -> bool:
    log_file = LOG_DIR / f"test_{slug}.log"
    LOG_DIR.mkdir(exist_ok=True)

    print(f"\n{'='*50}")
    print(f"TEST: {slug} — {datetime.now().strftime('%H:%M:%S')}")

    start = time.time()
    with open(log_file, "w") as log:
        log.write(f"--- TEST {slug} {datetime.now()} ---\n")
        result = subprocess.run(
            [sys.executable, "-u", "test_runner.py", "--channel", slug],
            stdout=log, stderr=log,
        )

    elapsed = int(time.time() - start)
    mins, secs = elapsed // 60, elapsed % 60

    if result.returncode == 0:
        print(f"✅ {slug} tamamlandı — {mins}dk {secs}s")
        # Son satırı göster (video URL)
        lines = log_file.read_text().strip().splitlines()
        for line in reversed(lines):
            if "youtu.be" in line or "Tamamlandı" in line:
                print(f"   {line.strip()}")
                break
        return True
    else:
        print(f"❌ {slug} HATA — log: {log_file}")
        lines = log_file.read_text().strip().splitlines()
        for line in lines[-5:]:
            print(f"   {line}")
        return False


def main():
    print(f"\n🧪 4 Kanal Test Başlıyor — {datetime.now().strftime('%H:%M:%S')}")
    print(f"Sıra: {' → '.join(CHANNELS)}")
    print("Tüm videolar PRIVATE yüklenecek.\n")

    results = {}
    for slug in CHANNELS:
        results[slug] = run_test(slug)

    print(f"\n{'='*50}")
    print(f"TEST ÖZET — {datetime.now().strftime('%H:%M:%S')}")
    for slug, ok in results.items():
        print(f"  {'✅' if ok else '❌'} {slug}")

    print("\nVideoları YouTube Studio'da kontrol et, beğenince 'Public' yap.")


if __name__ == "__main__":
    main()
