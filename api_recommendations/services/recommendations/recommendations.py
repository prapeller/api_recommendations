import json

import fastapi as fa
import httpx

from core.config import settings
from services.vector.repo import VectorMilvusRepository


class RecommendationsService:
    def __init__(self, vector_repo: VectorMilvusRepository):
        self.vector_repo = vector_repo

    async def recommend_films_for_user(self, user_uuid: str, limit: int) -> list[str]:
        films_uuids = await self.vector_repo.search_nearest_film_uuids_for_user(user_uuid=user_uuid, limit=limit)
        if not films_uuids:
            top_films_url = (f'http://{settings.API_SEARCH_HOST}:{settings.API_SEARCH_PORT}/api/v1/services-films/')
            headers = {'Authorization': settings.SERVICE_TO_SERVICE_SECRET,
                       'Service-Name': 'api_recommendations'}
            async with httpx.AsyncClient() as client:
                resp = await client.get(url=top_films_url, headers=headers)
            if resp.status_code == fa.status.HTTP_200_OK:
                resp_dict = json.loads(resp.text)
                films_uuids = [f.get('uuid') for f in resp_dict.get('objs', [])]
        return films_uuids
