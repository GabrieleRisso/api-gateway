#!/bin/bash

# Colori per output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Starting Weather Service...${NC}"

# Verifica presenza file .env
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo "Creating example .env file..."
    cp .env.example .env
    echo "Please configure your .env file and restart"
    exit 1
fi

# Ferma eventuali container in esecuzione
echo "Stopping any running containers..."
docker-compose down

# Costruisce le immagini
echo "Building Docker images..."
docker-compose build --no-cache

# Avvia i servizi
echo "Starting services..."
docker-compose up -d

# Verifica lo stato dei servizi
echo "Checking service status..."
docker-compose ps

echo -e "${GREEN}Services started successfully!${NC}"
echo "Access the API at: http://localhost/api/"
echo "Access the documentation at: http://localhost/api/docs"