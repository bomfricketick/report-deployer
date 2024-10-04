from os.path import exists
from pathlib import Path

import yaml


def get_files(files: str, separator: str):
    file_list: list[str] = files.split(separator)

    report_list = [
        {
            'file_name': Path(file).name,
            'file_path': Path(file),
            'file_binary': get_file_binary(file),
        }
        for file in file_list
        if file.endswith('.pbix') or file.endswith('.rdl')
    ]

    return report_list


def get_file_binary(file_path: str) -> bytes:
    if not exists(file_path):
        return None

    with open(file_path, 'rb') as file:
        bin_file: bytes = file.read()
        return bin_file
