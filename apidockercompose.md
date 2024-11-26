# Weather Service: Implementazione Completa con Docker

## Struttura del Progetto Aggiornata con Docker-Compose
```
weather_service/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── weather_service.py
│   │   ├── time_service.py
│   │   └── openai_service.py
│   ├── models/
│   │   └── schemas.py
│   └── utils/
│       └── error_handlers.py
├── docker/
│   ├── nginx/
│   │   ├── Dockerfile
│   │   └── nginx.conf
│   └── api/
│       └── Dockerfile
├── scripts/
│   ├── start.sh
│   └── cleanup.sh
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 1. Integrazione Docker nella Struttura Esistente

### 1.1 Spostamento e Aggiornamento del Dockerfile API
```dockerfile
# docker/api/Dockerfile

# Usa un'immagine Python ufficiale
FROM python:3.9-slim

# Imposta le variabili d'ambiente per Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.4.2

# Crea e imposta la directory di lavoro
WORKDIR /app

# Copia i file dei requisiti
COPY requirements.txt .

# Installa le dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice dell'applicazione
COPY ./app .

# Crea un utente non-root per la sicurezza
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app

# Passa all'utente non-root
USER appuser

# Espone la porta
EXPOSE 8000

# Comando di avvio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 1.2 Configurazione Nginx (docker/nginx/nginx.conf)
```nginx
# Configurazione base di Nginx
worker_processes 1;

events {
    worker_connections 1024;
}

http {
    # Configurazioni di base
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Include i tipi MIME
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Configurazione dei log
    log_format detailed '$remote_addr - $remote_user [$time_local] '
                       '"$request" $status $body_bytes_sent '
                       '"$http_referer" "$http_user_agent" '
                       '$request_time';

    access_log /var/log/nginx/access.log detailed;
    error_log /var/log/nginx/error.log warn;

    # Rate limiting zones
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

    # Configurazione del server
    server {
        listen 80;
        server_name localhost;

        # Configurazione della root directory
        root /usr/share/nginx/html;

        # Configurazione del proxy per l'API
        location /api/ {
            # Rate limiting
            limit_req zone=api_limit burst=20 nodelay;

            # Rimuove /api dal path
            rewrite ^/api/(.*) /$1 break;

            # Proxy all'API
            proxy_pass http://172.20.0.2:8000;

            # Headers per il proxy
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Timeout settings
            proxy_connect_timeout 300s;
            proxy_send_timeout 300s;
            proxy_read_timeout 300s;

            # CORS headers
            add_header 'Access-Control-Allow-Origin' '*' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
            add_header 'Access-Control-Expose-Headers' 'Content-Length,Content-Range' always;
        }

        # Health check endpoint
        location /health {
            access_log off;
            add_header Content-Type application/json;
            return 200 '{"status":"healthy"}';
        }

        # Gestione degli errori
        error_page 500 502 503 504 /50x.html;
        location = /50x.html {
            root /usr/share/nginx/html;
        }
    }
}
```

### 1.3 Docker Compose 
```yaml
# docker-compose.yml

version: '3.8'

services:
  # Servizio API FastAPI
  api:
    build: 
      context: .
      dockerfile: docker/api/Dockerfile
    container_name: weather_api
    restart: unless-stopped
    environment:
      - ENVIRONMENT=production
      - PYTHONUNBUFFERED=1
    env_file:
      - .env
    volumes:
      - ./app:/app
      - api_cache:/app/.cache
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      app_net:
        ipv4_address: 172.20.0.2

  # Servizio Nginx
  nginx:
    build:
      context: ./docker/nginx
      dockerfile: Dockerfile
    container_name: weather_nginx
    restart: unless-stopped
    ports:
      - "80:80"
    depends_on:
      api:
        condition: service_healthy
    volumes:
      - nginx_logs:/var/log/nginx
    networks:
      app_net:
        ipv4_address: 172.20.0.3

volumes:
  api_cache:
    driver: local
  nginx_logs:
    driver: local

networks:
  app_net:
    driver: bridge
    ipam:
      driver: default
      config:
        - subnet: 172.20.0.0/16
          gateway: 172.20.0.1
```

## 2. Script di Utilità

### 2.1 Script di Avvio (scripts/start.sh)
```bash
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
docker-compose build

# Avvia i servizi
echo "Starting services..."
docker-compose up -d

# Verifica lo stato dei servizi
echo "Checking service status..."
docker-compose ps

echo -e "${GREEN}Services started successfully!${NC}"
echo "Access the API at: http://localhost/api/"
echo "Access the documentation at: http://localhost/api/docs"
```

### 2.2 Script di Pulizia (scripts/cleanup.sh)
```bash
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
```

## 3. Guida all'Utilizzo e Best Practices

### 3.1 Setup Iniziale
1. Clonare il repository:


2. Creare e configurare il file .env:
```bash
cp .env.example .env
nano .env
```

3. Configurare le seguenti variabili nel file .env:
```env
# API Keys
OPENAI_API_KEY=la-tua-chave-openai

# Environment
ENVIRONMENT=production
DEBUG=0

# API Configuration
API_TIMEOUT=30
CACHE_TIMEOUT=3600

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

### 3.2 Avvio del Servizio
1. Rendere eseguibili gli script:
```bash
chmod +x scripts/start.sh scripts/cleanup.sh
```

2. Avviare il servizio:
```bash
./scripts/start.sh
```

### 3.3 Test degli Endpoint
```bash
# Test Weather Endpoint
curl http://localhost/api/weather/cuneo

# Test Time Endpoint
curl http://localhost/api/time

# Test Chat Endpoint
curl -X POST http://localhost/api/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Cosa posso visitare a Cuneo?"}'
```

### 3.4 Monitoraggio
1. Visualizzare i log:
```bash
# Log API
docker-compose logs -f api

# Log Nginx
docker-compose logs -f nginx
```

2. Controllare lo stato dei container:
```bash
docker-compose ps
```

## 4. Sicurezza e Best Practices

### 4.1 Sicurezza della Rete
- Utilizzo di una rete Docker isolata con IP statici
- Rate limiting implementato in Nginx
- Reverse proxy che nasconde l'architettura interna

### 4.2 Sicurezza dei Container
- Utilizzo di utenti non-root nei container
- Minimal base images (python:3.9-slim)
- Volumi Docker per dati persistenti
- Healthchecks per monitoring

### 4.3 Gestione dei Segreti
- Utilizzo di file .env per le variabili sensibili
- Mai committare il file .env nel repository
- Rotazione regolare delle chiavi API

### 4.4 Logging e Monitoring
- Log strutturati in Nginx
- Log separati per API e Nginx
- Healthcheck endpoints per monitoring

