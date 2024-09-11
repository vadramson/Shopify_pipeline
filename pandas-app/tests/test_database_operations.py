import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError
from src.database_operations import upsert_target_table
import pandas as pd

# Sample dataframe for testing
df = pd.DataFrame({
    'id': ['811451e6-c164-430c-b083-70842fc09005', '93d70c55-4403-4a22-bfa0-8b455c47ba24'],
    'shop_name': ['Shop1', 'Shop2'],  
    'config': ['config1', 'config2']  
})

CHUNKSIZE = 16000

@patch('src.database_operations.engine')
@patch('pandas.DataFrame.to_sql')
def test_upsert_target_table_success(mock_to_sql, mock_engine):
    """
    Test the upsert functionality for successful database operations.
    """
    mock_conn = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_conn

    # Mock to_sql to simulate successful table creation
    mock_to_sql.return_value = None

    # Call the function
    success = upsert_target_table(df, 'raw.shopify_configs_temp', 'staging.shopify_configs')

    # Assertions
    assert success is True
    mock_conn.execute.assert_called()
    mock_to_sql.assert_called_with(
        'shopify_configs_temp',
        mock_engine,  # Corrected to use the mocked engine object
        schema='raw',
        if_exists='replace',
        index=False,
        chunksize=CHUNKSIZE
    )


@patch('src.database_operations.engine')
@patch('pandas.DataFrame.to_sql')
def test_upsert_target_table_failure(mock_to_sql, mock_engine):
    """
    Test the upsert functionality for failure in database operations.
    """
    mock_conn = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_conn

    # Simulate a failure in the database operation
    mock_conn.execute.side_effect = SQLAlchemyError("Database error")

    # Call the function and expect it to fail
    success = upsert_target_table(df, 'raw.shopify_configs_temp', 'staging.shopify_configs')

    # Assertions
    assert success is False
    mock_conn.execute.assert_called()
    mock_to_sql.assert_called_once()  
