import requests
import re

def get_workspace_id(access_token, workspace_name):
    url = f'https://api.powerbi.com/v1.0/myorg/groups'
    response = requests.get(
        url=url,
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    )
    response.raise_for_status()
    response_json = response.json()
    workspace_id = next(workspace['id'] for workspace in response_json['value'] if workspace['name'] == workspace_name)
    return workspace_id

def get_dataset_id(access_token, workspace_id, dataset_name):
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets"
    response = requests.get(
        url=url,
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    )
    response.raise_for_status()
    dataset_id = next(dataset['id'] for dataset in response.json()['value'] if dataset['name'] == dataset_name)
    return dataset_id

def get_report_id(access_token, workspace_id, report_name):
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports"
    response = requests.get(
        url=url,
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    )
    response.raise_for_status()
    report_id = next(report['id'] for report in response.json()['value'] if report['name'] == report_name)
    return report_id

def get_imports(access_token, workspace_id, import_name):
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/imports"
    def import_exists(imports: list, import_name: str) -> bool:
        extensions = ['', '.pbix', '.rdl']
        return any(import_['name'] == f"{import_name}{ext}" for ext in extensions for import_ in imports)

    response = requests.get(
        url=url,
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    )
    response.raise_for_status()
    imports = response.json()['value']

    # Check if the import exists
    if import_exists(imports, import_name):
        import_id = next(import_['id'] for import_ in imports if import_['name'] == import_name or import_['name'] == f"{import_name}.pbix" or import_['name'] == f"{import_name}.rdl")
    else:
        import_id = None

    return import_id

def get_import_id(access_token, workspace_id, import_id):
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/imports/{import_id}"
    response = requests.get(
        url=url,
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )
    response.raise_for_status()
    return response.json()

def post_import(access_token, workspace_id, file, display_name, name_conflict, sub_folder):
    url = (
        f'https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/imports?'
        f'datasetDisplayName={display_name}'
        f'&nameConflict={name_conflict}{"&subfolderId=" + sub_folder if sub_folder else ""}'
    )

    response = requests.post(
        url = url,
        headers={
            'Authorization': f'Bearer {access_token}'
        },
        files={
            'file': file['binary'],
        },
    )

    response.raise_for_status()
    return response.json().get('id')


def get_datasources(access_token, workspace_id, report_id):
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/{report_id}/datasources"
    response = requests.get(
        url=url,
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )
    response.raise_for_status()
    return response.json()

def update_datasource(access_token, workspace_id, report_id, data_source_name, dataset_id):
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/{report_id}/Default.UpdateDatasources"

    response = requests.post(
        url=url,
        headers={
            'Authorization': f'Bearer {access_token}'
        },
                    # 'datasourceName': f"{formatted_string(workspace)}_{formatted_string(dataset)}",
        json={
            'updateDetails': [
                {
                    'dataSourceName': data_source_name,
                    'datasourceType': "AnalysisServices",
                    'connectionDetails': {
                        'server': "pbiazure://api.powerbi.com/",
                        'database': f"sobe_wowvirtualserver-{dataset_id}",
                    }
                }
            ]
        }
    )

    response.raise_for_status()
    return response.status_code
