#!/usr/bin/env python3
"""
Audit Logging Module
Logs all AI Employee actions for compliance and debugging

Usage:
    from src.utils.logging import log_action
    log_action("email_send", "user@example.com", {"subject": "Invoice"}, "success")
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()


def setup_logging(name: str, level: str = "INFO") -> logging.Logger:
    """Setup logger with console and file handlers"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level))

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    return logger


def log_action(
    action_type: str,
    target: str,
    parameters: Dict[str, Any],
    result: str,
    error_code: Optional[str] = None,
    error_message: Optional[str] = None,
    duration_ms: int = 0,
    approval_status: str = "auto",
    approved_by: Optional[str] = None,
    vault_path: Optional[str] = None
) -> Path:
    """
    Log an action to audit trail

    Args:
        action_type: Type of action (email_send, payment, social_post, etc.)
        target: Target of action (email, account, etc.)
        parameters: Action parameters (don't include secrets)
        result: success or failure
        error_code: Error code if failed
        error_message: Error message if failed
        duration_ms: How long it took
        approval_status: auto, human_approved, human_rejected
        approved_by: Who approved (if human approval)
        vault_path: Path to vault for logs

    Returns:
        Path to log file
    """

    vault = Path(vault_path or os.getenv("VAULT_PATH", "./vault"))
    logs_dir = vault / "Logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    log_file = logs_dir / f"{datetime.now().strftime('%Y-%m-%d')}.json"

    # Create log entry
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action_type": action_type,
        "action_id": f"{action_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "actor": "claude-code",
        "target": target,
        "parameters": parameters,
        "approval_status": approval_status,
        "approved_by": approved_by,
        "result": result,
        "error_code": error_code,
        "error_message": error_message,
        "duration_ms": duration_ms,
    }

    # Read existing logs
    logs = []
    if log_file.exists():
        try:
            with open(log_file, 'r') as f:
                logs = json.load(f)
        except:
            logs = []

    # Append new entry
    logs.append(log_entry)

    # Write back
    with open(log_file, 'w') as f:
        json.dump(logs, f, indent=2)

    return log_file


def query_logs(
    action_type: Optional[str] = None,
    result: Optional[str] = None,
    start_date: Optional[str] = None,
    vault_path: Optional[str] = None
) -> list:
    """
    Query audit logs

    Args:
        action_type: Filter by action type
        result: Filter by result (success/failure)
        start_date: Filter by date (YYYY-MM-DD)
        vault_path: Path to vault

    Returns:
        List of matching log entries
    """

    vault = Path(vault_path or os.getenv("VAULT_PATH", "./vault"))
    logs_dir = vault / "Logs"

    if not logs_dir.exists():
        return []

    results = []

    for log_file in sorted(logs_dir.glob("*.json"), reverse=True):
        if start_date and log_file.stem < start_date:
            break

        try:
            with open(log_file, 'r') as f:
                entries = json.load(f)
                for entry in entries:
                    if action_type and entry.get("action_type") != action_type:
                        continue
                    if result and entry.get("result") != result:
                        continue
                    results.append(entry)
        except:
            continue

    return results


if __name__ == "__main__":
    # Test logging
    log_action(
        action_type="test_action",
        target="test@example.com",
        parameters={"test": "data"},
        result="success",
        approval_status="auto"
    )
    print("✅ Log action working!")
