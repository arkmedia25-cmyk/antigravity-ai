import os
import time
import threading
import datetime
from src.core.logging import get_logger

logger = get_logger("core.health_monitor")

class HealthMonitor:
    def __init__(self, heartbeat_path="outputs/heartbeat.txt"):
        self.heartbeat_path = heartbeat_path
        self.is_running = False
        self._thread = None
        
        # Ensure outputs dir exists
        os.makedirs(os.path.dirname(self.heartbeat_path), exist_ok=True)

    def start(self):
        if self.is_running: return
        self.is_running = True
        self._thread = threading.Thread(target=self._run, name="HealthMonitorThread", daemon=True)
        self._thread.start()
        logger.info("✅ Health Monitor (Watchdog) started.")

    def stop(self):
        self.is_running = False
        if self._thread:
            self._thread.join(timeout=1.0)

    def _run(self):
        while self.is_running:
            try:
                # Update heartbeat file with current timestamp
                with open(self.heartbeat_path, "w") as f:
                    f.write(datetime.datetime.now().isoformat())
                
                # Check for critical system stats if needed (memory, disk)
                # ...
                
                time.sleep(60) # Update every minute
            except Exception as e:
                logger.error(f"Health Monitor Loop Error: {e}")
                time.sleep(10)

# Global singleton
health_monitor = HealthMonitor()
