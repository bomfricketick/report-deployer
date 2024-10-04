from os.path import exists
import os
from pathlib import Path

import yaml


def get_files(files: str, separator: str):
    file_list: list[str] = files.split(separator)
    print("Debug - file_list:", file_list)  # Debug print to check the split filenames
    report_list = [
        {
            'file_name': os.path.basename(file),
            'file_suffix': Path(file).suffix[1:],
            'file_without_extension': os.path.splitext(os.path.basename(file))[0],
            'file_path': Path(file),
            'file_binary': get_file_binary(file),
        }
        for file in file_list
        if Path(file).suffix[1:] in ('pbix', 'rdl')
    ]

    return report_list


def get_file_binary(file_path: str) -> bytes:
    if not exists(file_path):
        return None

    with open(file_path, 'rb') as file:
        bin_file: bytes = file.read()
        return bin_file
