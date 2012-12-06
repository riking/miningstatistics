#!/bin/bash
mkdir -p testworld1
cd testworld1
wget -O minecraft_server.jar "https://s3.amazonaws.com/MinecraftDownload/launcher/minecraft_server.jar"
# Start the server, have it generate chunks, and exit
echo "stop" | java -jar minecraft_server.jar

