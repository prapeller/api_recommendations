import fastapi as fa

from core.dependencies import vector_repo_dependency, current_user_uuid_dependency
from services.vector.repo import VectorMilvusRepository

router = fa.APIRouter()


@router.get("/recommend")
async def recommendations_search(
        user_uuid=fa.Depends(current_user_uuid_dependency),
        vector_repo: VectorMilvusRepository = fa.Depends(vector_repo_dependency),
):
    return await vector_repo.search_nearest_for_user(user_uuid)
