import numpy as np
import requests
from backoff import constant, on_exception
from logger_config import logger

from core.config import settings


def load_exception_handler(details):
    e = details['exception']
    message = f"can't load vectors: {e}".replace('\n', ' ')
    tries = details['tries']
    wait = details['wait']
    logger.error(f'{tries=:}, wait:{wait:0.1f}, {message=:}')


class VectorLoader:

    def __init__(self, host: str, port: int):
        self.load_url = f'http://{host}:{port}/api/v1/services-vectors/'

    @on_exception(constant, Exception, max_tries=500, on_backoff=load_exception_handler)
    def load(self, vectors: dict[str, np.ndarray]):
        vectors = {k: v.tolist() for k, v in vectors.items()}
        headers = {'Authorization': settings.SERVICE_TO_SERVICE_SECRET,
                   'Service-Name': 'etl_from_postgres_to_vector'}
        logger.debug(f'loading vectors: {len(vectors)}')
        response = requests.post(self.load_url, json=vectors, headers=headers)
        response.raise_for_status()
