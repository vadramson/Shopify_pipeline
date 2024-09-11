from src.data_processing import get_file_list
from unittest.mock import patch
from datetime import datetime
import pytest

@patch('src.data_processing.s3.list_objects_v2')
@patch('src.data_processing.extract_date_from_filename')
def test_get_file_list(mock_extract_date, mock_list_objects):
    """
    Test the retrieval of file list from S3, including a date range with a missing file.
    """
    # Simulating S3 returning files for the given date range (excluding 2019-04-03)
    mock_list_objects.return_value = {
        'Contents': [
            {'Key': '2019-04-01.csv'}, 
            {'Key': '2019-04-02.csv'}, 
            {'Key': '2019-04-04.csv'}, 
            {'Key': '2019-04-05.csv'}, 
            {'Key': '2019-04-06.csv'}, 
            {'Key': '2019-04-07.csv'}
        ]
    }
    
    # Setting the mock behavior for extracting dates from filenames
    mock_extract_date.side_effect = [
        datetime(2019, 4, 1).date(),
        datetime(2019, 4, 2).date(),
        datetime(2019, 4, 4).date(),
        datetime(2019, 4, 5).date(),
        datetime(2019, 4, 6).date(),
        datetime(2019, 4, 7).date(),
    ]
    
    # Calling the actual function
    files = get_file_list()

    # Validating that files between 2019-04-01 and 2019-04-07 (excluding 2019-04-03) are returned
    assert '2019-04-01.csv' in files
    assert '2019-04-02.csv' in files
    assert '2019-04-04.csv' in files
    assert '2019-04-05.csv' in files
    assert '2019-04-06.csv' in files
    assert '2019-04-07.csv' in files
    assert len(files) == 6  # Only 6 files should be present
