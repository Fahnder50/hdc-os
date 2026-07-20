import sqlite3

from .config import AppConfig
from .migrations import apply_migrations


def connect(config: AppConfig):
    connection = sqlite3.connect(config.database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize(config: AppConfig):
    config.database_path.parent.mkdir(parents=True, exist_ok=True)
    config.logs_path.mkdir(parents=True, exist_ok=True)
    config.reports_path.mkdir(parents=True, exist_ok=True)
    connection = connect(config)
    try:
        metadata = apply_migrations(connection, config.repository_root, config.repository_version)
    finally:
        connection.close()
    return metadata


def schema_status(config: AppConfig):
    if not config.database_path.exists():
        return {"reachable": False, "path": str(config.database_path), "schema_version": None, "tables": []}
    connection = connect(config)
    try:
        versions = [row[0] for row in connection.execute("SELECT version FROM schema_migrations ORDER BY version")]
        tables = [row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    finally:
        connection.close()
    return {
        "reachable": True,
        "path": str(config.database_path),
        "schema_version": versions[-1] if versions else None,
        "tables": tables,
    }
