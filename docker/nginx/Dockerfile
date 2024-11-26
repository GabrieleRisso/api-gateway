# docker/nginx/Dockerfile

# Usa l'immagine Alpine di Nginx per una build leggera
FROM nginx:1.25-alpine

# Aggiorniamo i pacchetti e installiamo le utility necessarie
RUN apk update && apk add --no-cache \
    curl \
    vim \
    bash \
    tzdata \
    && rm -rf /var/cache/apk/*

# Impostiamo il timezone
ENV TZ=Europe/Rome
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Creiamo le directory necessarie per i log con permessi corretti
RUN mkdir -p /var/log/nginx && \
    touch /var/log/nginx/access.log && \
    touch /var/log/nginx/error.log && \
    chown -R nginx:nginx /var/log/nginx && \
    chmod -R 755 /var/log/nginx

# Rimuoviamo la configurazione di default
RUN rm /etc/nginx/conf.d/default.conf

# Copiamo la nostra configurazione
COPY nginx.conf /etc/nginx/nginx.conf

# Creiamo una directory per i file statici
RUN mkdir -p /usr/share/nginx/html/static && \
    chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

# Verifica della configurazione di Nginx
RUN nginx -t

# Espone la porta 80
EXPOSE 80

# Comando di avvio con permessi corretti
CMD ["nginx", "-g", "daemon off;"]