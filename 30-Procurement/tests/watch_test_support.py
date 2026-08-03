import sqlite3


def activate_case_for_engine_test(config, case_id="PC-0001"):
    """Activate an isolated test case without reopening the repository case."""
    connection = sqlite3.connect(config.database_path)
    connection.execute("UPDATE procurement_cases SET status = 'WATCHING' WHERE case_id = ?", (case_id,))
    connection.commit()
    connection.close()
