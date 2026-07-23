from datetime import datetime, timezone
from pathlib import Path

from .version import repository_metadata


def migration_directory():
    return Path(__file__).resolve().parents[2] / "schema" / "migrations"


def _utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def apply_migrations(connection, repository_root, repository_version=None):
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute(
        "CREATE TABLE IF NOT EXISTS schema_migrations (version TEXT PRIMARY KEY, applied_at TEXT NOT NULL)"
    )
    migration_files = sorted(migration_directory().glob("*.sql"))
    applied = {row[0] for row in connection.execute("SELECT version FROM schema_migrations")}
    for migration_file in migration_files:
        version = migration_file.stem.split("_", 1)[0]
        if version in applied:
            continue
        connection.executescript(migration_file.read_text(encoding="utf-8"))
        connection.execute(
            "INSERT INTO schema_migrations(version, applied_at) VALUES (?, ?)",
            (version, _utc_now()),
        )
    metadata = repository_metadata(repository_root, repository_version=repository_version)
    for key, value in metadata.items():
        connection.execute(
            "INSERT OR IGNORE INTO runtime_metadata(metadata_key, metadata_value, created_at) VALUES (?, ?, ?)",
            (key, value, metadata["created"]),
        )
    connection.execute(
        "UPDATE runtime_metadata SET metadata_value = ? WHERE metadata_key = 'schema_version'",
        (metadata["schema_version"],),
    )
    connection.commit()
    return metadata
