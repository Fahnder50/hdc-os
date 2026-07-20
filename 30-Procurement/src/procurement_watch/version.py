from datetime import datetime, timezone
import os
from pathlib import Path
import subprocess


SCHEMA_VERSION = "002"


def _git_value(repository_root, *arguments):
    try:
        result = subprocess.run(
            ["git", *arguments],
            cwd=repository_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip() or None


def repository_metadata(repository_root, environ=None, created_at=None, repository_version=None):
    values = os.environ if environ is None else environ
    root = Path(repository_root)
    commit = _git_value(root, "rev-parse", "HEAD") or "unknown"
    version = repository_version or values.get("HDC_REPOSITORY_VERSION") or _git_value(root, "describe", "--tags", "--abbrev=0") or "unreleased"
    timestamp = created_at or datetime.now(timezone.utc).isoformat(timespec="seconds")
    return {
        "repository_commit": commit,
        "repository_version": version,
        "schema_version": SCHEMA_VERSION,
        "created": timestamp,
    }
