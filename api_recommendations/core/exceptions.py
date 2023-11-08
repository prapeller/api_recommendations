import fastapi as fa

from core.enums import ResponseDetailEnum


class UnauthorizedException(fa.HTTPException):
    def __init__(self, detail=None):
        super().__init__(
            status_code=fa.status.HTTP_401_UNAUTHORIZED,
            detail=ResponseDetailEnum.unauthorized if detail is None else detail,
        )


class BadRequestException(fa.HTTPException):
    def __init__(self, detail=None):
        super().__init__(
            status_code=fa.status.HTTP_400_BAD_REQUEST,
            detail=ResponseDetailEnum.bad_request if detail is None else detail,
        )
