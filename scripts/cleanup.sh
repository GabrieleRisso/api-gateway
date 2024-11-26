#!/bin/bash

# Colori per output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${RED}Cleaning up Weather Service...${NC}"

# Ferma e rimuove i container
echo "Stopping and removing containers..."
docker-compose down

# Rimuove i volumi
echo "Removing volumes..."
docker-compose down -v

# Rimuove le immagini
echo "Removing images..."
docker rmi $(docker images -q weather_api)
docker rmi $(docker images -q weather_nginx)

# Pulisce la cache di Docker
echo "Cleaning Docker cache..."
docker system prune -f

echo -e "${GREEN}Cleanup completed successfully!${NC}"