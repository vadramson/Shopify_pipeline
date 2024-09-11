import boto3
import pandas as pd
from botocore import UNSIGNED
from botocore.client import Config
from io import StringIO
from datetime import datetime
import logging

from .config import BUCKET_NAME, DATE_RANGE_START, DATE_RANGE_END, PREFIX_STR, CHUNKSIZE, TARGET_TABLE, TEMP_TABLE
from .database_operations import upsert_target_table

# Set up logger for logging information and errors
logger = logging.getLogger(__name__)

# Create an S3 client that doesn't require credentials
s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))

def extract_date_from_filename(filename: str) -> str:
    """
    Extracts the date from the given filename.

    Assumes the filename is in the format 'YYYY-mm-dd.csv'. 
    Extracts the date part and converts it to a datetime.date object.

    Args:
        filename (str): The filename from which to extract the date.

    Returns:
        datetime.date: The extracted date if successful, else None.
    """
    try:
        # Extract the date part from the filename (assumes format 'YYYY-mm-dd.csv')
        date_str = filename.split('.')[0]  # Extract the part before ".csv"
        return datetime.strptime(date_str, '%Y-%m-%d').date()  # Convert to date object
    except Exception as e:
        # Log critical errors if filename format is unexpected
        logger.critical(f"Error extracting filename: {e}", exc_info=True)
        return None  # Return None if extraction fails

def get_file_list() -> list:
    """
    Retrieves a list of filenames from the S3 bucket that are within the specified date range.

    Lists objects in the specified S3 bucket and filters them based on the date extracted from their filenames.
    Only filenames with dates within the date range defined by DATE_RANGE_START and DATE_RANGE_END are included.

    Returns:
        list: A list of filenames that match the date range criteria.
    """
    # List objects in the specified S3 bucket
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)

    files_to_process = []
    for obj in response.get('Contents', []):
        filename = obj['Key']
        file_date = extract_date_from_filename(filename)
        
        # Check if the file date is within the specified date range
        if file_date and DATE_RANGE_START <= file_date <= DATE_RANGE_END:
            files_to_process.append(filename)  # Add to list if within date range
    
    # Log the completion of file list retrieval
    logger.info(f"File list gotten")
    return files_to_process

def process_file(file: str) -> None:
    """
    Processes a single file from the S3 bucket.

    Retrieves the file from S3, reads it in chunks, and processes each chunk by:
    - Dropping rows with null values in the 'application_id' column
    - Adding columns for prefix matching, processing time, and a combined ID and export date
    - Upserting the processed data into the database

    Args:
        file (str): The filename of the file to process.
    """
    # Retrieve the file object from S3
    obj = s3.get_object(Bucket=BUCKET_NAME, Key=file)
    
    # Read the file in chunks to handle large files
    for chunk in pd.read_csv(obj['Body'], chunksize=CHUNKSIZE):
        # Drop rows where 'application_id' column values are null
        chunk = chunk.dropna(subset=['application_id'])  

        # Add a new column 'has_specific_prefix' to indicate if 'index_prefix' starts with the specified prefix
        chunk['has_specific_prefix'] = chunk['index_prefix'].str.startswith(PREFIX_STR)
        # Add additional columns 'processed_at' and 'id_export_date' for metadata
        chunk['processed_at'] = datetime.now()
        chunk['id_export_date'] = chunk['id'] + '__'+ chunk['export_date']

        # Upsert the chunk into the database, using TEMP_TABLE as staging and TARGET_TABLE for final storage
        success = upsert_target_table(chunk, TEMP_TABLE, TARGET_TABLE)
        
        if success:
            # Log success if upsert was successful
            logger.info(f"Successfully upserted chunk from {file}")
        else:
            # Log critical error if upsert failed
            logger.critical(f"Failed to upsert chunk from {file}", exc_info=True)
    
    # Log completion of file processing
    #logger.info('Finish process file method')
