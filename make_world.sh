#!/bin/bash
mkdir -p testworld1
cd testworld1
if [ ! -e minecraft_server.jar ]; then
    wget -O minecraft_server.jar "https://s3.amazonaws.com/MinecraftDownload/launcher/minecraft_server.jar"
fi
if [ -d world ]; then
    while true; do
        echo "A world already exists. Do you want to delete and regenerate, exit, or move the existing world?"
        read -p "delete/exit/rename [dy/eq/rm] " yn
        case $yn in
            [DdYy]* ) rm -r world; break;;
            [RrMm]* ) read -p "New name: " name;
                      mv world/ $name/; break;;
            [EeQq]* ) exit;
        esac
    done
fi
# Start the server, have it generate chunks, and exit
echo "stop" | java -jar minecraft_server.jar

