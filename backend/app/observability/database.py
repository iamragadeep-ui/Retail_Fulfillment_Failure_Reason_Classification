import sqlite3
from pathlib import Path
from typing import Generator


# Project root:
# Retail_Fulfillment_Failure_Reason_Classification/
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Separate database required for observability data.
OBSERVABILITY_DB_PATH = PROJECT_ROOT / "observability.db"


def get_connection() -> sqlite3.Connection:
    """
    Create and configure a SQLite connection for observability data.
    """

    connection = sqlite3.connect(
        OBSERVABILITY_DB_PATH,
        timeout=5.0,
    )

    # Return rows that can be accessed using column names.
    connection.row_factory = sqlite3.Row

    # SQLite production-style settings required by the project.
    connection.execute("PRAGMA foreign_keys = ON;")
    connection.execute("PRAGMA busy_timeout = 5000;")
    connection.execute("PRAGMA journal_mode = WAL;")

    return connection


def get_db() -> Generator[sqlite3.Connection, None, None]:
    """
    FastAPI dependency that provides an observability database
    connection and always closes it after the request.
    """

    connection = get_connection()

    try:
        yield connection
    finally:
        connection.close()


def check_database_connection() -> bool:
    """
    Verify that the observability SQLite database is accessible.
    """

    connection = None

    try:
        connection = get_connection()
        connection.execute("SELECT 1;")
        return True
    except sqlite3.Error:
        return False
    finally:
        if connection is not None:
            connection.close()