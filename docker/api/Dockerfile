ARG PYTHON_VERSION=3.11-slim-bullseye
FROM python:${PYTHON_VERSION} as my_python

FROM my_python as python-build-stage
ARG BUILD_ENV
ENV BUILD_ENV $BUILD_ENV

RUN apt-get update && apt-get install --no-install-recommends -y libpq-dev build-essential
COPY ./api_recommendations/requirements .
RUN pip wheel --wheel-dir /usr/src/app/wheels -r ${BUILD_ENV}.txt

FROM my_python as python-run-stage

ARG APP_HOME=/app/api_recommendations
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR ${APP_HOME}
RUN apt-get update && apt-get install --no-install-recommends -y libpq-dev gettext curl netcat \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

COPY --from=python-build-stage /usr/src/app/wheels /wheels/
RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
    && rm -rf /wheels/

COPY ./docker/api/entrypoint /entrypoint
COPY ./docker/api/start_prod /start_prod
COPY ./docker/api/start_local /start_local
COPY ./docker/api/start_tests /start_tests
RUN chmod +x /entrypoint
RUN chmod +x /start_prod
RUN chmod +x /start_local
RUN chmod +x /start_tests

COPY ./api_recommendations/ ${APP_HOME}
ENTRYPOINT ["/entrypoint"]