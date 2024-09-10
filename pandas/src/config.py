"""
Configuration settings for the application.

This module includes configuration for logging, database connections,
and other application settings.
"""

from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import psycopg2
import logging
from dotenv import load_dotenv
import os

# Load environment variables from a .env file
load_dotenv()

def setup_logging():
    """
    Sets up basic logging configuration.

    Configures the logging system to output messages with level INFO or higher
    and specifies the log message format.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

# Initialize logger
logger = logging.getLogger(__name__)

# Database connection string from environment variable
DB_CONNECTION_STRING = os.getenv('DB_CONNECTION_STRING')


# PostgreSQL connection using SQLAlchemy
engine = create_engine(DB_CONNECTION_STRING)
Session = sessionmaker(bind=engine)

# Check if the database connection works by trying to connect
try:
    with engine.connect() as connection:
        # Test connection is successful
        Session = sessionmaker(bind=engine)
        # Connection is successful; no further action needed here
        # Uncomment the next line if you want to log successful connections
        # logger.info("Database connection successful.")
except SQLAlchemyError as e:
    # Log database connection failure
    logger.critical(f"Database connection failed: {e}", exc_info=True)

# S3 bucket details
BUCKET_NAME = 'alg-data-public'

# Date range for processing files
DATE_RANGE_START = datetime(2019, 4, 1).date()
DATE_RANGE_END = datetime(2019, 4, 7).date()

# Target and Temp tables
TARGET_TABLE = 'staging.shopify_configs'
TEMP_TABLE = 'raw.shopify_configs_temp'

# Prefix string for matching
PREFIX_STR = 'shopify_'

# Chunk size for processing data
CHUNKSIZE = 16000
