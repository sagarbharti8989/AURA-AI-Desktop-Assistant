"""Unit tests for TTS worker lifecycle."""

import threading

from voice.speech_response import SpeechResponse


def test_tts_worker_is_not_restarted():
    tts = SpeechResponse()
    original = tts._worker_thread

    tts._start_worker()

    assert tts._worker_thread is original
    assert tts._worker_thread.is_alive()

    tts.stop()
    assert tts._stop_event.is_set()
