import asyncio
import edge_tts
import json

TEXT = (
    "Dit wist je nog NIET over je brein... "
    "Stress vermindert je geheugen met wel 40 procent. "
    "Je brein heeft dagelijks de juiste voeding en rust nodig om optimaal te functioneren. "
    "Kleine gewoontes, grote verschillen. "
    "Wat doe jij vandaag voor je mentale gezondheid?"
)

async def get_timestamps():
    communicate = edge_tts.Communicate(TEXT, "nl-NL-FennaNeural", rate="+10%")

    timestamps = []
    audio_bytes = b""

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_bytes += chunk["data"]
        elif chunk["type"] == "SentenceBoundary":
            timestamps.append({
                "sentence": chunk["text"],
                "start":    round(chunk["offset"]   / 10_000_000, 4),
                "duration": round(chunk["duration"]  / 10_000_000, 4),
                "end":      round((chunk["offset"] + chunk["duration"]) / 10_000_000, 4),
            })

    with open("outputs/audio_final.mp3", "wb") as f:
        f.write(audio_bytes)

    with open("outputs/timestamps.json", "w", encoding="utf-8") as f:
        json.dump(timestamps, f, indent=2, ensure_ascii=False)

    total_audio = len(audio_bytes)
    print(f"Ses dosyasi kaydedildi: outputs/audio_final.mp3 ({total_audio // 1024} KB)")
    print(f"Toplam {len(timestamps)} cumle timestamp alindi\n")

    for t in timestamps:
        print(f"  [{t['start']:5.2f}s - {t['end']:5.2f}s]  \"{t['sentence']}\"")

asyncio.run(get_timestamps())
