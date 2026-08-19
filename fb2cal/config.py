import configparser
from pathlib import Path

from .errors import ConfigurationError
from .logger import Logger

CONFIG_FILE_NAME = 'config.ini'
CONFIG_FILE_PATH = f'config/{CONFIG_FILE_NAME}'
CONFIG_FILE_TEMPLATE_NAME = 'config-template.ini'

class Config:
    def __init__(self, path=None, required=True):
        self.logger = Logger('fb2cal').getLogger()
        self.config = configparser.RawConfigParser()
        self.path = Path(path or CONFIG_FILE_PATH)

        # Parse config
        try:
            dataset = self.config.read(self.path)
            if not dataset and required:
                raise ConfigurationError(
                    f'{self.path} does not exist. Copy {CONFIG_FILE_TEMPLATE_NAME} if needed.'
                )
        except configparser.Error as e:
            raise ConfigurationError(f'ConfigParser error: {e}') from e

    def getConfig(self):
        return self.config
