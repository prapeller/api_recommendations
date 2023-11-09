from time import sleep

from core import config
from core.config import settings
from etl_postgres_to_vector_recommendations.helpers.extract import PostgresExtractor
from etl_postgres_to_vector_recommendations.helpers.load import VectorLoader
from etl_postgres_to_vector_recommendations.helpers.stateman import StateManager
from etl_postgres_to_vector_recommendations.helpers.transform import transform
from logger_config import logger


def dict_chunks_generator(dictionary, chunk_size):
    """Yield chunk_size elements chunks from dictionary."""
    dict_keys = iter(dictionary.keys())
    while True:
        # Extract the next chunk of keys
        chunk_keys = [next(dict_keys, None) for _ in range(chunk_size)]
        # Remove any `None` keys that signify the end of the iterator
        chunk_keys = [key for key in chunk_keys if key is not None]
        if not chunk_keys:
            break
        yield {key: dictionary[key] for key in chunk_keys}


VECTORS_CHUNK_SIZE = 100

if __name__ == '__main__':
    state_manager = StateManager(config.ETL_STATE_FILENAME)
    extractor = PostgresExtractor({
        'host': settings.SEARCH_POSTGRES_HOST,
        'port': settings.SEARCH_POSTGRES_PORT,
        'database': settings.SEARCH_POSTGRES_DB,
        'user': settings.SEARCH_POSTGRES_USER,
        'password': settings.SEARCH_POSTGRES_PASSWORD,
    }, state_manager)
    loader = VectorLoader(settings.API_RECOMMENDATIONS_HOST, settings.API_RECOMMENDATIONS_PORT)

    logger.debug('start etl loop')
    while True:
        films_data = extractor.get_films_data()
        if films_data:
            film_vectors = transform(films_data)
            for film_vectors_chunk in dict_chunks_generator(film_vectors, VECTORS_CHUNK_SIZE):
                loader.load(film_vectors_chunk)
            logger.debug(f"success: extracted and loaded vectors: {len(film_vectors)}")
            state_manager.save_state()
        sleep(config.ETL_LOOP_SLEEP_SECONDS)
