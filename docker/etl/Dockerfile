FROM python:3.9-slim-bullseye

ARG APP_HOME=/app/etl
ARG BUILD_ENV
ENV BUILD_ENV $BUILD_ENV

WORKDIR ${APP_HOME}

RUN apt-get update && apt-get install --no-install-recommends -y libpq-dev build-essential gettext curl netcat postgresql \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*


COPY ./etl/requirements /requirements
RUN pip install --upgrade pip
RUN pip install -r /requirements/${BUILD_ENV}.txt

COPY ./docker/etl/entrypoint /entrypoint
COPY ./docker/etl/start_local /start_local
RUN chmod +x /entrypoint
RUN chmod +x /start_local
#RUN chmod +x /start_prod
#RUN chmod +x /start_tests
#COPY ./docker/start_prod /start_prod
#COPY ./docker/start_tests /start_tests

COPY ./etl ${APP_HOME}
ENTRYPOINT ["/entrypoint"]