from pathlib import Path
import sqlite3


def backup_database(config, destination):
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not config.database_path.exists():
        raise FileNotFoundError(f"Database does not exist: {config.database_path}")
    source = sqlite3.connect(config.database_path)
    target = sqlite3.connect(destination)
    try:
        source.backup(target)
    finally:
        target.close()
        source.close()
    return destination


def restore_database(config, source, overwrite=False):
    source = Path(source)
    if not source.exists():
        raise FileNotFoundError(f"Backup does not exist: {source}")
    if config.database_path.exists() and not overwrite:
        raise FileExistsError("Destination database exists; pass overwrite explicitly.")
    config.database_path.parent.mkdir(parents=True, exist_ok=True)
    source_connection = sqlite3.connect(source)
    target_connection = sqlite3.connect(config.database_path)
    try:
        source_connection.backup(target_connection)
    finally:
        target_connection.close()
        source_connection.close()
    return config.database_path
