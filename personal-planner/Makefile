.PHONY: up down build logs shell-tg shell-agent clean migrate test

# Запуск всех сервисов
up:
	docker-compose up -d

# Остановка всех сервисов
down:
	docker-compose down

# Пересборка и запуск
build:
	docker-compose build

# Просмотр логов
logs:
	docker-compose logs -f

# Лог конкретного сервиса
logs-%:
	docker-compose logs -f $(shell echo $@ | cut -d'-' -f2)

# Shell в tg_gateway
shell-tg:
	docker-compose exec tg_gateway /bin/bash

# Shell в agent_core
shell-agent:
	docker-compose exec agent_core /bin/bash

# Миграции БД
migrate:
	docker-compose exec postgres psql -U postgres -d personal_planner -f /docker-entrypoint-initdb.d/001_initial.sql

# Тесты
test:
	docker-compose exec agent_core pytest /app/tests/unit
	docker-compose exec tg_gateway pytest /app/tests/unit

# E2E тесты
test-e2e:
	docker-compose exec agent_core pytest /app/tests/e2e

# Очистка кэшей и томов
clean:
	docker-compose down -v --remove-orphans
	docker system prune -f

# Помощь
help:
	@echo "Personal Planner - Makefile Commands"
	@echo "====================================="
	@echo "make up          - Запуск всех сервисов"
	@echo "make down        - Остановка сервисов"
	@echo "make build       - Пересборка контейнеров"
	@echo "make logs        - Просмотр логов всех сервисов"
	@echo "make logs-<svc>  - Просмотр логов сервиса (tg, asr, agent, mcp, rag, scheduler)"
	@echo "make shell-tg    - Shell в tg_gateway"
	@echo "make shell-agent - Shell в agent_core"
	@echo "make migrate     - Применение миграций БД"
	@echo "make test        - Запуск unit-тестов"
	@echo "make test-e2e    - Запуск E2E тестов"
	@echo "make clean       - Очистка всех томов и кэшей"
