"""
Central Assistant Coordinator for AURA.
Orchestrates the entire voice-to-action-to-speech lifecycle.
"""

import threading
from typing import Optional
from utils.constants import AssistantState
from utils.helpers import generate_request_id
from utils.logger import logger

from core.state_manager import state_manager
from core.event_manager import event_manager
from voice.microphone import microphone_manager
from voice.speech_recognition import speech_recognizer
from voice.speech_response import speech_response
from intelligence.intent_classifier import intent_classifier
from intelligence.context_manager import context_manager
from security.request_validator import ActionRequest, ActionResponse
from security.permission_manager import permission_manager
from controllers.action_dispatcher import action_dispatcher


class Assistant:
    """Central orchestrator for AURA."""

    def __init__(self) -> None:
        self.state_manager = state_manager
        self.event_manager = event_manager
        self.mic = microphone_manager
        self.stt = speech_recognizer
        self.tts = speech_response
        # Ensure the TTS worker thread is running (no‑op if already started)
        if not getattr(self.tts, "_worker_thread", None):
            self.tts._start_worker()
        self.classifier = intent_classifier
        self.context = context_manager
        self.permission = permission_manager
        self.dispatcher = action_dispatcher
        # Pre-warm STT model asynchronously so first voice command is instant
        threading.Thread(target=self.stt.prewarm, daemon=True).start()

    def start_listening(self) -> None:
        """Starts Push-to-Talk audio capture."""
        if not self.state_manager.can_listen():
            logger.warning("Cannot start listening: assistant is busy.")
            return

        try:
            self.state_manager.set_state(AssistantState.LISTENING)
            self.event_manager.emit("LISTENING_STARTED")
            self.mic.start_recording()
        except Exception as e:
            logger.error(f"Failed to start listening: {e}")
            self.state_manager.set_state(AssistantState.ERROR)
            self.event_manager.emit("ERROR", str(e))

    def stop_listening(self) -> None:
        """Stops Push-to-Talk recording and processes audio in background thread."""
        if not self.state_manager.is_listening():
            return

        self.state_manager.set_state(AssistantState.PROCESSING)
        self.event_manager.emit("LISTENING_STOPPED")

        audio_data = self.mic.stop_recording()

        # Run speech recognition and execution in worker thread
        threading.Thread(
            target=self._process_pipeline_worker,
            args=(audio_data,),
            daemon=True,
        ).start()

    def process_text_command(self, text: str) -> ActionResponse:
        """Direct text-based entry point for UI or testing."""
        return self._execute_command_pipeline(text)

    def _process_pipeline_worker(self, audio_data) -> None:
        """Background thread executing speech-to-action."""
        try:
            success, transcript, _ = self.stt.transcribe(audio_data)

            if not success or not transcript:
                logger.info("No speech detected or empty audio.")
                msg = "I didn't catch that. Could you repeat?"
                self.event_manager.emit("TRANSCRIPTION_FAILED", msg)
                self.tts.speak(msg)
                self.state_manager.set_state(AssistantState.IDLE)
                return

            self.event_manager.emit("TRANSCRIPTION_COMPLETED", transcript)
            self._execute_command_pipeline(transcript)
        except Exception as e:
            logger.error(f"Error in processing pipeline: {e}", exc_info=True)
            self.state_manager.set_state(AssistantState.ERROR)
            self.event_manager.emit("ERROR", str(e))
        finally:
            self.state_manager.set_state(AssistantState.IDLE)

    def _execute_command_pipeline(self, raw_text: str) -> ActionResponse:
        """Processes text through resolution, validation, dispatch, and feedback."""
        req_id = generate_request_id()

        # 1. Resolve context ("it", etc.)
        resolved_text = self.context.resolve_reference(raw_text)

        # 2. Classify intent
        intent, params, refusal = self.classifier.classify(resolved_text)

        if refusal:
            # Policy refusal (power termination or personal file access)
            logger.warning(f"Command blocked: '{raw_text}' -> {refusal}")
            self.event_manager.emit("COMMAND_REFUSED", {"text": raw_text, "message": refusal})
            self.tts.speak(refusal)
            return ActionResponse(
                request_id=req_id,
                intent="blocked",
                success=False,
                verified=True,
                message=refusal,
            )

        if not intent:
            msg = "I could not find a supported action for that instruction."
            self.event_manager.emit("COMMAND_UNKNOWN", {"text": raw_text, "message": msg})
            self.tts.speak(msg)
            return ActionResponse(
                request_id=req_id,
                intent="unknown",
                success=False,
                verified=False,
                message=msg,
            )

        # 3. Validate permissions and parameters
        is_authorized, perm_err, validated_params = self.permission.validate_action(intent, params)

        if not is_authorized:
            logger.info(f"Action '{intent}' not authorized: {perm_err}")
            self.event_manager.emit("ACTION_UNAUTHORIZED", {"intent": intent, "message": perm_err})
            self.tts.speak(perm_err or "Action not authorized.")
            return ActionResponse(
                request_id=req_id,
                intent=intent,
                success=False,
                verified=False,
                message=perm_err or "Action not authorized.",
            )

        # 4. Dispatch action
        try:
            self.state_manager.set_state(AssistantState.EXECUTING)
            self.event_manager.emit("ACTION_DISPATCHED", {"intent": intent, "parameters": validated_params})

            action_request = ActionRequest(
                request_id=req_id,
                intent=intent,
                parameters=validated_params,
                source="voice",
            )

            response = self.dispatcher.dispatch(action_request)

            # 5. Provide feedback and update context
            if response.success:
                self.context.update_context(intent, validated_params)

            self.event_manager.emit("ACTION_COMPLETED", response.model_dump())
            # Ensure we always speak something back to the user
            spoken_msg = (response.message or "").strip() or "Task completed."
            self.tts.speak(spoken_msg)
            return response
        finally:
            self.state_manager.set_state(AssistantState.IDLE)


assistant = Assistant()

