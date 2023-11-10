import datetime as dt

from core import config
from core.config import BASE_DIR
from logger_config import logger

STATE_FILE_PATH = BASE_DIR / config.ETL_STATE_FILENAME
STATE_FILE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
default_datetime = dt.datetime(1970, 1, 1)


class StateManager:
    def __init__(self):
        self.state = self.load_state()

    def load_state(self) -> dt.datetime:
        """return datetime loaded from 'state' file.
        If 'state' file does not exist (there's no state yet) - return 'default' datetime"""
        try:
            with open(STATE_FILE_PATH, 'r') as f:
                last_modified_timestamp_str = f.read()
                if last_modified_timestamp_str:
                    last_modified_at = dt.datetime.strptime(last_modified_timestamp_str.strip(), STATE_FILE_TIME_FORMAT)
                    self.state = last_modified_at
                    logger.debug(f"loaded state from {STATE_FILE_PATH}: {last_modified_at=:}")
                    return last_modified_at
                else:
                    return default_datetime
        except FileNotFoundError:
            return default_datetime

    @staticmethod
    def save_state():
        """save current_timestamp to state file"""

        with open(STATE_FILE_PATH, 'w') as f:
            saved_at = dt.datetime.now().strftime(STATE_FILE_TIME_FORMAT)
            f.write(saved_at)
            logger.debug(f"saved to {STATE_FILE_PATH}: {saved_at}")
