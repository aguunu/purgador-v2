.PHONY: build
build:
	docker build --tag purgador-docker purgador
	docker build --tag lavalink-docker lavalink

.PHONY: up
up:
	docker compose up -d

.PHONY: down
down:
	docker compose down

.PHONY: logs
logs:
	docker compose logs

.PHONY: clean
clean:
	docker system prune --all --force
