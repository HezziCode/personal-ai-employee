#!/usr/bin/env python3
"""
Custom Error Classes
Error taxonomy for AI Employee
"""

import time
from functools import wraps
from typing import Callable, Any


# ==================== ERROR CLASSES ====================

class AIEmployeeError(Exception):
    """Base error for AI Employee"""
    pass


class TransientError(AIEmployeeError):
    """Transient errors (timeout, rate limit, etc.) - retry with backoff"""
    pass


class AuthError(AIEmployeeError):
    """Authentication/authorization error - alert human"""
    pass


class ValidationError(AIEmployeeError):
    """Validation error - manual review needed"""
    pass


class DataError(AIEmployeeError):
    """Data corruption/missing field - quarantine"""
    pass


class SystemError(AIEmployeeError):
    """System error (crash, disk full) - watchdog restart"""
    pass


# ==================== RETRY DECORATOR ====================

def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    on_error: Callable = None
):
    """
    Retry decorator with exponential backoff

    Usage:
        @retry_with_backoff(max_attempts=3)
        def risky_operation():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except TransientError as e:
                    if attempt == max_attempts - 1:
                        raise
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    print(f"⚠️ Attempt {attempt + 1} failed. Retrying in {delay}s...")
                    time.sleep(delay)
                except (AuthError, ValidationError, DataError) as e:
                    # Don't retry these
                    if on_error:
                        on_error(e)
                    raise
        return wrapper
    return decorator


# ==================== ERROR HANDLER ====================

class ErrorHandler:
    """Centralized error handling"""

    @staticmethod
    def handle_error(error: Exception, context: str = "") -> dict:
        """
        Handle error and return action

        Returns:
            {
                "category": "transient|auth|validation|data|system",
                "action": "retry|alert|manual_review|quarantine|restart",
                "message": "Human readable message"
            }
        """

        if isinstance(error, TransientError):
            return {
                "category": "transient",
                "action": "retry",
                "message": f"Transient error: {error}. Will retry with backoff."
            }

        elif isinstance(error, AuthError):
            return {
                "category": "auth",
                "action": "alert",
                "message": f"Authentication failed: {error}. Pausing operations and alerting user."
            }

        elif isinstance(error, ValidationError):
            return {
                "category": "validation",
                "action": "manual_review",
                "message": f"Validation error: {error}. Moving to manual review."
            }

        elif isinstance(error, DataError):
            return {
                "category": "data",
                "action": "quarantine",
                "message": f"Data error: {error}. Quarantining and alerting user."
            }

        elif isinstance(error, SystemError):
            return {
                "category": "system",
                "action": "restart",
                "message": f"System error: {error}. Watchdog will restart."
            }

        else:
            return {
                "category": "unknown",
                "action": "alert",
                "message": f"Unknown error: {error}. Alerting user."
            }


if __name__ == "__main__":
    # Test error handling
    handler = ErrorHandler()

    errors = [
        TransientError("Network timeout"),
        AuthError("Invalid credentials"),
        ValidationError("Missing field"),
        DataError("Corrupted file"),
    ]

    for error in errors:
        result = handler.handle_error(error)
        print(f"✅ {result['category']}: {result['action']}")
