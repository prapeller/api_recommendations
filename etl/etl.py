from time import sleep

from core import config
from core.config import settings
from etl_postgres_to_vector_recommendations.helpers.extract import PostgresExtractor
from etl_postgres_to_vector_recommendations.helpers.load import VectorLoader
from etl_postgres_to_vector_recommendations.helpers.stateman import StateManager
from etl_postgres_to_vector_recommendations.helpers.transform import transform
from logger_config import logger

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
            loader.load(film_vectors)
            state_manager.save_state()
        sleep(config.ETL_LOOP_SLEEP_SECONDS)
