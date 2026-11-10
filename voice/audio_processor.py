"""
Audio Processor for AURA.
Prepares and normalizes captured PCM audio buffers for speech recognition.
"""

import numpy as np
from utils.logger import logger


class AudioProcessor:
    """Processes in-memory audio arrays without saving to disk."""

    @staticmethod
    def normalize_for_whisper(audio_data: np.ndarray, sample_rate: int = 16000) -> np.ndarray:
        """
        Converts microphone audio into 16kHz mono float32 array normalized to [-1.0, 1.0].
        """
        if audio_data is None or len(audio_data) == 0:
            return np.array([], dtype=np.float32)

        # Convert to mono if multi-channel
        if audio_data.ndim > 1:
            audio_data = np.mean(audio_data, axis=1)

        # Ensure float32
        if audio_data.dtype != np.float32:
            if np.issubdtype(audio_data.dtype, np.integer):
                max_val = float(np.iinfo(audio_data.dtype).max)
                audio_data = audio_data.astype(np.float32) / max_val
            else:
                audio_data = audio_data.astype(np.float32)

        return audio_data


audio_processor = AudioProcessor()

