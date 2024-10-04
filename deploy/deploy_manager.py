import urllib.parse
import requests

def get_imports(workspace_id: str, access_token: str):
    url = f'https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/imports'

    response = requests.get(
        url = url,
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )

    if response.status_code != 200:
        raise Exception(
            {
                'error': {
                    'status_code': response.status_code,
                    'message': response.content,
                    'url': response.url,
                }
            }
        )

    return response.json()

def deploy (
    workspace_id: str,
    file_name: str,
    file_suffix: str,
    access_token: str,
    file_binary: bytes,
    nameConflict: str,
    sub_folder: str = None
    ):
    escaped_file_name = f"{urllib.parse.quote(file_name)}{'.rdl' if file_suffix == 'rdl' else ''}"
    url = (
        f'https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/imports?'
        f'datasetDisplayName={escaped_file_name}'
        f'&nameConflict={nameConflict}{"&subfolderObjectId=" + sub_folder if sub_folder else ""}'
    )

    response = requests.post(
        url = url,
        headers={
            'Authorization': f'Bearer {access_token}'
        },
        files={
            'file': file_binary,
        },
    )

    # lets log some shit
    print(response.status_code)
    print("---")
    print(response.json())
    print("---")
    print(response.request.headers)
    print("---")
    print(response.headers)
    print("---")

    if response.status_code not in [200, 201, 202, 204]:
        raise Exception(
            {
                'error': {
                    'status_code': response.status_code,
                    'message': response.content,
                    'url': response.url,
                }
            }
        )

