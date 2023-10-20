# type: ignore
import os
from pathlib import Path
from typing import Any

import dotenv
import psycopg2
from modules.config import CONFIG_DIR

# Import database environment variables
dotenv.load_dotenv(Path(CONFIG_DIR / "database.env"))

# PostgreSQL connection parameters
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")


def connect() -> Any:
    """Create a connection to a PostgresSQL database.

    Returns:
        Any: Database connection object used to perform
    """
    # #"""Connect to the PostgreSQL database and return the connection."""
    return psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
    )
