import logging
import os
from datetime import datetime

LOG_FILE = f"{datetime.now().strftime('%Y%m%d_%H.%M.%S')}.log"
logs_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "logs",
    datetime.now().strftime("%Y_%m"),
)
os.makedirs(logs_path, exist_ok=True)

LOG_FILE_PATH = os.path.join(logs_path, LOG_FILE)


class CustomLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        handler = logging.FileHandler(LOG_FILE_PATH)
        formatter = logging.Formatter(
            fmt="[%(asctime)s] Line %(lineno)d %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def info(self, msg):
        return self.logger.info(msg)

    def warning(self, msg):
        return self.logger.warning(msg)

    def error(self, msg):
        return self.logger.error(msg)

    def critical(self, msg):
        return self.logger.critical(msg)


if __name__ == "__main__":
    logger = CustomLogger(__name__)
    logger.info("Test info")
