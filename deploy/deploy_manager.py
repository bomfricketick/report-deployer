from urllib import parse
import requests

def deploy (
    workspace_id: str,
    report_name: str,
    file_suffix: str,
    access_token: str,
    file_binary: bytes
    ):

    if file_suffix == 'pbix':
        file_name = f'{report_name}.pbix'
    if file_suffix == 'rdl':
        file_name = f'{report_name}.rdl'

    print(f'Uploading {report_name} to workspace {workspace_id}...')
    url = (
        f'https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/imports?'
        f'datasetDisplayName={parse.quote(file_name)}&'
        f'nameConflict={"CreateOrOverwrite" if file_suffix == "pbix" else "Overwrite"}'
    )

    response = requests.post(
        url = url,
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
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

