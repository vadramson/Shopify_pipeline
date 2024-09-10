import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import logging

from .config import engine, CHUNKSIZE

# Set up logger for logging information and errors
logger = logging.getLogger(__name__)

def upsert_target_table(df: pd.DataFrame, temp_table: str, target_table: str, merge_key: str = 'id_export_date') -> bool:
    """
    Performs an upsert operation on the target table using data from a temporary table.

    The function will:
    1. Load the DataFrame into a temporary table.
    2. Perform an upsert operation to merge data into the target table.
    3. Drop the temporary table after the operation.

    If the target table does not exist, it creates the target table, inserts the data, and adds a unique constraint.
    
    Args:
        df (pd.DataFrame): The DataFrame to be upserted.
        temp_table (str): The name of the temporary table including schema (e.g., 'schema.temp_table').
        target_table (str): The name of the target table including schema (e.g., 'schema.target_table').
        merge_key (str): The column used for the conflict resolution during upsert (default is 'id_export_date').

    Returns:
        bool: True if the upsert operation was successful, False otherwise.
    """
    # Split schema and table name for temp and target tables
    temp_schema, temp_table_name = temp_table.split('.', 1)
    target_schema, target_table_name = target_table.split('.', 1)

    try:
        # Connect to the database and start a transaction
        with engine.connect() as conn:
            transaction = conn.begin()
            try:
                # Load DataFrame into the temporary table
                df.to_sql(temp_table_name, engine, schema=temp_schema, if_exists='replace', index=False, chunksize=CHUNKSIZE)

                # Construct the INSERT ... ON CONFLICT query for upsert
                column_names = df.columns.tolist()
                column_mappings = ", ".join([f"\"{col}\" = EXCLUDED.\"{col}\"" for col in column_names])
                insert_columns = ", ".join([f"\"{col}\"" for col in column_names])
                insert_values = ", ".join([f"\"{col}\"" for col in column_names])

                insert_query = f"""
                    INSERT INTO {target_schema}.{target_table_name} ({insert_columns})
                    SELECT {insert_values}
                    FROM {temp_schema}.{temp_table_name}
                    ON CONFLICT ({merge_key})
                    DO UPDATE SET {column_mappings};
                """

                # Query to drop the temporary table
                del_query = f"""DROP TABLE IF EXISTS {temp_schema}.{temp_table_name}"""

                # Execute the upsert operation and drop the temporary table
                conn.execute(text(insert_query))
                conn.execute(text(del_query))
                #logger.info("Upsert completed.")
                
                # Commit the transaction if no errors
                transaction.commit()
                #logger.info('Transaction committed')
                return True

            except SQLAlchemyError as e:
                # Rollback the transaction if an error occurs
                transaction.rollback()
                logger.info('Transaction rolled back due to an error')

                # Check if the error indicates that the target table does not exist
                if 'relation "staging.shopify_configs" does not exist' in str(e):
                    #logger.info(f"Table does not exist: {e}")

                    try:
                        # Start a new transaction for table creation
                        with engine.connect() as conn:
                            transaction = conn.begin()
                            try:
                                # Create the target table and insert the data
                                df.to_sql(target_table_name, engine, schema=target_schema, if_exists='append', index=False, chunksize=CHUNKSIZE)
                                del_query = f"""DROP TABLE IF EXISTS {temp_schema}.{temp_table_name}"""
                                add_constraint_query = f"""ALTER TABLE {target_schema}.{target_table_name} ADD CONSTRAINT unique_id_export_date UNIQUE (id_export_date)"""
                                conn.execute(text(add_constraint_query))
                                conn.execute(text(del_query))

                                logger.info(f"Table {target_table_name} created and data inserted.")
                                transaction.commit()
                                return True
                            except SQLAlchemyError as inner_e:
                                transaction.rollback()  # Rollback if an error occurs during table creation
                                logger.critical(f"Error creating table: {inner_e}", exc_info=True)
                                return False
                    except SQLAlchemyError as inner_e:
                        logger.critical(f"Error handling table creation transaction: {inner_e}", exc_info=True)
                        return False
                else:
                    logger.critical(f"Error occurred during upsert: {e}", exc_info=True)
                    return False

    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}", exc_info=True)
        return False
