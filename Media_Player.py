import time
import os
import vlc
from threading import Thread

class AlarmSystem:
    def __init__(self):
        os.add_dll_directory(r'C:\Program Files\VideoLAN\VLC')
        self.alarm_duration = 3  # seconds
        self.is_playing = False
        self.media = None

    def play_alarm(self):
        """Play alarm in a separate thread to avoid blocking the main GUI"""
        if not self.is_playing:
            Thread(target=self._play_alarm_thread).start()

    def _play_alarm_thread(self):
        try:
            self.is_playing = True
            self.media = vlc.MediaPlayer('alarmbak.wav')
            self.media.play()

            timeout = time.time() + self.alarm_duration
            while time.time() < timeout:
                time.sleep(0.1)
                if not self.is_playing:  # Check if we should stop early
                    break

            self.media.stop()
            self.is_playing = False
            self.media = None
        except Exception as e:
            print(f"Error playing alarm: {e}")
            self.is_playing = False

    def stop_alarm(self):
        """Stop the currently playing alarm"""
        self.is_playing = False
        if self.media:
            self.media.stop()
            self.media = None

    def set_duration(self, seconds):
        """Set the duration for how long the alarm should play"""
        self.alarm_duration = seconds
