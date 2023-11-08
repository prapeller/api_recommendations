from enum import Enum


class EnvEnum(str, Enum):
    local = 'local'
    docker_compose_local = 'docker-compose-local'
    prod = 'prod'

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self)


class ResponseDetailEnum(str, Enum):
    ok = 'ok'
    unauthorized = 'Unauthorized for this action.'
    bad_request = 'Bad reqeust.'

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self)


class OrderEnum(str, Enum):
    asc = 'asc'
    desc = 'desc'

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self)


class ServicesNamesEnum(str, Enum):
    etl_from_postgres_to_vector = 'etl_from_postgres_to_vector'

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self)
