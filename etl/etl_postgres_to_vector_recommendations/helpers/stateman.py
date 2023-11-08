import datetime
from typing import AnyStr

from core.config import BASE_DIR
from logger_config import logger


class StateManager:
    def __init__(self, state_file: AnyStr):
        """
        :param state_file: file where state will be saved
        """
        self.state_file = BASE_DIR / state_file
        self.default = datetime.datetime(1970, 1, 1)
        self.state = self.load_state()
        self.time_format = '%Y-%m-%d %H:%M:%S'

    def load_state(self):
        """return datetime loaded from 'state' file.
        If 'state' file does not exist (theres no state yet) - return 'default' datetime(1970, 1, 1)
        """
        try:
            with open(self.state_file, 'r') as f:
                state = f.read()
                if state:
                    a = state.strip()
                    saved_at = datetime.datetime.strptime(a, self.time_format)
                    logger.debug(f"loaded from {self.state_file}: {saved_at}")
                    self.state = saved_at
                    return self.state
                else:
                    return self.default.strftime(self.time_format)
        except FileNotFoundError:
            return self.default

    def save_state(self):
        """
        save current time to file
        :return:
        """
        with open(self.state_file, 'w') as f:
            saved_at = datetime.datetime.now().strftime(self.time_format)
            f.write(saved_at)
            logger.debug(f"saved to {self.state_file}: {saved_at}")
