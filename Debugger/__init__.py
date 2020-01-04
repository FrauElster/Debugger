import logging
import os

from Debugger.Filenames import FILENAMES
from Debugger.utils.filehandler import check_if_dir_exists, to_abs_file_path

LOGGER: logging.Logger = logging.getLogger('Debugger')


def setup_logger() -> None:
    """
    setup for the various handler for logging
    :return:
    """
    LOGGER.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s \t|%(asctime)s \t| %(name)s \t|  %(message)s')

    if not check_if_dir_exists(FILENAMES.LOG_DIR):
        os.mkdir(to_abs_file_path(FILENAMES.LOG_DIR))

    file_handler: logging.FileHandler = logging.FileHandler(to_abs_file_path(FILENAMES.LOG), mode='w')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    console_handler: logging.StreamHandler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)

    LOGGER.addHandler(file_handler)
    LOGGER.addHandler(console_handler)
    LOGGER.info('Filehandler and Console_Handler were born, let\'s start logging')


setup_logger()
