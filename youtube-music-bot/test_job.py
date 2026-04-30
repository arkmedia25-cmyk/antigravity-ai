import subprocess
from pathlib import Path

def merge_video(bg_video: Path, audio_path: Path, output_path: Path, duration: int = 15):
    print(f"\nFFMPEG ile birlestiriliyor (Test icin {duration} saniyelik bir kesit)...")
    
    # Botun video_build.py'sinde kullandığı FFMPEG komutunun aynısı (waveform ve çözünürlük ayarları dahil)
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", str(bg_video),
        "-i", str(audio_path),
        "-filter_complex", 
        "[0:v]scale=1920:-2,crop=1920:1080,setsar=1,eq=saturation=1.1[bg];"
        "[1:a]showwaves=s=1920x250:mode=cline:colors=0x00FFFF@0.8|0xFF00FF@0.5[wave];"
        "[bg][wave]overlay=0:830[out]",
        "-map", "[out]",
        "-map", "1:a",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "26",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(duration),
        "-shortest",
        str(output_path)
    ]
    
    print("Calistirilan komut:", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"\n>>> Test klibi basariyla olusturuldu: {output_path} <<<")
        print("Bu klibi acarak ses, hareketli arka plan ve ses dalgasini (waveform) test edebilirsiniz.")
    else:
        print(f"\nFFMPEG hatasi:\n{result.stderr}")

if __name__ == "__main__":
    # Neonpulse kanalı için enerji dolu EDM nişini seçiyoruz
    bg_video_path = Path("channels/neonpulse/backgrounds/bg_energy-edm.mp4")
    
    # Sistemde üretilmiş mevcut final.mp3 sesini kullanıyoruz
    audio_src = Path("output/final.mp3")
    
    final_output = Path("test_final.mp4")

    if not bg_video_path.exists():
        print(f"Hata: Arka plan videosu bulunamadı -> {bg_video_path}")
        exit(1)
        
    if not audio_src.exists():
        print(f"Hata: Ses dosyası bulunamadı -> {audio_src}")
        exit(1)

    merge_video(bg_video_path, audio_src, final_output, duration=15)
