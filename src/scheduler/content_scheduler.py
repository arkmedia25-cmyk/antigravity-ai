import time
import datetime
import threading
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

# Global flag to stop scheduler if needed
_STOP_SCHEDULER = False

def start_content_factory(chat_id):
    """
    Automated Content Factory:
    Triggers content generation for both brands at Dutch Peak Hours (CET).
    GlowUp: 07:45 AM & 08:15 PM
    Holisti: 12:30 PM & 09:00 PM
    """
    def run_scheduler():
        print(f"[Scheduler] Content Factory started for Chat ID: {chat_id}")
        while not _STOP_SCHEDULER:
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M")
            
            # --- GLOWUP SCHEDULE ---
            if current_time == "07:45":
                print("[Scheduler] Triggering Morning GlowUp Package...")
                from skills.automation.telegram_handler import _generate_and_send_video
                threading.Thread(target=_generate_and_send_video, args=(chat_id, "Sabah enerjisi ve sağlıklı başlangıçlar", "glow")).start()
                time.sleep(65) # Avoid double triggering
                
            elif current_time == "20:15":
                print("[Scheduler] Triggering Evening GlowUp Package...")
                from skills.automation.telegram_handler import _generate_and_send_video
                threading.Thread(target=_generate_and_send_video, args=(chat_id, "Gün sonu yenilenme ve güzellik uykusu", "glow")).start()
                time.sleep(65)

            # --- HOLISTIGLOW SCHEDULE ---
            elif current_time == "12:30":
                print("[Scheduler] Triggering Lunch HolistiGlow Package...")
                from skills.automation.telegram_handler import _generate_and_send_video
                threading.Thread(target=_generate_and_send_video, args=(chat_id, "Öğle arası wellness ve dengeli yaşam", "holisti")).start()
                time.sleep(65)
                
            elif current_time == "21:00":
                print("[Scheduler] Triggering Night HolistiGlow Package...")
                from skills.automation.telegram_handler import _generate_and_send_video
                threading.Thread(target=_generate_and_send_video, args=(chat_id, "Gece huzuru ve bütünsel sağlık ritüelleri", "holisti")).start()
                time.sleep(65)

            time.sleep(30) # Check every 30 seconds

    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
    return thread
