import fastapi as fa
import pydantic as pd

from core.dependencies import recommendations_service_dependency, current_user_uuid_dependency
from services.recommendations.recommendations import RecommendationsService

router = fa.APIRouter()


@router.get("/recommend")
async def recommendations_search(
        limit: int = fa.Query(default=10),
        current_user_uuid: pd.UUID4 = fa.Depends(current_user_uuid_dependency),
        rec_service: RecommendationsService = fa.Depends(recommendations_service_dependency),
):
    return await rec_service.recommend_films_for_user(user_uuid=str(current_user_uuid), limit=limit)
