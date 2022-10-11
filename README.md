# discord bot using hikari and lightbulb
To run the bot use the following command in your terminal.
```shell
$ python -m purgador
```

To create the database you must run the following command in your terminal.
```shell
$ sqlite3 database.db < tools/queries.sql
```

Build purgador docker command.
```shell
$ docker build --tag purgador-docker purgador
```

Build lavalink docker command
```shell
$ docker build --tag lavalink-docker lavalink
```

Run docker-compose command.
```shell
$ docker-compose up -d
```