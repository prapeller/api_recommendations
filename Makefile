API_RECOMMENDATIONS_LOCAL := -p api_recommendations -f ./docker/api/docker-compose-local.yml
ETL_RECOMMENDATIONS_LOCAL := -p etl_recommendations -f ./docker/etl/docker-compose-local.yml
VECTOR_RECOMMENDATIONS_LOCAL := -p vector_recommendations -f ./docker/vector/docker-compose-local.yml

API_RECOMMENDATIONS_PROD := -p api_recommendations -f ./docker/api/docker-compose-prod.yml
ETL_RECOMMENDATIONS_PROD := -p etl_recommendations -f ./docker/etl/docker-compose-prod.yml
VECTOR_RECOMMENDATIONS_PROD := -p vector_recommendations -f ./docker/vector/docker-compose-prod.yml

build-loc:
	@docker network create shared_network || true
	docker-compose $(API_RECOMMENDATIONS_LOCAL) up --build -d --remove-orphans
	docker-compose $(ETL_RECOMMENDATIONS_LOCAL) up --build -d --remove-orphans
	docker-compose $(VECTOR_RECOMMENDATIONS_LOCAL) up --build -d --remove-orphans

build:
	@docker network create shared_network || true
	docker-compose $(API_RECOMMENDATIONS_PROD) up --build -d --remove-orphans
	docker-compose $(ETL_RECOMMENDATIONS_PROD) up --build -d --remove-orphans
	docker-compose $(VECTOR_RECOMMENDATIONS_PROD) up --build -d --remove-orphans

down-loc:
	docker-compose $(API_RECOMMENDATIONS_LOCAL) down
	docker-compose $(ETL_RECOMMENDATIONS_LOCAL) down
	docker-compose $(VECTOR_RECOMMENDATIONS_LOCAL) down

down:
	docker-compose $(API_RECOMMENDATIONS_PROD) down
	docker-compose $(ETL_RECOMMENDATIONS_PROD) down
	docker-compose $(VECTOR_RECOMMENDATIONS_PROD) down

down-v-loc:
	docker-compose $(API_RECOMMENDATIONS_LOCAL) down -v
	docker-compose $(ETL_RECOMMENDATIONS_LOCAL) down -v
	docker-compose $(VECTOR_RECOMMENDATIONS_LOCAL) down -v

down-v:
	docker-compose $(API_RECOMMENDATIONS_PROD) down -v
	docker-compose $(ETL_RECOMMENDATIONS_PROD) down -v
	docker-compose $(VECTOR_RECOMMENDATIONS_PROD) down -v


api-build-loc:
	docker-compose $(API_RECOMMENDATIONS_LOCAL) up --build -d  --remove-orphans --no-deps api_recommendations

api-build:
	docker-compose $(API_RECOMMENDATIONS_PROD) up --build -d  --remove-orphans --no-deps api_recommendations

api-pipinstall-loc:
	docker-compose $(API_RECOMMENDATIONS_LOCAL)  run --rm api_recommendations pip install -r requirements/local.txt

api-pipinstall:
	docker-compose $(API_RECOMMENDATIONS_PROD)  run --rm api_recommendations pip install -r requirements/prod.txt

api-check-ip:
	docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' api_recommendations

api-redis-build-loc:
	docker-compose $(API_RECOMMENDATIONS_LOCAL) up --build -d --remove-orphans --no-deps redis_recommendations

api-nginx-build-loc:
	docker-compose $(API_RECOMMENDATIONS_LOCAL) up --build -d --remove-orphans --no-deps nginx_recommendations

api-tests-build-loc:
	docker-compose $(API_RECOMMENDATIONS_LOCAL) up --build -d --remove-orphans --no-deps tests_recommendations



etl-build:
	docker-compose $(VECTOR_RECOMMENDATIONS_PROD) up --build -d  --remove-orphans --no-deps
	docker-compose $(ETL_RECOMMENDATIONS_PROD) up --build -d  --remove-orphans --no-deps

etl-build-loc:
	docker-compose $(VECTOR_RECOMMENDATIONS_LOCAL) up --build -d  --remove-orphans --no-deps
	docker-compose $(ETL_RECOMMENDATIONS_LOCAL) up --build -d  --remove-orphans --no-deps

etl-down-loc:
	docker-compose $(ETL_RECOMMENDATIONS_LOCAL) down
	docker-compose $(VECTOR_RECOMMENDATIONS_LOCAL) down

etl-down:
	docker-compose $(ETL_RECOMMENDATIONS_PROD) down
	docker-compose $(VECTOR_RECOMMENDATIONS_PROD) down

etl-down-v-loc:
	docker-compose $(ETL_RECOMMENDATIONS_LOCAL) down -v
	docker-compose $(VECTOR_RECOMMENDATIONS_LOCAL) down -v

etl-down-v:
	docker-compose $(ETL_RECOMMENDATIONS_PROD) down -v
	docker-compose $(VECTOR_RECOMMENDATIONS_PROD) down -v

etl-dump-loc:
	docker-compose $(ETL_RECOMMENDATIONS_LOCAL) exec etl_recommendations dump.sh
	docker-compose $(VECTOR_RECOMMENDATIONS_LOCAL) exec etl_recommendations dump.sh

etl-dump:
	docker-compose $(ETL_RECOMMENDATIONS_PROD) exec etl_recommendations dump.sh
	docker-compose $(VECTOR_RECOMMENDATIONS_PROD) exec etl_recommendations dump.sh



check-config:
	docker-compose $(API_RECOMMENDATIONS_PROD) config
	docker-compose $(ETL_RECOMMENDATIONS_PROD) config
	docker-compose $(VECTOR_RECOMMENDATIONS_PROD) config

check-config-loc:
	docker-compose $(API_RECOMMENDATIONS_LOCAL) config
	docker-compose $(ETL_RECOMMENDATIONS_LOCAL) config
	docker-compose $(VECTOR_RECOMMENDATIONS_LOCAL) config



check-logs:
	docker-compose $(API_RECOMMENDATIONS_PROD) logs
	docker-compose $(ETL_RECOMMENDATIONS_PROD) logs
	docker-compose $(VECTOR_RECOMMENDATIONS_PROD) logs

check-logs-loc:
	docker-compose $(API_RECOMMENDATIONS_LOCAL) logs
	docker-compose $(ETL_RECOMMENDATIONS_LOCAL) logs
	docker-compose $(VECTOR_RECOMMENDATIONS_LOCAL) logs



flake8:
	docker-compose $(API_RECOMMENDATIONS_LOCAL) exec api_recommendations flake8 .

black-check:
	docker-compose $(API_RECOMMENDATIONS_LOCAL) exec api_recommendations black --check --exclude=venv .

black-diff:
	docker-compose $(API_RECOMMENDATIONS_LOCAL) exec api_recommendations black --diff --exclude=venv .

black:
	docker-compose $(API_RECOMMENDATIONS_LOCAL) exec api_recommendations black --exclude=venv .

isort-check:
	docker-compose $(API_RECOMMENDATIONS_LOCAL) exec api_recommendations isort . --check-only --skip venv

isort-diff:
	docker-compose $(API_RECOMMENDATIONS_LOCAL) exec api_recommendations isort . --diff --skip venv

isort:
	docker-compose $(API_RECOMMENDATIONS_LOCAL) exec api_recommendations isort . --skip venv
