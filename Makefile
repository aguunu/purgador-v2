purgador_tag := purgador-docker
lavalink_tag := lavalink-docker
	
.PHONY: purgador
purgador: $(purgador_tag)
	docker build --tag $(purgador_tag) ./purgador

.PHONY: lavalink
lavalink: $(lavalink_tag)
	docker build --tag $(lavalink_tag) ./lavalink

.PHONY: build
build: lavalink purgador

.PHONY: up
up:
	docker compose up -d --build

.PHONY: down
down:
	docker compose down

.PHONY: logs
logs:
	docker compose logs

.PHONY: clean
clean:
	docker system prune --all --force
