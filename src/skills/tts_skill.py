import os
import asyncio
import edge_tts

_OUTPUT_DIR = "outputs"
_DEFAULT_VOICE = "nl-NL-FennaNeural"
_DEFAULT_RATE = "+10%"


async def _generate(text: str, output_path: str, voice: str, rate: str) -> None:
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(output_path)


def generate_dutch_audio(
    text: str,
    filename: str,
    voice: str = _DEFAULT_VOICE,
    rate: str = _DEFAULT_RATE,
) -> str:
    """
    Convert text to Dutch speech using edge-tts.
    Saves the result as an MP3 in the outputs/ folder.
    Returns the full path to the saved file.
    """
    os.makedirs(_OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(_OUTPUT_DIR, filename)
    asyncio.run(_generate(text, output_path, voice, rate))
    print(f"[tts_skill] Audio saved: {output_path} | voice={voice} | rate={rate}")
    return output_path


if __name__ == "__main__":
    test_text = (
        "Wist je dat stress je geheugen met wel 40% kan verminderen? "
        "Je brein heeft dagelijks de juiste voeding en rust nodig om optimaal te functioneren. "
        "Kleine gewoontes, grote verschillen. "
        "Wat doe jij vandaag voor je mentale gezondheid?"
    )

    path = generate_dutch_audio(test_text, "test_audio_v3.mp3")
    print(f"[tts_skill] Test geslaagd: {path} ({os.path.getsize(path)} bytes)")
