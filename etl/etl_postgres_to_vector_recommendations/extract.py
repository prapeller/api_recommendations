from datetime import datetime
from typing import Any, Dict, Generator, List

import psycopg2
from backoff import constant, on_exception

from core.config import settings
from etl_postgres_to_vector_recommendations.state_manager import StateManager
from logger_config import logger


def extract_exception_handler(details):
    e = details['exception']
    message = f"can't extract films: {e}".replace('\n', ' ')
    tries = details['tries']
    wait = details['wait']
    logger.error(f'{tries=:}, wait:{wait:0.1f}, {message=:}')


@on_exception(constant, Exception, max_tries=120, on_backoff=extract_exception_handler)
def connect():
    return psycopg2.connect(host=settings.SEARCH_POSTGRES_HOST,
                            port=settings.SEARCH_POSTGRES_PORT,
                            user=settings.SEARCH_POSTGRES_USER,
                            password=settings.SEARCH_POSTGRES_PASSWORD,
                            database=settings.SEARCH_POSTGRES_DB)


class PostgresExtractor:
    def __init__(self, state_manager: StateManager):
        self.conn = connect()
        self.cursor = self.conn.cursor()
        self.state_manager = state_manager
        self.last_modified_at = self.state_manager.load_state()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.conn.close()

    def execute_query_batched(self, query: str, batch_size=100) -> Generator[Dict, Any, Any]:
        """yield batch_size of executed query results """

        self.cursor.execute(query)
        while True:
            results = self.cursor.fetchmany(batch_size)
            if not results:
                break
            for row in results:
                yield row

    def get_modified_films_uuids(self, modified=True) -> List:
        """get films which were modified (or if its genres or persons were modified)
        if modified=False - get all films"""

        if modified:
            films_query = f"""
            select distinct fm.uuid from (
                select film.uuid as uuid
                FROM content.film AS film
                LEFT JOIN content.film_person AS film_person ON film_person.film_uuid = film.uuid
                LEFT JOIN content.person AS person ON person.uuid = film_person.person_uuid
                LEFT JOIN content.film_genre AS film_genre ON film_genre.film_uuid = film.uuid
                LEFT JOIN content.genre AS genre ON genre.uuid = film_genre.genre_uuid
                WHERE GREATEST(film.updated_at, person.updated_at, genre.updated_at) > '{self.last_modified_at}'
                ORDER BY film.uuid) as fm"""

        else:
            films_query = """select distinct fm.uuid from (
                                select distinct film.uuid
                                from content.film as film
                                left join content.film_person as film_person on film_person.film_uuid = film.uuid
                                left join content.person as person on person.uuid = film_person.person_uuid
                                left join content.film_genre as film_genre on film_genre.film_uuid = film.uuid
                                left join content.genre as genre on genre.uuid = film_genre.genre_uuid
                                order by film.uuid) as fm"""

        rows = self.execute_query_batched(films_query)
        extracted = []
        for row in rows:
            extracted.append(row[0])
        return extracted

    def get_films_data(self) -> List[Dict]:
        """get modified films data (uuid, description, type, genres_names)"""

        self.last_modified_at = self.state_manager.load_state()
        if self.last_modified_at == datetime(1970, 1, 1):
            uuids = self.get_modified_films_uuids(modified=False)
        else:
            uuids = self.get_modified_films_uuids(modified=True)
        if not uuids:
            return []
        film_uuids = [str(_uuid).replace("'", "''") for _uuid in uuids]
        film_uuids_string = ",".join([f"'{id}'" for id in film_uuids])
        films_description_type_genresnames_query = f"""
                SELECT
                    film.uuid,
                    film.description,
                    film.type,
                    ARRAY_AGG(genre.name) AS genre_names
                FROM
                    content.film film
                    LEFT JOIN content.film_genre fg ON fg.film_uuid = film.uuid
                    LEFT JOIN content.genre genre ON genre.uuid = fg.genre_uuid
                WHERE
                    film.uuid IN ({film_uuids_string})
                GROUP BY film.uuid, film.description, film.type
                ORDER BY film.uuid
            """
        films_data_generator = self.execute_query_batched(films_description_type_genresnames_query)
        films_data = []
        for film_data in films_data_generator:
            films_data.append(film_data)
        return films_data
