.PHONY: init down down-clear up logs build pull restart \
	docker-up docker-down docker-down-clear docker-pull docker-build-pull docker-logs docker-restart

# Как в bots/supplier: полный цикл и базовые docker-цели
init: docker-down docker-pull docker-build-pull docker-up
down: docker-down
down-clear: docker-down-clear

# Короткие алиасы (удобно в README)
up: docker-up
logs: docker-logs
build: docker-build-pull
pull: docker-pull
restart: docker-restart

docker-up:
	docker compose up -d

docker-down:
	docker compose down --remove-orphans

docker-down-clear:
	docker compose down -v --remove-orphans

docker-pull:
	docker compose pull

docker-build-pull:
	docker compose build --pull

docker-logs:
	docker compose logs -f --tail=200

docker-restart:
	docker compose restart
