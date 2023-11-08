import numpy as np
import requests
from backoff import constant, on_exception

from core.config import settings
from logger_config import logger


class VectorLoader:

    def __init__(self, host: str, port: int):
        self.load_url = f'http://{host}:{port}/api/v1/services-recommendations/set'

    @on_exception(constant, Exception, max_tries=500)
    def load(self, vectors: dict[str, np.ndarray]):
        vectors = {k: v.tolist() for k, v in vectors.items()}
        headers = {'Authorization': settings.SERVICE_TO_SERVICE_SECRET,
                   'Service-Name': 'etl_from_postgres_to_vector'}
        try:
            response = requests.post(self.load_url, json=vectors, headers=headers)
            response.raise_for_status()
            logger.debug("Vectors successfully sent to the Vector service.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send vectors to the Vector service. Error: {str(e)}")
