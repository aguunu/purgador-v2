# 🖤 Purgador-v2
Purgador-v2 is a discord bot made with love using hikari-lightbulb command handler.  
You can invite the bot to your own server [here](https://discord.com/api/oauth2/authorize?client_id=917111121750671370&permissions=8&scope=bot).  

Contact me `Agus#1882` 💖

## Building & Running the bot using Docker
Build or rebuild `purgador` & `lavalink` services.
```shell
$ make build
```

Create and starts (in the background) `purgador` & `lavalink` containers.
```shell
$ make up
```

Stop and remove `purgador` & `lavalink` containers and network. 
```shell
$ make down
```

Remove unused data and all unused images.
```shell
$ make clean
```
