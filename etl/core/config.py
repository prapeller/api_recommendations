import os
from pathlib import Path

import pydantic_settings as ps


class Settings(ps.BaseSettings):
    API_RECOMMENDATIONS_HOST: str
    API_RECOMMENDATIONS_PORT: int

    SEARCH_POSTGRES_HOST: str
    SEARCH_POSTGRES_PORT: int
    SEARCH_POSTGRES_USER: str
    SEARCH_POSTGRES_DB: str
    SEARCH_POSTGRES_PASSWORD: str

    SERVICE_TO_SERVICE_SECRET: str

    class Config:
        extra = 'allow'

    def __init__(self, DOCKER, DEBUG, BASE_DIR):
        if DEBUG and DOCKER:
            super().__init__(_env_file=[BASE_DIR / '../.envs/.docker-compose-local/.postgres',
                                        BASE_DIR / '../.envs/.docker-compose-local/.vector',
                                        BASE_DIR / '../.envs/.docker-compose-local/.etl'
                                        ])
        elif DEBUG and not DOCKER:
            super().__init__(_env_file=[BASE_DIR / '../.envs/.local/.postgres',
                                        BASE_DIR / '../.envs/.local/.vector',
                                        BASE_DIR / '../.envs/.local/.etl',
                                        ])
        else:
            super().__init__(_env_file=[BASE_DIR / '../.envs/.prod/.postgres',
                                        BASE_DIR / '../.envs/.prod/.vector',
                                        BASE_DIR / '../.envs/.prod/.etl',
                                        ])


DEBUG = os.getenv('DEBUG', False) == 'True'
DOCKER = os.getenv('DOCKER', False) == 'True'
BASE_DIR = Path(__file__).resolve().parent.parent

settings = Settings(DOCKER, DEBUG, BASE_DIR)

REDIS_CACHE_EXPIRES_IN_SECONDS = 30
ETL_STATE_FILENAME = 'state'
ETL_LOOP_SLEEP_SECONDS = 5
