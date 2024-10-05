import pytest
from deploy.file_manager import get_files
from unittest.mock import patch, MagicMock
from main import validate_config
from main import get_workspace_details

def test_get_files(monkeypatch):
    # Input string simulating file paths separated by ";"
    files = "report1.rdl;report2.pbix;not_a_report.txt"
    separator = ";"

    # Expected result focuses on .pbix and .rdl files
    expected = [
        {
            'file_name': 'report1.rdl',
            'file_suffix': 'rdl',
            'file_without_extension': 'report1',
        },
        {
            'file_name': 'report2.pbix',
            'file_suffix': 'pbix',
            'file_without_extension': 'report2',
        }
    ]

    # Call the function under test
    result = get_files(files, separator)

    # Verify the result matches the expected output
    assert len(result) == 2  # Ensure only two files are processed
    for file_info, expected_info in zip(result, expected):
        assert file_info['file_name'] == expected_info['file_name']
        assert file_info['file_suffix'] == expected_info['file_suffix']
        assert file_info['file_without_extension'] == expected_info['file_without_extension']


def test_validate_config_file_not_in_config(capfd):
    file = {'file_without_extension': 'missing_report'}
    config = {'reports': [{'name': 'existing_report', 'environment': {'prod': {'workspace': 'workspace_id'}}}]}
    environment = 'prod'

    assert validate_config(file, config, environment) is None
    out, err = capfd.readouterr()
    assert "File missing_report not in the configuration file" in out

def test_validate_config_environment_not_found(capfd):
    file = {'file_without_extension': 'existing_report'}
    config = {'reports': [{'name': 'existing_report', 'environment': {'dev': {'workspace': 'workspace_id'}}}]}
    environment = 'prod'

    assert validate_config(file, config, environment) is None
    out, err = capfd.readouterr()
    assert "Environment prod not found for existing_report" in out

def test_validate_config_success():
    file = {'file_without_extension': 'existing_report'}
    config = {'reports': [{'name': 'existing_report', 'environment': {'prod': {'workspace': 'workspace_id'}}}]}
    environment = 'prod'

    result = validate_config(file, config, environment)
    assert result == {'workspace': 'workspace_id'}

@patch('main.WorkspaceManager')
def test_get_workspace_details_with_subfolder(mock_workspace_manager, capfd):
    # Setup mock return value
    mock_workspace_manager_instance = MagicMock()
    mock_workspace_manager_instance.get_workspace_id.return_value = 'workspace_id_123'
    mock_workspace_manager.return_value = mock_workspace_manager_instance

    workspace_info = {'workspace': 'TestWorkspace', 'subfolder': 'TestSubfolder'}
    access_token = 'dummy_access_token'

    workspace_id, sub_folder = get_workspace_details(workspace_info, access_token)

    # Verify return values
    assert workspace_id == 'workspace_id_123'
    assert sub_folder == 'TestSubfolder'

@patch('main.WorkspaceManager')
def test_get_workspace_details_without_subfolder(mock_workspace_manager, capfd):
    # Setup mock return value
    mock_workspace_manager_instance = MagicMock()
    mock_workspace_manager_instance.get_workspace_id.return_value = 'workspace_id_456'
    mock_workspace_manager.return_value = mock_workspace_manager_instance

    workspace_info = {'workspace': 'TestWorkspace'}
    access_token = 'dummy_access_token'

    workspace_id, sub_folder = get_workspace_details(workspace_info, access_token)

    # Verify return values
    assert workspace_id == 'workspace_id_456'
    assert sub_folder is None
