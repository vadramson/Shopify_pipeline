import logging
from src.config import setup_logging, logger
from src.data_processing import get_file_list, process_file

def main():
    """
    Main entry point for the script.

    Sets up logging, retrieves the list of files to process, and processes each file.
    Handles exceptions at both the file processing and main execution levels.
    """
    # Set up logging configuration
    setup_logging()

    try:
        # Retrieve list of files from the source
        files = get_file_list()

        if not files:
            logger.warning("No files found to process.")
            return

        # Process each file retrieved
        for file in files:
            try:
                logger.info(f"Processing file: {file}")
                
                # Process the current file
                process_file(file)
                
                logger.info(f"Successfully processed file: {file}\n\n")
            except Exception as e:
                logger.error(f"Error processing file {file}: {e}", exc_info=True)

    except Exception as e:
        logger.critical(f"Unexpected error: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
