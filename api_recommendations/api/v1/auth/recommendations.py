import json

import fastapi as fa
import httpx

from core.config import settings
from core.dependencies import vector_repo_dependency, current_user_uuid_dependency
from services.vector.repo import VectorMilvusRepository

router = fa.APIRouter()


@router.get("/recommend")
async def recommendations_search(
        user_uuid=fa.Depends(current_user_uuid_dependency),
        vector_repo: VectorMilvusRepository = fa.Depends(vector_repo_dependency),
):
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            url=f'http://{settings.API_UGC_HOST}:{settings.API_UGC_PORT}/api/v1/film-bookmarks/{user_uuid}')
        if resp.status_code == fa.status.HTTP_200_OK:
            resp_dict = json.loads(resp.text)
            film_uuids = [film_bookmark.get('film_uuid') for film_bookmark in resp_dict.get('film_bookmarks', [])]
            if film_uuids:
                return await vector_repo.search_nearest([str(film_uuid) for film_uuid in film_uuids])
        return []
