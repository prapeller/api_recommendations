from time import sleep

from core import config
from core.config import settings
from etl_postgres_to_vector_recommendations.extract import PostgresExtractor
from etl_postgres_to_vector_recommendations.helpres import dict_chunks_generator
from etl_postgres_to_vector_recommendations.load import VectorLoader
from etl_postgres_to_vector_recommendations.state_manager import StateManager
from etl_postgres_to_vector_recommendations.transform import transform
from logger_config import logger

VECTORS_CHUNK_SIZE = 500

if __name__ == '__main__':
    state_manager = StateManager()
    loader = VectorLoader(settings.API_RECOMMENDATIONS_HOST, settings.API_RECOMMENDATIONS_PORT)
    with PostgresExtractor(state_manager) as extractor:
        logger.debug('start etl loop')
        while True:
            films_data = extractor.get_films_data()
            if not films_data:
                logger.debug(f"no newly modified films were extracted...")
            else:
                film_vectors = transform(films_data)
                for film_vectors_chunk in dict_chunks_generator(film_vectors, VECTORS_CHUNK_SIZE):
                    loader.load(film_vectors_chunk)
                logger.debug(f"success: extracted and loaded vectors: {len(film_vectors)}")
                state_manager.save_state()
            sleep(config.ETL_LOOP_SLEEP_SECONDS)
