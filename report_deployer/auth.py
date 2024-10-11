import requests

def authenticate(tenant_id, client_id, client_secret):
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    scope = "https://analysis.windows.net/powerbi/api/.default"

    data = {
        "client_id": client_id,
        "scope": scope,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
    }

    response = requests.post(url=token_url, data=data)
    response.raise_for_status()
    access_token = response.json()['access_token']
    return access_token
