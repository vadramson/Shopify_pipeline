import pytest
from src.config import setup_logging, logger, DB_CONNECTION_STRING
from dotenv import load_dotenv
import os

# Load environment variables from a .env file
load_dotenv()

def test_setup_logging(caplog):
    """
    Test that the logging setup does not produce any unexpected log messages.
    """
    setup_logging()
    assert len(caplog.records) == 0  # Ensure no log messages are produced at setup

def test_db_connection_string():
    """
    Test that the database connection string is correctly set in the config.
    """
    assert DB_CONNECTION_STRING == os.getenv('DB_CONNECTION_STRING')
