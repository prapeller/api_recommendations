import numpy as np
import requests
from backoff import constant, on_exception
from logger_config import logger

from core.config import settings


def chunks_generator(lst, chunk_size):
    """Yield chunk_sized elements chunks from lst sequence."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


VECTORS_CHUNK_SIZE = 100


class VectorLoader:

    def __init__(self, host: str, port: int):
        self.load_url = f'http://{host}:{port}/api/v1/services-recommendations/set'

    @on_exception(constant, Exception, max_tries=500)
    def load(self, vectors: dict[str, np.ndarray]):
        vectors = {k: v.tolist() for k, v in vectors.items()}
        headers = {'Authorization': settings.SERVICE_TO_SERVICE_SECRET,
                   'Service-Name': 'etl_from_postgres_to_vector'}
        for vectors_chunk in chunks_generator(vectors, VECTORS_CHUNK_SIZE):
            try:
                response = requests.post(self.load_url, json=vectors_chunk, headers=headers)
                response.raise_for_status()
                logger.debug("Vectors successfully sent to the Vector service.")
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to send vectors to the Vector service. Error: {str(e)}")
                raise
