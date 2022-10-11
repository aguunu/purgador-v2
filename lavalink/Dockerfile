FROM openjdk:11-jre-slim

WORKDIR /lavalink

COPY application.yml application.yml

RUN apt-get update
RUN apt install wget -y
RUN wget https://github.com/freyacodes/Lavalink/releases/latest/download/Lavalink.jar

CMD ["java", "-jar", "Lavalink.jar"]
