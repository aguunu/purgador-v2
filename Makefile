build:
	docker build --tag purgador-docker purgador
	docker build --tag lavalink-docker lavalink
up:
	docker-compose up -d
down:
	docker-compose down
logs:
	docker compose logs
