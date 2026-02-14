"""
Cloud Worker - FastAPI app for Platinum Tier
Runs on Render.com - 24/7 email triage + social drafts

Architecture:
- /health endpoint (keeps Render alive via UptimeRobot ping every 5 min)
- Background Gmail watcher (detects new emails)
- Background Ralph Loop (draft-only mode - creates items, never sends)
- Background git sync (pulls approvals from local, pushes drafts back)

Local laptop handles:
- WhatsApp messages
- Approval decisions
- Final sends/posts
"""

import os
import sys
import logging
import threading
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('CloudWorker')

# ============================================================================
# INITIALIZATION
# ============================================================================

app = FastAPI(title="AI Employee Cloud Worker", version="0.1.0")

# Global state
WORKERS_STATE = {
    'started': datetime.now().isoformat(),
    'gmail_watcher_running': False,
    'ralph_loop_running': False,
    'git_sync_running': False,
    'last_email_check': None,
    'last_ralph_iteration': None,
    'last_git_sync': None,
    'error_log': []
}

# Configuration from environment
VAULT_PATH = os.getenv('VAULT_PATH', './vault')
AGENT_MODE = os.getenv('AGENT_MODE', 'cloud')
DRY_RUN = os.getenv('DRY_RUN', 'true').lower() == 'true'
RALPH_CHECK_INTERVAL = int(os.getenv('RALPH_CHECK_INTERVAL', '300'))  # 5 min
GIT_SYNC_INTERVAL = int(os.getenv('GIT_SYNC_INTERVAL', '300'))  # 5 min
GMAIL_CHECK_INTERVAL = int(os.getenv('GMAIL_CHECK_INTERVAL', '120'))  # 2 min

logger.info(f"Cloud Worker Config: vault={VAULT_PATH}, agent_mode={AGENT_MODE}, dry_run={DRY_RUN}")

# ============================================================================
# ENDPOINTS
# ============================================================================


@app.get("/health")
@app.head("/health")
def health():
    """
    Health check endpoint - called by UptimeRobot every 5 minutes to keep Render alive
    Supports both GET and HEAD requests
    """
    return JSONResponse({
        "status": "alive",
        "mode": AGENT_MODE,
        "vault": VAULT_PATH,
        "workers": {
            "gmail_watcher": WORKERS_STATE['gmail_watcher_running'],
            "ralph_loop": WORKERS_STATE['ralph_loop_running'],
            "git_sync": WORKERS_STATE['git_sync_running'],
        },
        "timestamp": datetime.now().isoformat(),
        "started": WORKERS_STATE['started'],
        "last_email_check": WORKERS_STATE['last_email_check'],
        "last_ralph_iteration": WORKERS_STATE['last_ralph_iteration'],
        "last_git_sync": WORKERS_STATE['last_git_sync'],
        "recent_errors": WORKERS_STATE['error_log'][-5:] if WORKERS_STATE['error_log'] else []
    })


@app.get("/status")
def status():
    """
    Detailed status endpoint
    """
    return health()


@app.get("/vault-status")
def vault_status():
    """
    Check vault folder status (items in each folder)
    """
    vault = Path(VAULT_PATH)
    folders = {
        'needs_action': len(list((vault / 'Needs_Action').glob('*.md'))) if (vault / 'Needs_Action').exists() else 0,
        'pending_approval': len(list((vault / 'Pending_Approval').glob('*.md'))) if (vault / 'Pending_Approval').exists() else 0,
        'approved': len(list((vault / 'Approved').glob('*.md'))) if (vault / 'Approved').exists() else 0,
        'in_progress_cloud': len(list((vault / 'In_Progress' / 'cloud-agent').glob('*.md'))) if (vault / 'In_Progress' / 'cloud-agent').exists() else 0,
        'in_progress_local': len(list((vault / 'In_Progress' / 'local-agent').glob('*.md'))) if (vault / 'In_Progress' / 'local-agent').exists() else 0,
        'done': len(list((vault / 'Done').glob('*.md'))) if (vault / 'Done').exists() else 0,
    }
    return JSONResponse({"vault_folders": folders})


# ============================================================================
# BACKGROUND WORKERS
# ============================================================================


def run_gmail_watcher():
    """Background thread: Gmail watcher (draft-only, no replies)"""
    try:
        from watchers.gmail_watcher import GmailWatcher

        logger.info("Starting Gmail Watcher")
        watcher = GmailWatcher(VAULT_PATH)
        WORKERS_STATE['gmail_watcher_running'] = True

        while True:
            try:
                emails = watcher.check_for_updates()
                if emails:
                    logger.info(f"Gmail Watcher found {len(emails)} new emails")
                    for email in emails:
                        try:
                            watcher.create_action_file(email)
                            logger.info(f"Created action file for email")
                        except Exception as e:
                            logger.error(f"Failed to create action file: {e}")
                            WORKERS_STATE['error_log'].append(f"Gmail action file error: {e}")

                WORKERS_STATE['last_email_check'] = datetime.now().isoformat()
                time.sleep(GMAIL_CHECK_INTERVAL)

            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Gmail Watcher error: {e}")
                WORKERS_STATE['error_log'].append(f"Gmail Watcher error: {e}")
                time.sleep(GMAIL_CHECK_INTERVAL)

        WORKERS_STATE['gmail_watcher_running'] = False

    except ImportError:
        logger.error("Gmail API not available")
        WORKERS_STATE['error_log'].append("Gmail API import failed")
    except Exception as e:
        logger.error(f"Gmail Watcher initialization failed: {e}")
        WORKERS_STATE['error_log'].append(f"Gmail Watcher init failed: {e}")
        WORKERS_STATE['gmail_watcher_running'] = False


def run_ralph_loop():
    """Background thread: Ralph Loop (cloud mode = draft-only, never executes)"""
    try:
        from scripts.ralph_loop import RalphLoop

        logger.info(f"Starting Ralph Loop (mode=cloud, dry_run=true)")
        WORKERS_STATE['ralph_loop_running'] = True

        while True:
            try:
                # Always run in dry_run mode in cloud - actions are drafts only
                loop = RalphLoop(
                    vault_path=VAULT_PATH,
                    max_iterations=3,  # 3 quick iterations per cycle
                    dry_run=True,  # ALWAYS draft-only in cloud
                    agent_mode='cloud'
                )
                result = loop.run()

                logger.info(f"Ralph iteration complete: {result['auto_executed']} auto, {result['sent_to_approval']} to approval")
                WORKERS_STATE['last_ralph_iteration'] = datetime.now().isoformat()

                # Sleep before next iteration
                time.sleep(RALPH_CHECK_INTERVAL)

            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Ralph Loop error: {e}")
                WORKERS_STATE['error_log'].append(f"Ralph Loop error: {e}")
                time.sleep(RALPH_CHECK_INTERVAL)

        WORKERS_STATE['ralph_loop_running'] = False

    except ImportError as e:
        logger.error(f"Ralph Loop import failed: {e}")
        WORKERS_STATE['error_log'].append(f"Ralph Loop import failed: {e}")
    except Exception as e:
        logger.error(f"Ralph Loop initialization failed: {e}")
        WORKERS_STATE['error_log'].append(f"Ralph Loop init failed: {e}")
        WORKERS_STATE['ralph_loop_running'] = False


def run_git_sync():
    """Background thread: Git sync (pull local changes, push cloud drafts)"""
    try:
        from cloud.git_sync import GitSync

        logger.info("Starting Git Sync")
        WORKERS_STATE['git_sync_running'] = True

        syncer = GitSync(VAULT_PATH, agent_name='cloud-agent', dry_run=DRY_RUN)

        while True:
            try:
                result = syncer.sync_cycle()
                logger.info(f"Git sync complete: pulled={result['pulled']}, pushed={result['pushed']}")
                WORKERS_STATE['last_git_sync'] = datetime.now().isoformat()

                if result['errors']:
                    WORKERS_STATE['error_log'].extend(result['errors'])

                time.sleep(GIT_SYNC_INTERVAL)

            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Git Sync error: {e}")
                WORKERS_STATE['error_log'].append(f"Git Sync error: {e}")
                time.sleep(GIT_SYNC_INTERVAL)

        WORKERS_STATE['git_sync_running'] = False

    except ImportError:
        logger.warning("GitPython not available - git sync disabled")
    except Exception as e:
        logger.error(f"Git Sync initialization failed: {e}")
        WORKERS_STATE['error_log'].append(f"Git Sync init failed: {e}")
        WORKERS_STATE['git_sync_running'] = False


# ============================================================================
# STARTUP / SHUTDOWN
# ============================================================================


@app.on_event("startup")
def startup_event():
    """Start background worker threads on app startup"""
    logger.info("=" * 70)
    logger.info("CLOUD WORKER STARTING")
    logger.info("=" * 70)
    logger.info(f"Vault: {VAULT_PATH}")
    logger.info(f"Agent Mode: {AGENT_MODE}")
    logger.info(f"Dry Run: {DRY_RUN}")
    logger.info(f"Gmail check interval: {GMAIL_CHECK_INTERVAL}s")
    logger.info(f"Ralph check interval: {RALPH_CHECK_INTERVAL}s")
    logger.info(f"Git sync interval: {GIT_SYNC_INTERVAL}s")
    logger.info("=" * 70)

    # Verify vault exists
    vault = Path(VAULT_PATH)
    if not vault.exists():
        logger.error(f"VAULT NOT FOUND: {VAULT_PATH}")
        WORKERS_STATE['error_log'].append(f"Vault not found: {VAULT_PATH}")
        return

    # Start worker threads (daemon mode = they stop when main thread stops)
    threads = [
        ("GmailWatcher", run_gmail_watcher),
        ("RalphLoop", run_ralph_loop),
        ("GitSync", run_git_sync),
    ]

    for name, func in threads:
        t = threading.Thread(target=func, daemon=True, name=name)
        t.start()
        logger.info(f"Started {name} thread")

    logger.info("All worker threads started")


@app.on_event("shutdown")
def shutdown_event():
    """Log shutdown"""
    logger.info("Cloud Worker shutting down")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv('PORT', 8000))
    host = os.getenv('HOST', '0.0.0.0')

    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
