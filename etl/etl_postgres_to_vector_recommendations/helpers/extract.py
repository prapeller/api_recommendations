import logging
from datetime import datetime
from typing import Any, Dict, Generator, List, Set

import psycopg2
from backoff import expo, on_exception

from .stateman import StateManager


class PostgresExtractor:
    def __init__(self, dns: Dict[str, str], state_man: StateManager):
        self.dns = dns
        self.state_manager = state_man
        self.connection = None
        self.last_modified = self.state_manager.load_state()

    def __enter__(self):
        self.connect()
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()

    @on_exception(expo, psycopg2.OperationalError, max_tries=10)
    def connect(self):
        self.connection = psycopg2.connect(**self.dns)

    def execute_query(self, query: str, batch_size=100) -> Generator[Dict, Any, Any]:
        """
        Context managed cursor and connection executor
        :param query: SQL query
        :param batch_size:
        :return:
        """
        with self as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                while True:
                    results = cursor.fetchmany(batch_size)
                    if not results:
                        break
                    for row in results:
                        yield row

    def get_films_uuids(self, modified=True) -> Set:
        """
        Get set of films where genre or person was modified
        :return:
        """
        if modified:
            edited_films_query = f"SELECT DISTINCT film.uuid \
            FROM content.film AS film \
            LEFT JOIN content.film_person AS film_person ON film_person.film_uuid = film.uuid \
            LEFT JOIN content.person AS person ON person.uuid = film_person.person_uuid \
            LEFT JOIN content.film_genre AS film_genre ON film_genre.film_uuid = film.uuid \
            LEFT JOIN content.genre AS genre ON genre.uuid = film_genre.genre_uuid \
            WHERE GREATEST(film.updated_at, person.updated_at, genre.updated_at) > '{self.last_modified}' \
            ORDER BY film.uuid"
        else:
            edited_films_query = "select distinct film.uuid \
                            from content.film as film \
                            left join content.film_person as film_person on film_person.film_uuid = film.uuid \
                            left join content.person as person on person.uuid = film_person.person_uuid \
                            left join content.film_genre as film_genre on film_genre.film_uuid = film.uuid \
                            left join content.genre as genre on genre.uuid = film_genre.genre_uuid \
                            order by film.uuid"
        rows = self.execute_query(edited_films_query)
        extracted = set()
        if not rows:
            logging.info('No new modified filmworks found')
            return set()
        for row in rows:
            extracted.add(row[0])
        return extracted

    def get_films_data(self) -> List[Dict]:
        """
        Get all needed for Elasticsearch entries for modified filmworks
        :return:
        """
        self.last_modified = self.state_manager.load_state()
        if self.last_modified == datetime(1970, 1, 1):
            uuids = self.get_films_uuids(modified=False)
        else:
            uuids = self.get_films_uuids(modified=True)
        if not uuids:
            return []
        uuid_strings = [str(id) for id in uuids]
        uuid_strings = [id.replace("'", "''") for id in uuid_strings]
        uuid_string = ",".join([f"'{id}'" for id in uuid_strings])
        sql_query = f"""
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
                    film.uuid IN ({uuid_string})
                GROUP BY film.uuid, film.description, film.type
                ORDER BY film.uuid
            """
        rows = self.execute_query(sql_query)
        extracted = []
        for row in rows:
            extracted.append(row)
        return extracted
