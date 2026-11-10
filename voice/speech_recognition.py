"""
Speech Recognition module for AURA.
Transcribes audio using Faster-Whisper with CPU int8 quantization.
"""

from typing import Optional, Tuple
import numpy as np
from config import config
from utils.logger import logger
from utils.exceptions import SpeechRecognitionError

# ---------------------------------------------------------------------------
# Helper: trim near‑silence from the beginning and end of the audio buffer.
# ---------------------------------------------------------------------------
def _trim_silence(sig: np.ndarray, thresh: float = 0.02) -> np.ndarray:
    """Remove leading/trailing samples whose absolute amplitude is below `thresh`."""
    idx = np.where(np.abs(sig) > thresh)[0]
    return sig[idx[0]: idx[-1] + 1] if idx.size else np.array([], dtype=sig.dtype)


class SpeechRecognizer:
    """Manages Faster-Whisper model lifecycle and audio transcription."""

    def __init__(self) -> None:
        self.model_size = config.whisper_model
        self.device = config.whisper_device
        self.compute_type = config.whisper_compute_type
        self._model = None

    def _load_model(self) -> None:
        """Loads Faster-Whisper model lazily."""
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
                logger.info(
                    f"Loading Faster-Whisper model ({self.model_size}, {self.device}, {self.compute_type})..."
                )
                self._model = WhisperModel(
                    self.model_size, device=self.device, compute_type=self.compute_type
                )
                logger.info("Faster-Whisper model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load Faster-Whisper model: {e}")
                raise SpeechRecognitionError(f"Could not load STT engine: {e}") from e

    def prewarm(self) -> None:
        """Preloads model in background so first command has zero load lag."""
        try:
            self._load_model()
        except Exception as e:
            logger.warning(f"STT prewarm failed: {e}")

    def transcribe(self, audio: np.ndarray) -> Tuple[bool, str, str]:
        """
        Transcribes audio array with automatic gain normalization and VAD filtering.
        Returns (success, transcribed_text, language).
        """
        if audio is None or audio.size < 1600:  # Need at least 0.1s
            logger.debug("Transcription skipped: Audio buffer is too short (< 0.1s).")
            return False, "", "en"

        duration_sec = len(audio) / 16000.0
        peak_amp = float(np.max(np.abs(audio))) if audio.size > 0 else 0.0
        logger.info(f"Transcribing {duration_sec:.2f}s of audio (peak amplitude: {peak_amp:.6f})...")

        # Digital silence check (only skip if truly zero or pure noise floor)
        if peak_amp < 0.00001:
            logger.info("Transcription skipped: Microphone recorded near-zero amplitude (check if mic is unmuted).")
            return False, "", "en"

        # Gain normalization: boost quiet laptop microphones to 0.7 max amplitude (allow up to 30×)
        if peak_amp > 0:
            scale = min(0.7 / peak_amp, 30.0)
            audio = np.clip(audio * scale, -1.0, 1.0)

        # Trim tiny silence before feeding Whisper (helps short utterances)
        audio = _trim_silence(audio, thresh=0.02)

        try:
            self._load_model()
            segments, info = self._model.transcribe(
                audio,
                beam_size=5,
                language="en",
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500),
            )
            text_parts = [segment.text.strip() for segment in segments]
            full_text = " ".join(text_parts).strip()
            logger.info(f"Transcribed speech ({info.language}, prob {info.language_probability:.2f}): '{full_text}'")
            return bool(full_text), full_text, info.language
        except Exception as e:
            logger.error(f"Speech transcription failed: {e}", exc_info=True)
            return False, "", "en"

    def unload(self) -> None:
        """Releases Whisper model from memory."""
        self._model = None
        logger.info("Faster-Whisper model unloaded.")


speech_recognizer = SpeechRecognizer()
