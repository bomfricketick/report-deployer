import argparse
import os
import yaml
from dotenv import load_dotenv
import time
import logging
from report_deployer.auth import authenticate
from report_deployer.workspace import get_workspace_id, get_dataset_id, post_import, get_import_id, get_imports, update_datasource, get_datasources
from report_deployer.files import get_files, file_binary, copy_and_unpack_file
from pydantic import BaseModel
import urllib.parse

logger = logging.getLogger(__name__)

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, required=True, help='path to the configuration file')
    parser.add_argument('--files', type=str, required=True, help='path to the changelog files')
    parser.add_argument('--separator', type=str, default=',', help='separator for the changelog files')
    parser.add_argument('--env', type=str, required=True, help='environment to deploy the reports')
    parser.add_argument('--log-level', type=str, default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='set the logging level')
    parser.add_argument('--log-file', type=str, help='path to the log file')
    parser.add_argument('--dry-run', action='store_true', help='simulate the deployment without making any changes')
    return parser.parse_args()

def setup_logging(log_level, log_file=None):
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    if log_file:
        logging.basicConfig(level=log_level, format=log_format, filename=log_file)
    else:
        logging.basicConfig(level=log_level, format=log_format)
    logger.setLevel(log_level)

def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def validate_config(file, config, environment):
    report_config = next((report for report in config['reports'] if report['name'] == file['file_without_extension']), None)
    if not report_config:
        logger.error(f"File {file['file_without_extension']} not in the configuration file")
        return None

    dataset = report_config.get('dataset')
    if not dataset:
        logger.error(f"Dataset not found for {file['file_without_extension']}")
        return None

    display_name = report_config.get('display_name')
    if not display_name:
        logger.debug(f"Display name not found for {file['file_without_extension']}")

    workspace_info = report_config['environment'].get(environment)
    if not workspace_info:
        logger.error(f"Environment {environment} not found for {file['file_without_extension']}")
        return None
    return report_config, workspace_info


class ReportConfig(BaseModel):
    workspace: str
    workspace_id: str = None
    dataset: str = None
    dataset_id: str = None
    environment: str = None
    subfolder: str = None
    report_name: str = None
    import_id: str = None
    existing: bool = False
    report_id: str = None


def generate_report_config(access_token: str, workspace: str, config: dict, environment: str) -> ReportConfig:
    report_config = ReportConfig(workspace=workspace)
    report_config.dataset = config['dataset']
    report_config.environment = environment
    report_config.subfolder = config['environment'].get(environment, {}).get('subfolder', None)
    report_config.workspace_id = get_workspace_id(access_token, report_config.workspace)
    report_config.dataset_id = get_dataset_id(access_token, report_config.workspace_id, report_config.dataset)
    report_config.report_name = config.get('display_name') if config.get('display_name') else config.get('name')
    report_config.import_id = get_imports(access_token, report_config.workspace_id, report_config.report_name)
    report_config.existing = True if report_config.import_id else False

    return report_config


def deploy_report(access_token, file, report_config, dry_run=False):
    if dry_run:
        logger.info(f"[DRY RUN] Would deploy report {report_config.report_name} to workspace {report_config.workspace}")
        return None

    if report_config.existing:
        logger.info(f"Report {report_config.report_name} already exists in workspace {report_config.workspace}")
        logger.info("Will overwrite it now")
        name_conflict = "CreateOrOverwrite" if file['suffix'] == "pbix" else "Overwrite"
    else:
        logger.info(f"Deploying {report_config.report_name} to workspace {report_config.workspace}...")
        name_conflict = "Abort" if file['suffix'] != "pbix" else "CreateOrOverwrite"

    display_name = f"{urllib.parse.quote(report_config.report_name)}{'.rdl' if file['suffix'] == 'rdl' else ''}"
    logger.info(f"Display name: {display_name}")

    import_id = post_import(
        access_token=access_token,
        workspace_id=report_config.workspace_id,
        file=file,
        display_name=display_name,
        name_conflict=name_conflict,
        sub_folder=report_config.subfolder
    )

    return import_id

def get_report_id_from_import_id(access_token, report_config, import_id, timeout=300, interval=5):
    start_time = time.time()

    while time.time() - start_time < timeout:
        imports_data = get_import_id(access_token, report_config.workspace_id, import_id)
        import_state = imports_data.get('importState')
        logger.info(f"Import state: {import_state}")

        if import_state == 'Succeeded':
            reports = imports_data.get('reports', [])
            if reports:
                return reports[0]['id']
            return None
        elif import_state == 'Failed':
            raise Exception(f"Import failed: {imports_data.get('error')}")
        time.sleep(interval)

    raise TimeoutError("Timeout while waiting for the import to finish")


def process_file(access_token, file, report_config, dry_run=False):
    if file['suffix'] == 'pbix':
        file['binary'] = copy_and_unpack_file(file['path'], report_config.dataset_id, report_config.workspace)
    if file['suffix'] == 'rdl':
        file['binary'] = file_binary(file['path'])

    import_id = deploy_report(access_token, file, report_config, dry_run)
    if dry_run:
        logger.info(f"[DRY RUN] Would get import ID for report {report_config.report_name} in workspace {report_config.workspace} after succesful deployment")
        return

    logger.info(f"Import ID: {import_id}")

    report_id = get_report_id_from_import_id(access_token, report_config, import_id)

    logger.info(f"Report ID: {report_id}")

    if file['suffix'] == 'rdl':
        datasource = get_datasources(access_token, report_config.workspace_id, report_id)
        data_source_name = next((item['name'] for item in datasource['value'] if 'name' in item), None)
        logger.info(f"Data source name: {data_source_name}")
        update_datasource(access_token, report_config.workspace_id, report_id, data_source_name, report_config.dataset_id)


def main():
    load_dotenv()
    args = parse_arguments()
    setup_logging(args.log_level, args.log_file)
    config = load_config(args.config)
    access_token = authenticate(os.getenv('TENANT_ID'), os.getenv('CLIENT_ID'), os.getenv('CLIENT_SECRET'))

    files = get_files(args.files, args.separator)
    for file in files:
        report_config, workspace_config = validate_config(file, config, args.env)
        logger.info(f"report_config: {report_config}")
        logger.info(f"workspace_config: {workspace_config}")
        report = generate_report_config(access_token, workspace_config['workspace'], report_config, args.env)
        logger.info(f"report: {report}")
        process_file(access_token, file, report, args.dry_run)

if __name__ == "__main__":
    main()
