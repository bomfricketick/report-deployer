import argparse
import os
import yaml
from dotenv import load_dotenv
from auth.auth_manager import AuthManager, WorkspaceManager
from deploy.file_manager import get_files
from deploy.deploy_manager import deploy, get_imports

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, required=True, help='path to the configuration file')
    parser.add_argument('--files', type=str, required=True, help='path to the changelog files')
    parser.add_argument('--separator', type=str, default=',', help='separator for the changelog files')
    parser.add_argument('--env', type=str, required=True, help='environment to deploy the reports')
    return parser.parse_args()

def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def authenticate(tenant_id, client_id, client_secret):
    auth_manager = AuthManager(tenant_id, client_id, client_secret)
    try:
        return auth_manager.authenticate()
    except Exception as e:
        print(f"Authentication failed: {e}")
        exit(1)

def process_files(files, config, environment, access_token):
    workspace_manager = WorkspaceManager(access_token)
    for file in files:
        report_config = next((report for report in config['reports'] if report['name'] == file['file_without_extension']), None)
        if not report_config:
            print(f"File {file['file_without_extension']} not in the configuration file")
            continue
        workspace_info = report_config['environment'].get(environment)
        if not workspace_info:
            print(f"Environment {environment} not found for {file['file_without_extension']}")
            continue
        workspace_id = workspace_manager.get_workspace_id(workspace_info['workspace'])

        sub_folder = workspace_info.get('subfolder')
        print(f"Sub folder: {sub_folder}")

        imports = get_imports(workspace_id, access_token)
        file_exists = any(import_['name'] == file['file_name'] for import_ in imports['value'])
        if file_exists:
            print(f"Report {file['file_name']} already exists in workspace {workspace_id}")
            print("Will overwrite it now")
            for import_ in imports['value']:
                if import_['name'] == file['file_name']:
                    print(import_)
            deploy(
                workspace_id = workspace_id,
                file_name = file['file_without_extension'],
                file_suffix = file['file_suffix'],
                access_token = access_token,
                file_binary = file['file_binary'],
                nameConflict = "CreateOrOverwrite" if file['file_suffix'] == "pbix" else "Overwrite",
                sub_folder = sub_folder
            )
        else:
            print(f"Deploying {file['file_name']} to workspace {workspace_id}...")
            deploy(
                workspace_id = workspace_id,
                file_name = file['file_without_extension'],
                file_suffix = file['file_suffix'],
                access_token = access_token,
                file_binary = file['file_binary'],
                nameConflict = "Abort" if file['file_suffix'] != "pbix" else "CreateOrOverwrite",
                sub_folder = sub_folder
            )

def main():
    load_dotenv()
    args = parse_arguments()
    config = load_config(args.config)
    access_token = authenticate(os.getenv('TENANT_ID', 'default_tenant_id'), os.getenv('CLIENT_ID', 'default_client_id'), os.getenv('CLIENT_SECRET', 'default_client_secret'))
    files = get_files(files=args.files, separator=args.separator)
    process_files(files, config, args.env, access_token)

if __name__ == "__main__":
    main()
