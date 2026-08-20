import atexit
import logging
import os

LOGGING_FILE_PATH = "logs/fb2cal.log"


class Logger:
    def __init__(self, name):
        # Setup logger
        if not os.path.exists(os.path.dirname(LOGGING_FILE_PATH)):
            os.makedirs(os.path.dirname(LOGGING_FILE_PATH), exist_ok=True)

        if not logging.getLogger().handlers:
            logging.basicConfig(
                format="[%(asctime)s] %(name)s %(levelname)s (%(funcName)s) %(message)s",
                level=logging.INFO,
                handlers=[
                    logging.StreamHandler(),
                    logging.FileHandler(LOGGING_FILE_PATH, encoding="UTF-8"),
                ],
            )
            atexit.register(logging.shutdown)

        self.logger = logging.getLogger(name)

    def getLogger(self):
        return self.logger
