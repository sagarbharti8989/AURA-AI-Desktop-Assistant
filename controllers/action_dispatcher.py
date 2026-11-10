"""
Action Dispatcher for AURA.
Routes authorized requests to dedicated controller functions.
Ensures zero arbitrary string evaluation or dynamic execution.
"""

from typing import Dict, Any, Callable
from security.request_validator import ActionRequest, ActionResponse
from verification.result_verifier import result_verifier
from database.repositories import ExecutionLogRepository
from database.models import ExecutionLogRecord
from utils.helpers import current_iso_timestamp
from utils.logger import logger
from utils.exceptions import ActionExecutionError

from controllers.volume_controller import volume_controller
from controllers.brightness_controller import brightness_controller
from controllers.application_controller import application_controller
from controllers.wifi_controller import wifi_controller
from controllers.bluetooth_controller import bluetooth_controller
from controllers.system_controller import system_controller


class ActionDispatcher:
    """Dispatches authorized action requests to predefined controller methods."""

    def __init__(self, log_repo: ExecutionLogRepository = None, verifier=result_verifier) -> None:
        self.log_repo = log_repo or ExecutionLogRepository()
        self.verifier = verifier
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Explicitly binds intents to controller methods."""
        self.handlers: Dict[str, Callable[[Dict[str, Any]], Any]] = {
            # Volume
            "set_volume": lambda p: volume_controller.set_volume(p.get("level", 50)),
            "increase_volume": lambda p: volume_controller.increase_volume(p.get("amount", 10)),
            "decrease_volume": lambda p: volume_controller.decrease_volume(p.get("amount", 10)),
            "mute_audio": lambda _: volume_controller.mute(),
            "unmute_audio": lambda _: volume_controller.unmute(),
            # Brightness
            "set_brightness": lambda p: brightness_controller.set_brightness(p.get("level", 50)),
            "increase_brightness": lambda p: brightness_controller.increase_brightness(p.get("amount", 10)),
            "decrease_brightness": lambda p: brightness_controller.decrease_brightness(p.get("amount", 10)),
            # Applications
            "open_app": lambda p: application_controller.open_app(p.get("app_name", "")),
            "close_app": lambda p: application_controller.close_app(p.get("app_name", "")),
            # Wi-Fi
            "get_wifi_status": lambda _: wifi_controller.get_status(),
            "enable_wifi": lambda _: wifi_controller.enable(),
            "disable_wifi": lambda _: wifi_controller.disable(),
            # Bluetooth
            "get_bluetooth_status": lambda _: bluetooth_controller.get_status(),
            "enable_bluetooth": lambda _: bluetooth_controller.enable(),
            "disable_bluetooth": lambda _: bluetooth_controller.disable(),
            # Safe System
            "lock_system": lambda _: system_controller.lock_system(),
            "check_battery": lambda _: system_controller.check_battery(),
            "take_screenshot": lambda _: system_controller.take_screenshot(),
        }

    def dispatch(self, request: ActionRequest) -> ActionResponse:
        """
        Executes an authorized ActionRequest.
        Validates post-execution state and logs the outcome.
        """
        intent = request.intent
        req_id = request.request_id

        if intent not in self.handlers:
            msg = f"No handler registered for intent: {intent}"
            logger.error(msg)
            return self._record_and_return(
                ActionResponse(
                    request_id=req_id,
                    intent=intent,
                    success=False,
                    verified=False,
                    message=msg,
                )
            )

        handler = self.handlers[intent]

        try:
            success, requested_val, actual_val, raw_msg = handler(request.parameters)
            verified_response = self.verifier.verify(
                request_id=req_id,
                intent=intent,
                success=success,
                requested_value=requested_val,
                actual_value=actual_val,
                raw_message=raw_msg,
            )
            return self._record_and_return(verified_response)
        except ActionExecutionError as e:
            logger.error(f"Execution error on {intent}: {e}")
            err_response = ActionResponse(
                request_id=req_id,
                intent=intent,
                success=False,
                verified=False,
                message=str(e),
            )
            return self._record_and_return(err_response)
        except Exception as e:
            logger.error(f"Unexpected error executing {intent}: {e}", exc_info=True)
            err_response = ActionResponse(
                request_id=req_id,
                intent=intent,
                success=False,
                verified=False,
                message=f"System operation failed: {e}",
            )
            return self._record_and_return(err_response)

    def _record_and_return(self, response: ActionResponse) -> ActionResponse:
        """Persists the execution result to SQLite."""
        record = ExecutionLogRecord(
            request_id=response.request_id,
            timestamp=current_iso_timestamp(),
            intent=response.intent,
            outcome="SUCCESS" if response.success else "FAILED",
            verified=response.verified,
            message=response.message,
        )
        self.log_repo.log(record)
        return response


action_dispatcher = ActionDispatcher()

