# type: ignore
from typing import Any

import psycopg2

# PostgreSQL connection parameters
DB_NAME = "railway"
DB_USER = "postgres"
DB_PASS = "bfIwUUa1L3RCjGZSw3oX"
DB_HOST = "containers-us-west-179.railway.app"
DB_PORT = "6563"


def connect() -> Any:
    """Create a connection to a PostgresSQL database.

    Returns:
        Any: Database connection object used to perform
    """
    # #"""Connect to the PostgreSQL database and return the connection."""
    return psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
    )
