"""
Microphone Manager for AURA.
Captures push-to-talk audio using sounddevice.
No audio is permanently written to disk.
"""

import threading
from typing import Optional, List
import numpy as np
import sounddevice as sd
from voice.audio_processor import audio_processor
from utils.logger import logger
from utils.exceptions import MicrophoneError


class MicrophoneManager:
    """Manages audio capture for Push-to-Talk interactions."""

    def __init__(self, sample_rate: int = 16000) -> None:
        self.sample_rate = sample_rate
        self.channels = 1
        self.is_recording = False
        self._audio_chunks: List[np.ndarray] = []
        self._stream: Optional[sd.InputStream] = None
        self._lock = threading.Lock()

    def _audio_callback(self, indata, frames, time_info, status) -> None:
        """Callback invoked by sounddevice for each audio block."""
        if status:
            logger.debug(f"Audio stream status: {status}")
        with self._lock:
            if self.is_recording:
                self._audio_chunks.append(indata.copy())

    def start_recording(self) -> None:
        """Begins in-memory audio recording."""
        try:
            with self._lock:
                self._audio_chunks = []
                self.is_recording = True

            if self._stream is None:
                self._stream = sd.InputStream(
                    samplerate=self.sample_rate,
                    channels=self.channels,
                    dtype="float32",
                    callback=self._audio_callback,
                )
                self._stream.start()
            logger.info("Microphone recording started.")
        except Exception as e:
            self.is_recording = False
            logger.error(f"Failed to start audio recording: {e}")
            raise MicrophoneError(f"Could not open microphone: {e}") from e

    def stop_recording(self) -> np.ndarray:
        """Stops recording and returns normalized audio array."""
        try:
            with self._lock:
                self.is_recording = False
                chunks = self._audio_chunks
                self._audio_chunks = []

            if self._stream:
                self._stream.stop()
                self._stream.close()
                self._stream = None

            if not chunks:
                return np.array([], dtype=np.float32)

            concatenated = np.concatenate(chunks, axis=0)
            normalized = audio_processor.normalize_for_whisper(concatenated, self.sample_rate)
            logger.info(f"Microphone recording stopped. Captured {len(normalized)} samples.")
            return normalized
        except Exception as e:
            logger.error(f"Error stopping audio recording: {e}")
            return np.array([], dtype=np.float32)

    def release(self) -> None:
        """Releases audio stream."""
        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None


microphone_manager = MicrophoneManager()

