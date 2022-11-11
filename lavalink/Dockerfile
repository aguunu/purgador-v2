FROM openjdk:11-jre-slim

WORKDIR /lavalink

COPY application.yml application.yml

RUN apt update -y && apt upgrade -y
RUN apt install wget -y
RUN wget https://github.com/freyacodes/Lavalink/releases/latest/download/Lavalink.jar

EXPOSE ${LAVALINK_PORT}

ENTRYPOINT ["java", "-Xmx512M", "-jar", "Lavalink.jar"]
