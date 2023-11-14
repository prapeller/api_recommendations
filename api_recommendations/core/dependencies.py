import json
import uuid

import fastapi as fa
import httpx
from fastapi.security import OAuth2PasswordBearer
from redis.asyncio import Redis

from core.config import settings
from core.enums import ServicesNamesEnum
from core.exceptions import UnauthorizedException
from core.logger_config import logger
from services.cache.cache import RedisCache
from services.recommendations.recommendations import RecommendationsService
from services.vector.repo import VectorMilvusRepository

redis: Redis | None = None
vector_repo: VectorMilvusRepository | None = None


async def redis_dependency() -> Redis:
    return redis


async def redis_cache_dependency(
        redis=fa.Depends(redis_dependency),
) -> RedisCache:
    return RedisCache(redis)


async def vector_repo_dependency() -> VectorMilvusRepository:
    return vector_repo


oauth2_scheme_local = OAuth2PasswordBearer(
    tokenUrl=f"http://{settings.API_AUTH_HOST}:{settings.API_AUTH_PORT}/api/v1/auth/login")


async def verified_access_token_dependency(
        request: fa.Request,
        access_token: str = fa.Depends(oauth2_scheme_local),
) -> dict:
    url = f"http://{settings.API_AUTH_HOST}:{settings.API_AUTH_PORT}/api/v1/auth/verify-access-token"
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }
    data = {
        'useragent': request.headers.get("user-agent"),
        'ip': request.headers.get('X-Forwarded-For'),
        'access_token': access_token,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=headers, json=data)
    if resp.status_code != fa.status.HTTP_200_OK:
        raise UnauthorizedException
    return json.loads(resp.text)


async def current_user_uuid_dependency(
        verified_token: dict = fa.Depends(verified_access_token_dependency),
) -> uuid.UUID:
    return uuid.UUID(verified_token.get('sub'))


async def verify_service_dependency(
        request: fa.Request,
) -> None:
    auth_header = request.headers.get('Authorization')
    service_name = request.headers.get('Service-Name')
    if (not auth_header
            or service_name not in [s.value for s in ServicesNamesEnum]
            or auth_header != settings.SERVICE_TO_SERVICE_SECRET):
        detail = f"can't verify service request: {auth_header=:} {service_name=:}"
        logger.error(detail)
        raise UnauthorizedException(detail)


async def recommendations_service_dependency(
        vector_repo: VectorMilvusRepository = fa.Depends(vector_repo_dependency),
) -> RecommendationsService:
    return RecommendationsService(vector_repo)
