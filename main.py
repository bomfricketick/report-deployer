from dotenv import load_dotenv
import argparse
import os
from auth.auth_manager import AuthManager, WorkspaceManager
from deploy.file_manager import get_files
from deploy.deploy_manager import deploy

def main():
    load_dotenv()
    tenant_id = os.getenv('TENANT_ID', 'default_tenant_id')
    client_id = os.getenv('CLIENT_ID', 'default_client_id')
    client_secret = os.getenv('CLIENT_SECRET', 'default_client_secret')

    # use argparse to get a yaml file with configuration
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, help='path to the configuration file')
    parser.add_argument('--CHANGED_FILES', type=str, help='path to the changelog files')
    parser.add_argument('--SEPARATOR', type=str, help='separator for the changelog files')
    args = parser.parse_args()


    if args.CHANGED_FILES is None:
        print("No files to deploy")
        return
    else:
        files = get_files(
            files = args.CHANGED_FILES, separator = args.SEPARATOR
        )
        
    auth_manager = AuthManager(tenant_id, client_id, client_secret)

    try:
        access_token = auth_manager.authenticate()
        print(f"Successfully authenticated. Access token: {access_token}")
    except Exception as e:
        print(f"An error occurred: {e}")



    # Check the config file if report is listed and which workspace to deploy to
    with open(args.config, 'r') as file:
        config = yaml.safe_load(file)

    for file in files:
        if file['file_binary'] is None:
            continue

        # Check if the file is in the config file and to what workspace it should be deployed
        if file['file_name'] not in config['reports']:
            print(f"File {file['file_name']} not in the configuration file")


        workspace = config['reports'][file['file_name']]['workspace']

        workspace_manager = WorkspaceManager(access_token)
        workspace_id = workspace_manager.get_workspace_id(workspace)



        deploy(
            workspace_id = os.getenv('WORKSPACE_ID'),
            report_name = file['file_name'],
            file_suffix = file['file_path'].suffix[1:],
            access_token = access_token,
            file_binary = file['file_binary'],
        )


if __name__ == "__main__":
    main()
