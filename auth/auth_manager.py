import requests

class AuthManager:
    def __init__(self, tenant_id, client_id, client_secret):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        self.scope = "https://graph.microsoft.com/.default"  # Example scope, adjust as needed

    def authenticate(self):
        # Prepare the data for the token request
        data = {
            "client_id": self.client_id,
            "scope": self.scope,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }

        # Send a POST request to the token endpoint
        response = requests.post(self.token_url, data=data)
        response_data = response.json()

        if response.status_code == 200:
            # Extract the token from the response
            access_token = response_data.get("access_token")
            return access_token
        else:
            raise Exception(f"Authentication failed: {response_data.get('error_description')}")


class WorkspaceManager:
    def __init__(self, access_token):
        self.access_token = access_token

    def get_workspace_id(self, workspace_name):
        url = "https://api.powerbi.com/v1.0/myorg/groups"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        # Send a GET request to retrieve the list of workspaces
        response = requests.get(url, headers=headers)
        response_data = response.json()

        if response.status_code == 200:
            # Find the workspace ID based on the workspace name
            for workspace in response_data["value"]:
                if workspace["name"] == workspace_name:
                    return workspace["id"]
            raise Exception(f"Workspace '{workspace_name}' not found.")
        else:
            raise Exception(f"Failed to retrieve workspaces: {response_data.get('error')}")
