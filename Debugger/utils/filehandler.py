import dataclasses
import datetime
import glob
import json
import logging
import os
import pickle
import shutil
from decimal import Decimal
from typing import List, Any, Optional

LOGGER = logging.getLogger(__name__)


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        if isinstance(o, datetime.datetime):
            return o.strftime("%H:%M:%S %d.%m.%y")
        if isinstance(o, Decimal):
            return float(o)
        else:
            return o


def to_rel_file_path(abs_path: str):
    package_directory = os.path.dirname(os.path.abspath(__file__))
    return os.path.relpath(abs_path, os.path.join(package_directory, '..', '..'))


def to_abs_file_path(file_name: str) -> str:
    """ :returns an existing absolute file path based on the project root directory + file_name"""
    package_directory = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(package_directory, '..', '..', file_name)
    path = os.path.normpath(path)
    return path


def create_dir(dir_name: str, is_abs: bool = False) -> str:
    """
    creates a directory if it is not already exiting
    :param is_abs: determines if the given path is absolute or relative to project root
    :param dir_name: directory name
    :return: the absolute path to the directory
    """
    dir_path: str = dir_name if is_abs else to_abs_file_path(dir_name)
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)
        LOGGER.info(f'created {dir_name} directory')

    return dir_path


def delete_file(filename: str, is_abs: bool = False) -> bool:
    filename = filename if is_abs else to_abs_file_path(filename)
    if os.path.isfile(filename):
        os.remove(filename)
        LOGGER.info(f'Removed file {filename}')
        return True
    else:
        if not os.path.exists(filename):
            LOGGER.warning(f'"{filename}" does not exist')
        else:
            LOGGER.warning(f'"{filename}" is not a file')
        return False


def delete_dir(dir_name: str, is_abs: bool = False) -> bool:
    """
    deletes a directory if it exists
    :param is_abs: determines if the given path is absolute or relative to project root
    :param dir_name: directory name
    :return: whether it exists or not
    """
    dir_path: str = dir_name if is_abs else to_abs_file_path(dir_name)
    if os.path.isdir(dir_path):
        shutil.rmtree(dir_path, ignore_errors=True)
        LOGGER.info(f'Removed directory "{dir_name}"')
        return True
    if not os.path.exists(dir_path):
        LOGGER.warning(f'"{dir_name}" does not exists')
    else:
        LOGGER.warning(f'"{dir_name}" is not a directory')
    return False


def check_if_file_exists(filename: str, is_abs: bool = False) -> bool:
    """
    Checks if a file exist and if it is a file
    :param is_abs: determines if the given path is absolute or relative to project root
    :param filename: the file to check
    :return: whether it exists and is a file
    """
    filepath: str = to_abs_file_path(filename)
    if not os.path.exists(filepath):
        LOGGER.warning(f'{filepath} does not exist')
        return False
    if not os.path.isfile(filepath):
        LOGGER.warning(f'{filepath} is not a file')
        return False
    return True


def check_if_dir_exists(dirname: str, is_abs: bool = False) -> bool:
    """
    Checks if a directory exist and if it is a directory
    :param dirname: the directory to check
    :param is_abs: determines if the given path is absolute or relative to project root
    :return: whether it exists and is a file
    """
    dir_path: str = dirname if is_abs else to_abs_file_path(dirname)
    if not os.path.exists(dir_path):
        LOGGER.warning(f'{dir_path} does not exist')
        return False
    if not os.path.isdir(dir_path):
        LOGGER.warning(f'{dir_path} is not a directory')
        return False
    return True


def save_file(file_name: str, data: Any, is_abs: bool = False, force_pickle: bool = False) -> None:
    """ writes a file, if a file with file_name already exists its content gets overwritten """
    file_path: str = file_name if is_abs else to_abs_file_path(file_name)
    if not os.path.isfile(file_path):
        LOGGER.info(f'{file_path} created')
    if force_pickle:
        with open(file_path, 'wb') as fb:
            pickle.dump(obj=data, file=fb)
            return
    with open(file_path, 'w') as f:
        if get_file_ending(file_path) == 'json':
            json.dump(data, f, cls=EnhancedJSONEncoder, )
        else:
            f.write(data)
    LOGGER.info(f'saved {file_name}')


def append_to_file(file_name: str, data: Any, is_abs: bool = False, force_pickle: bool = False) -> bool:
    ok: bool = True
    if not check_if_file_exists(file_name, is_abs=is_abs):
        save_file(file_name=file_name, data=data, is_abs=is_abs, force_pickle=force_pickle)
        return ok

    content = load_file(filename=file_name, is_abs=is_abs, force_pickle=force_pickle)
    if isinstance(content, list):
        if isinstance(data, list):
            content.extend(data)  # type: ignore
        else:
            content.append(data)  # type: ignore
    elif isinstance(content, str):
        content += f'\n{data}'  # type: ignore
    elif isinstance(content, dict) and isinstance(data, dict):
        try:
            content.update(data)  # type: ignore
        except Exception as e:
            LOGGER.warning(f'{e.__class__.__name__} occurred while trying to append to file {file_name}: {e}')
            ok = False
    save_file(file_name=file_name, data=content, force_pickle=force_pickle)
    return ok


def get_files_in_dir(dirname: str, endings: List[str] = None, recursive: bool = False, is_abs: bool = False) \
        -> Optional[List[str]]:
    """
    :param dirname: the directory name or path specific to project root
    :param is_abs: determines if the given path is absolute or relative to project root
    :param endings: A optional list of str with str. Only file that end with one of the endings will be returned
                    endings e.g.: "png", "txt", "css" so NOT ".css"
    :param recursive: if files in subfolders should be returned
    :return: a list with filepaths
    """
    if not check_if_dir_exists(dirname):
        LOGGER.info(f"Directory {dirname} doesnt exist in {to_abs_file_path('')}")
        return None

    if not endings:
        endings = ["*"]
    dir_path: str = dirname if is_abs else to_abs_file_path(dirname)
    files: List[str] = []
    for ending in endings:
        files.extend(glob.glob(dir_path + f'{"/**" if recursive else ""}/*.{ending}', recursive=recursive))
    return files


def load_file(filename: str, is_abs: bool = False, force_pickle: bool = False) -> Any:
    """
    loads contents of a file. If it is a json file, it tries to parse it.
    :param filename: the path to the file to load
    :param is_abs: determines if the given path is absolute or relative to project root
    :return:
    """
    file_path: str = filename if is_abs else to_abs_file_path(filename)
    if not check_if_file_exists(file_path):
        return None
    if force_pickle:
        with open(file_path, 'rb') as file:
            try:
                return pickle.load(file)
            except EOFError:
                return None
    with open(file_path, 'r') as stream:
        if get_file_ending(file_path) == 'json':
            try:
                return json.load(stream)
            except json.JSONDecodeError as exc:
                LOGGER.error(f'JSON parsing error: {exc}')
                return None

        else:
            return stream.read()


def get_file_base(filepath: str) -> str:
    """
    :param filepath: the absolute filepath
    :return: the filename / filebase
    """
    return os.path.basename(filepath)


def get_file_ending(filepath: str) -> str:
    """
    :param filepath: the path to a file
    :return: the ending of a file
    """
    return filepath.split(".")[-1]
