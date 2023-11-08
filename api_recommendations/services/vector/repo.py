from abc import ABC, abstractmethod

import numpy as np
from core.config import settings
from pymilvus import Collection, CollectionSchema, FieldSchema, DataType, connections
from services.cache.cache import RedisCache
from services.vector.logger_config import logger


class AbstractRepository(ABC):

    @abstractmethod
    def set(self, *args, **kwargs):
        pass

    @abstractmethod
    def get(self, *args, **kwargs):
        pass


class VectorMilvusRepository(AbstractRepository):
    def __init__(self, cache: RedisCache, dimension=300, collection_name='film_vectors_varchar'):
        self.dimension = dimension
        self.collection_name = collection_name
        self._connect_to_milvus()
        self._create_collection()
        self._create_index()
        self.cache = cache

    def _connect_to_milvus(self):
        connections.connect(alias="default", host=settings.VECTOR_HOST, port=settings.VECTOR_PORT)

    def _create_index(self):
        index_params = {
            'metric_type': 'L2',
            'index_type': 'IVF_FLAT',
            'params': {'nlist': 1}
        }
        self.collection.create_index(field_name='vector', index_params=index_params)

    def _create_collection(self):
        # Define fields for the collection schema
        fields = [
            FieldSchema(name="film_uuid", dtype=DataType.VARCHAR, is_primary=True, max_length=36, auto_id=False),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=self.dimension)
        ]
        schema = CollectionSchema(fields)

        # Create the collection in Milvus
        collection = Collection(name=self.collection_name, schema=schema)
        self.collection = collection

    async def set(self, film_vectors_data: dict[str, list[float]]) -> None:
        """set vector to Milvus collection"""
        for film_uuid, vector in film_vectors_data.items():
            film_id = [film_uuid]
            vector_data = [vector]
            self.collection.insert([film_id, vector_data])
            logger.debug(f'inserted by {film_id}: {str(vector)[:10]}...')
            await self.cache.set(film_uuid, vector_data)
        self.collection.flush()

    async def get(self, film_uuid: str) -> list[float] | None:
        vector = await self.cache.get(film_uuid)
        if vector is None:
            # Retrieve vector from Milvus collection by primary key
            self.collection.load()
            results = self.collection.query(expr=f"film_uuid in ['{film_uuid}']", output_fields=["vector"])
            vector = results[0]["vector"] if results[0]["vector"] else None
        return vector

    async def search_nearest(self, liked_film_uuids: list[str], k=10):
        print(self.collection.index().params)
        nearest_uuids = await self.cache.get(str(liked_film_uuids))
        if nearest_uuids is None:
            vectors = [await self.get(film_uuid) for film_uuid in liked_film_uuids]
            average_vector = np.mean(vectors, axis=0)
            search_params = {
                "data": [average_vector],
                "anns_field": "vector",
                "param": {"metric_type": "L2", "params": {"nprobe": 10}},
                "limit": k,
            }
            results = self.collection.search(**search_params)
            nearest_uuids = [str(result.entity.id) for result in results[0]]
            await self.cache.set(str(liked_film_uuids), nearest_uuids)
        return nearest_uuids
