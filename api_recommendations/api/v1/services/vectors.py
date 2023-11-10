import fastapi as fa
import pydantic as pd
from core.dependencies import vector_repo_dependency
from core.enums import ResponseDetailEnum
from services.vector.repo import VectorMilvusRepository

router = fa.APIRouter()


@router.get("/{film_uuid}", response_model=list[float])
async def vectors_read(
        film_uuid: pd.UUID4,
        vector_repo: VectorMilvusRepository = fa.Depends(vector_repo_dependency),
):
    return await vector_repo.get(str(film_uuid))


@router.post("/")
async def vectors_create(
        film_vectors_data: dict[str, list[float]] = fa.Body(...),
        vector_repo: VectorMilvusRepository = fa.Depends(vector_repo_dependency),
):
    await vector_repo.set(film_vectors_data)
    return {'detail': ResponseDetailEnum.ok}
