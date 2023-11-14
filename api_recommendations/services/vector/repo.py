import json
from abc import ABC, abstractmethod

import fastapi as fa
import httpx
import numpy as np
from backoff import on_exception, constant
from pymilvus import Collection, CollectionSchema, FieldSchema, DataType, connections
from pymilvus import MilvusException

from core.config import settings
from services.cache.cache import RedisCache
from services.vector.logger_config import logger


class AbstractVectorRepository(ABC):

    @abstractmethod
    def set(self, *args, **kwargs):
        pass

    @abstractmethod
    def get(self, *args, **kwargs):
        pass


def milvus_exception_handler(details):
    e = details['exception']
    message = f"milvus exception: {e}".replace('\n', ' ')
    tries = details['tries']
    wait = details['wait']
    logger.error(f'{tries=:}, wait:{wait:0.1f}, {message=:}')


class VectorMilvusRepository(AbstractVectorRepository):
    def __init__(self, cache: RedisCache, dimension=300, collection_name='film_vectors_varchar'):
        self.dimension = dimension
        self.collection = None
        self.collection_name = collection_name
        self._connect_to_milvus()
        self._get_or_create_collection()
        self._create_index()
        self.cache = cache

    @on_exception(constant, MilvusException, max_tries=120, on_backoff=milvus_exception_handler)
    def _connect_to_milvus(self):
        connections.connect(alias="default", host=settings.VECTOR_HOST, port=settings.VECTOR_PORT)

    @on_exception(constant, MilvusException, max_tries=120, on_backoff=milvus_exception_handler)
    def _create_index(self):
        collection_exists_without_index = self.collection is not None and not self.collection.has_index()
        index_params = {
            'metric_type': 'L2',
            'index_type': 'IVF_FLAT',
            'params': {'nlist': 1}
        }

        if collection_exists_without_index:
            self.collection.create_index(field_name='vector', index_params=index_params)

        elif collection_exists_without_index and self.collection.index() != index_params:
            self.collection.drop_index()
            self.collection.create_index(field_name='vector', index_params=index_params)

    def _create_collection_with_schema(self):
        fields = [
            FieldSchema(name="film_uuid", dtype=DataType.VARCHAR, is_primary=True, max_length=36, auto_id=False),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=self.dimension)
        ]
        schema = CollectionSchema(fields)
        return Collection(name=self.collection_name, schema=schema)

    @on_exception(constant, MilvusException, max_tries=120, on_backoff=milvus_exception_handler)
    def _get_or_create_collection(self):
        if connections.get_connection().has_collection(self.collection_name):
            self.collection = self._create_collection_with_schema()
        else:
            self.collection = Collection(name=self.collection_name)

    async def set(self, film_vectors_data: dict[str, list[float]]) -> None:
        """set vectors to Milvus collection"""
        try:
            for film_uuid, vector in film_vectors_data.items():
                film_id = [film_uuid]
                vector_data = [vector]
                self.collection.insert([film_id, vector_data])
                logger.debug(f'inserted by {film_id}: {str(vector)[:10]}...')
                await self.cache.set(film_uuid, vector_data)
            self.collection.flush()
        except MilvusException as e:
            raise fa.HTTPException(fa.status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def get(self, film_uuid: str) -> list[float] | None:
        vector = await self.cache.get(film_uuid)
        if vector is None:
            # Retrieve vector from Milvus collection by primary key
            try:
                self.collection.load()
                results = self.collection.query(expr=f"film_uuid in ['{film_uuid}']", output_fields=["vector"])
                vector = results[0]["vector"] if results[0]["vector"] else None
            except MilvusException as e:
                raise fa.HTTPException(fa.status.HTTP_400_BAD_REQUEST, detail=str(e))
        return vector

    async def search_nearest(self, film_uuids: list[str], k=10) -> list:
        nearest_uuids = await self.cache.get(str(film_uuids))
        if nearest_uuids is None:
            try:
                vectors = [await self.get(film_uuid) for film_uuid in film_uuids]
                average_vector = np.mean(vectors, axis=0)

                # Exclude provided film_uuids in the search
                exclude_expression = " && ".join([f"film_uuid != '{_uuid}'" for _uuid in film_uuids])
                search_params = {
                    "data": [average_vector],
                    "anns_field": "vector",
                    "param": {"metric_type": "L2", "params": {"nprobe": 10}},
                    "limit": k,
                    "expression": exclude_expression
                }
                nearest_uuids = []
                results = self.collection.search(**search_params)
            except MilvusException as e:
                raise fa.HTTPException(fa.status.HTTP_400_BAD_REQUEST, detail=str(e))
            if results:
                nearest_uuids = [str(result.entity.id) for result in results[0]]
                await self.cache.set(str(film_uuids), nearest_uuids)
        return nearest_uuids

    async def search_nearest_film_uuids_for_user(self, user_uuid: str) -> list[str]:
        logger.debug(f'search_nearest_for_user: {user_uuid=:}')
        user_bookmarks_url = f'http://{settings.API_UGC_HOST}:{settings.API_UGC_PORT}/api/v1/film-bookmarks/{user_uuid}'
        nearest_film_uuids = []
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(url=user_bookmarks_url)
            if resp.status_code == fa.status.HTTP_200_OK:
                nearest_films_uuids_dict = json.loads(resp.text)
                film_uuids = [fb.get('film_uuid') for fb in nearest_films_uuids_dict.get('film_bookmarks', [])]
                if film_uuids:
                    nearest_film_uuids = await self.search_nearest([str(film_uuid) for film_uuid in film_uuids])
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            raise fa.HTTPException(fa.status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        return nearest_film_uuids
