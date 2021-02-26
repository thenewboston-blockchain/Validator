pv_env_vars=. local/local.sh && export $$(grep -v '^\#' .env-pv | xargs)
cv1_env_vars=. local/local.sh && export $$(grep -v '^\#' .env-cv1 | xargs)
cv2_env_vars=. local/local.sh && export $$(grep -v '^\#' .env-cv2 | xargs)

.PHONY: build
build:
	docker build .

.PHONY: install
install:
	poetry install

.PHONY: test
test:
	poetry run pytest -v -n auto

.PHONY: test-dockerized
test-dockerized:
	docker-compose run pv pytest -v -n auto

.PHONY: lint
lint:
	# TODO(dmu) MEDIUM: Consider namespacing everything under single package
	poetry run flake8 thenewboston_validator tests config

.PHONY: migrate
migrate:
	${pv_env_vars} && poetry run python manage.py migrate
	${cv1_env_vars} && poetry run python manage.py migrate
	${cv2_env_vars} && poetry run python manage.py migrate

.PHONY: initialize
initialize:
	${pv_env_vars} && poetry run python manage.py initialize_test_primary_validator -ip $${PUBLIC_IP_ADDRESS}
	${cv1_env_vars} && poetry run python manage.py initialize_test_confirmation_validator -ip $${PUBLIC_IP_ADDRESS}
	${cv2_env_vars} && poetry run python manage.py initialize_test_confirmation_validator -ip $${PUBLIC_IP_ADDRESS}

# TODO(dmu) MEDIUM: Can run-* and run-*-celery be implemented in a DRY way?
.PHONY: run-pv
run-pv:
	${pv_env_vars} && poetry run python manage.py runserver 0.0.0.0:8001

.PHONY: run-cv1
run-cv1:
	${cv1_env_vars} && poetry run python manage.py runserver 0.0.0.0:8002

.PHONY: run-cv2
run-cv2:
	${cv2_env_vars} && poetry run python manage.py runserver 0.0.0.0:8003

.PHONY: run-pv-celery
run-pv-celery:
	${pv_env_vars} && poetry run celery -A config.settings worker -l debug -Q celery,block_queue,confirmation_block_queue

.PHONY: run-cv1-celery
run-cv1-celery:
	${cv1_env_vars} && poetry run celery -A config.settings worker -l debug -Q celery,block_queue,confirmation_block_queue

.PHONY: run-cv2-celery
run-cv2-celery:
	${cv2_env_vars} && poetry run celery -A config.settings worker -l debug -Q celery,block_queue,confirmation_block_queue

.PHONY: up
up:
	docker-compose up --force-recreate --build

.PHONY: up-dependencies-only
up-dependencies-only:
	docker-compose up --force-recreate db redis bank

.PHONY: monitor-pv
monitor-pv:
	docker-compose exec celery_pv celery flower -A config.settings --port=5556

.PHONY: monitor-cv1
monitor-cv1:
	docker-compose exec celery_cv1 celery flower -A config.settings --port=5557

.PHONY: monitor-cv2
monitor-cv2:
	docker-compose exec celery_cv2 celery flower -A config.settings --port=5558

.PHONY: monitor-bank
monitor-bank:
	docker-compose exec celery_bank celery flower -A config.settings --port=5559

.PHONY: monitor-pv-local
monitor-pv-local:
	${pv_env_vars} && poetry run celery flower -A config.settings --address=127.0.0.1 --port=5556

.PHONY: monitor-cv1-local
monitor-cv1-local:
	${cv1_env_vars} && poetry run celery flower -A config.settings --address=127.0.0.1 --port=5557

.PHONY: monitor-cv2-local
monitor-cv2-local:
	${cv2_env_vars} && poetry run celery flower -A config.settings --address=127.0.0.1 --port=5558
