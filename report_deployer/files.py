from pathlib import Path
from typing import Optional, List, Dict
import shutil
import zipfile
import json
import os

def get_files(files: str, separator: str) -> list:
    files = files.split(separator)
    return [
        {
            'name': Path(file).name,
            'suffix': Path(file).suffix[1:],
            'file_without_extension': Path(file).stem,
            'path': Path(file),
        }
        for file in files
        if Path(file).suffix[1:] in ('rdl', 'pbix')
    ]

def file_binary(file_path: Path) -> Optional[bytes]:
    if not file_path.exists():
        raise FileNotFoundError(f"File {file_path} not found")
    return file_path.read_bytes()


def copy_and_unpack_file(file_path: Path, dataset_id: str, workspace: str) -> Optional[bytes]:
    if not file_path.exists() or file_path.suffix != ".pbix":
        raise FileNotFoundError(f"File {file_path} not found or not a .pbix file")

    temp_folder = Path("temp")
    temp_folder.mkdir(exist_ok=True)

    try:
        zip_path = temp_folder / f"{file_path.stem}.zip"
        shutil.copy(file_path, zip_path)

        unpack_folder = temp_folder / file_path.stem
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(unpack_folder)

        connections_content = {
            "Version": 2,
            "Connections": [
                {
                    "Name": "EntityDataSource",
                    "ConnectionString": f"Data Source=pbiazure://api.powerbi.com;Initial Catalog={dataset_id};Identity Provider=\"https://login.microsoftonline.com/common, https://analysis.windows.net/powerbi/api, 7f67af8a-fedc-4b08-8b4e-37c4d127b6cf\";Integrated Security=ClaimsToken",
                    "ConnectionType": "pbiServiceLive",
                    "PbiServiceModelId": 0,
                    "PbiModelVirtualServerName": "sobe_wowvirtualserver",
                    "PbiModelDatabaseName": f"{dataset_id}",
                }
            ],
        }

        connections_file = unpack_folder / "Connections"
        if not connections_file.exists():
            raise FileNotFoundError(f"Connections file not found in {unpack_folder}")

        with connections_file.open("w", encoding="utf-8") as f:
            json.dump(connections_content, f)

        new_zip_path = temp_folder / f"{file_path.stem}_modified.zip"
        with zipfile.ZipFile(new_zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
            for folder_name, subfolders, files in os.walk(unpack_folder):
                for file in files:
                    file_path = Path(folder_name) / file
                    zip_ref.write(file_path, file_path.relative_to(unpack_folder))

        new_bpix_path = new_zip_path.with_suffix(".pbix")
        new_zip_path.rename(new_bpix_path)

        file_binary = new_bpix_path.read_bytes()

        return file_binary
    finally:
        shutil.rmtree(temp_folder, ignore_errors=True)


