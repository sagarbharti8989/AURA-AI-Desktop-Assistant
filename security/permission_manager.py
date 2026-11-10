"""
Permission Manager for AURA.
Validates requests against ACTION_REGISTRY and user permission toggles.
"""

from typing import Tuple, Optional, Dict, Any
from security.action_registry import ACTION_REGISTRY
from security.security_policy import SecurityPolicy
from security.request_validator import validate_intent_parameters
from database.repositories import PermissionRepository
from utils.constants import (
    SECURITY_REJECT_UNAUTHORIZED_MESSAGE,
    SECURITY_REJECT_UNKNOWN_MESSAGE,
)
from utils.logger import logger
from utils.exceptions import PermissionDeniedError, InvalidCommandError


class PermissionManager:
    """Evaluates and authorizes requested actions before dispatch."""

    def __init__(self, permission_repo: Optional[PermissionRepository] = None) -> None:
        self.permission_repo = permission_repo or PermissionRepository()

    def validate_action(
        self, intent: str, parameters: Dict[str, Any]
    ) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Validates an action against:
        1. Security policy prohibitions (power, files).
        2. Action registry inclusion.
        3. Parameter constraints.
        4. User permission database toggles.

        Returns (is_authorized, error_message, validated_parameters).
        """
        # 1. Security Policy check
        is_allowed, policy_msg = SecurityPolicy.evaluate_intent(intent)
        if not is_allowed:
            return False, policy_msg, {}

        # 2. Registry check
        if intent not in ACTION_REGISTRY:
            logger.warning(f"Permission Manager: Unknown intent '{intent}' rejected.")
            return False, SECURITY_REJECT_UNKNOWN_MESSAGE, {}

        action_def = ACTION_REGISTRY[intent]
        permission_key = action_def["permission"]

        # 3. User Permission check
        if not self.permission_repo.is_enabled(permission_key):
            logger.info(
                f"Permission Manager: Action '{intent}' blocked due to disabled permission '{permission_key}'."
            )
            return False, SECURITY_REJECT_UNAUTHORIZED_MESSAGE, {}

        # 4. Parameter validation
        try:
            validated_params = validate_intent_parameters(intent, parameters)
        except InvalidCommandError as e:
            logger.warning(f"Permission Manager: Parameter validation failed: {e}")
            return False, str(e), {}

        return True, None, validated_params

    def is_permission_enabled(self, permission_name: str) -> bool:
        """Direct check if a capability is enabled."""
        return self.permission_repo.is_enabled(permission_name)

    def set_permission(self, permission_name: str, enabled: bool) -> None:
        """Toggles a capability permission."""
        self.permission_repo.set_enabled(permission_name, enabled)
        logger.info(f"Permission '{permission_name}' set to {enabled}")


permission_manager = PermissionManager()

