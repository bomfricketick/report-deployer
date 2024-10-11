import pytest
from unittest.mock import patch, MagicMock
from report_deployer.auth import authenticate
from report_deployer.workspace import get_workspace_id, get_dataset_id, get_report_id, post_import
from report_deployer.app import parse_arguments


def test_parse_arguments(monkeypatch):
    test_args = [
        '--config', 'config.yaml',
        '--files', 'changelog.csv',
        '--env', 'production',
        '--log-level', 'DEBUG',
        '--log-file', 'app.log',
        '--dry-run'
    ]
    monkeypatch.setattr('sys.argv', ['app.py'] + test_args)
    args = parse_arguments()

    assert args.config == 'config.yaml'
    assert args.files == 'changelog.csv'
    assert args.env == 'production'
    assert args.log_level == 'DEBUG'
    assert args.log_file == 'app.log'
    assert args.dry_run is True

    
def setup_mock_response(mock_get, json_data):
    mock_response = MagicMock()
    mock_response.json.return_value = json_data
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

def assert_mock_get_called_once(mock_get, url, access_token):
    mock_get.assert_called_once_with(
        url=url,
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    )

@patch('requests.post')
def test_authenticate(mock_post):
    mock_post.return_value = MagicMock(
        json=MagicMock(return_value={'access_token': 'mock_access_token'}),
        raise_for_status=MagicMock()
    )

    access_token = authenticate('mock_tenant_id', 'mock_client_id', 'mock_client_secret')

    assert access_token == 'mock_access_token'
    mock_post.assert_called_once()

@patch('requests.get')
def test_get_workspace_id(mock_get):
    setup_mock_response(mock_get, {'value': [{'id': 'workspace_id_123', 'name': 'TestWorkspace'}]})

    access_token = 'mock_access_token'
    workspace_name = 'TestWorkspace'
    workspace_id = get_workspace_id(access_token, workspace_name)

    assert workspace_id == 'workspace_id_123'
    assert_mock_get_called_once(mock_get, 'https://api.powerbi.com/v1.0/myorg/groups', access_token)

@patch('requests.get')
def test_get_dataset_id(mock_get):
    setup_mock_response(mock_get, {'value': [{'id': 'dataset_id_456', 'name': 'TestDataset'}]})

    access_token = 'mock_access_token'
    workspace_id = 'workspace_id_123'
    dataset_name = 'TestDataset'
    dataset_id = get_dataset_id(access_token, workspace_id, dataset_name)

    assert dataset_id == 'dataset_id_456'
    assert_mock_get_called_once(mock_get, f'https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets', access_token)

@patch('requests.get')
def test_get_report_id(mock_get):
    setup_mock_response(mock_get, {'value': [{'id': 'report_id_789', 'name': 'TestReport'}]})

    access_token = 'mock_access_token'
    workspace_id = 'workspace_id_123'
    report_name = 'TestReport'
    report_id = get_report_id(access_token, workspace_id, report_name)

    assert report_id == 'report_id_789'
    assert_mock_get_called_once(mock_get, f'https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports', access_token)

