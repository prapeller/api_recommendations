import numpy as np
import requests
from backoff import constant, on_exception
from logger_config import logger

from core.config import settings


def dict_chunks_generator(dictionary, chunk_size):
    """Yield chunk_size elements chunks from dictionary."""
    it = iter(dictionary.items())
    for first in it:
        chunk = dict([first] + [next(it, (None, None)) for _ in range(chunk_size - 1)])
        yield {k: v for k, v in chunk if k is not None}


VECTORS_CHUNK_SIZE = 100


def load_exception_handler(details):
    e = details['exception']
    message = f'{e.error} {e.info}'.replace('\n', ' ')
    tries = details['tries']
    wait = details['wait']
    logger.error(f'{tries=:}, wait:{wait:0.1f}, {message=:}')


class VectorLoader:

    def __init__(self, host: str, port: int):
        self.load_url = f'http://{host}:{port}/api/v1/services-recommendations/set'

    @on_exception(constant, Exception, max_tries=500, on_backoff=load_exception_handler)
    def load(self, vectors: dict[str, np.ndarray]):
        vectors = {k: v.tolist() for k, v in vectors.items()}
        headers = {'Authorization': settings.SERVICE_TO_SERVICE_SECRET,
                   'Service-Name': 'etl_from_postgres_to_vector'}
        for vectors_chunk in dict_chunks_generator(vectors, VECTORS_CHUNK_SIZE):
            try:
                logger.debug(f'loading vectors_chunk: {len(vectors_chunk)} of {len(vectors)}')
                response = requests.post(self.load_url, json=vectors_chunk, headers=headers)
                response.raise_for_status()
                logger.debug("Vectors successfully sent to the Vector service.")
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to send vectors to the Vector service. Error: {str(e)}")
                raise
