"""
Text-to-Speech Response Engine for AURA.
Strategy: pyttsx3.save_to_file -> winsound.PlaySound (avoids SPERR_DEVICE_BUSY 0x8004503A)
Fallback: PowerShell speak.ps1
"""

import os
import queue
import subprocess
import tempfile
import threading
import winsound
from typing import Optional

from config import config
from utils.logger import logger

_PS1_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "utils", "speak.ps1")
)


class SpeechResponse:
    """Non-blocking TTS worker that speaks after every command."""

    def __init__(self) -> None:
        self.rate = config.voice_rate
        self.volume = config.voice_volume
        self._queue: queue.Queue = queue.Queue(maxsize=200)
        self._stop_event = threading.Event()
        self._worker_thread: Optional[threading.Thread] = None
        self._start_worker()

    def _start_worker(self) -> None:
        self._worker_thread = threading.Thread(target=self._run_tts_loop, daemon=True)
        self._worker_thread.start()

    # ------------------------------------------------------------------
    # Strategy 1: pyttsx3 save-to-WAV + winsound
    # ------------------------------------------------------------------

    def _speak_via_wav(self, text: str) -> bool:
        """
        Render speech to a temporary WAV file with pyttsx3 (uses SAPI SpFileStream,
        which does NOT touch the audio output device), then play the file with
        winsound to avoid SPERR_DEVICE_BUSY (0x8004503A).
        Returns True on success.
        """
        tmp_path = None
        try:
            import pyttsx3
            engine = pyttsx3.init("sapi5")
            engine.setProperty("rate", self.rate)
            engine.setProperty("volume", self.volume)

            # Save to temp WAV (no audio device involved)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                tmp_path = f.name

            engine.save_to_file(text, tmp_path)
            engine.runAndWait()
            engine.stop()

            # Play the WAV file synchronously
            winsound.PlaySound(tmp_path, winsound.SND_FILENAME)
            return True

        except Exception as e:
            logger.warning(f"TTS WAV strategy failed: {e}")
            return False
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

    # ------------------------------------------------------------------
    # Strategy 2: PowerShell speak.ps1 (last resort)
    # ------------------------------------------------------------------

    def _speak_via_ps1(self, text: str) -> None:
        if not os.path.exists(_PS1_PATH):
            logger.warning("TTS speak.ps1 not found.")
            return
        try:
            subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass",
                 "-File", _PS1_PATH, "-text", text],
                timeout=30,
                check=False,
            )
        except Exception as e:
            logger.warning(f"TTS speak.ps1 error: {e}")

    # ------------------------------------------------------------------
    # Worker loop
    # ------------------------------------------------------------------

    def _run_tts_loop(self) -> None:
        """Daemon thread: consume the queue and speak each item."""
        try:
            import pythoncom
            pythoncom.CoInitialize()
        except Exception:
            pass

        while not self._stop_event.is_set():
            try:
                text = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if text is None:
                break

            logger.info(f"TTS Speaking: '{text}'")

            if not self._speak_via_wav(text):
                self._speak_via_ps1(text)

            self._queue.task_done()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def speak(self, text: str) -> None:
        """Queues text to be spoken asynchronously."""
        if not text or not text.strip():
            return
        try:
            self._queue.put_nowait(text.strip())
        except queue.Full:
            logger.warning("TTS queue full; dropping message.")

    def stop(self) -> None:
        """Signals the worker thread to exit."""
        self._stop_event.set()
        self._queue.put(None)


speech_response = SpeechResponse()
