import fastapi as fa

from core.dependencies import recommendations_service_dependency
from services.recommendations.recommendations import RecommendationsService

router = fa.APIRouter()


@router.get("/recommend")
async def recommendations_search(
        rec_service: RecommendationsService = fa.Depends(recommendations_service_dependency),
):
    return await rec_service.recommend_films()
