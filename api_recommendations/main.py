from contextlib import asynccontextmanager

import fastapi as fa
import uvicorn
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from api.v1.auth import recommendations as v1_recommendations_auth
from api.v1.services import vectors as v1_vectors_services
from core import dependencies
from core.config import settings
from core.dependencies import verified_access_token_dependency, verify_service_dependency
from services.cache.cache import RedisCache
from services.vector.repo import VectorMilvusRepository


@asynccontextmanager
async def lifespan(app: fa.FastAPI):
    # startup
    redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
    dependencies.redis = redis
    redis_cache = RedisCache(redis=redis)
    dependencies.vector_repo = VectorMilvusRepository(cache=redis_cache)
    yield
    # shutdown


app = fa.FastAPI(
    title=settings.PROJECT_NAME,
    docs_url=f'/{settings.DOCS_URL}',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

v1_router_auth = fa.APIRouter(
    dependencies=[fa.Depends(verified_access_token_dependency)],
)
v1_router_auth.include_router(v1_recommendations_auth.router, prefix='/recommendations', tags=['recommendations'])

v1_router_services = fa.APIRouter(dependencies=[fa.Depends(verify_service_dependency)])
v1_router_services.include_router(v1_vectors_services.router, prefix='/services-vectors',
                                  tags=['services-vectors'])

app.include_router(v1_router_auth, prefix="/api/v1")
app.include_router(v1_router_services, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run('main:app', host=settings.API_RECOMMENDATIONS_HOST, port=settings.API_RECOMMENDATIONS_PORT, reload=True)
