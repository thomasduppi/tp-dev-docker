# Serveur web : reverse proxy nginx, seul conteneur exposé sur l'hôte.
# Il route /api/* vers le backend Python et le reste vers le frontend React.
FROM tictactoe/base:1.0

# nginx depuis les dépôts Alpine ; config par défaut supprimée (la nôtre est
# générée au démarrage par entrypoint.sh).
RUN apk add --no-cache nginx \
 && rm -f /etc/nginx/http.d/default.conf

ENV PORT=8080 \
    WORKER_PROCESSES=1 \
    WORKER_CONNECTIONS=512 \
    CLIENT_MAX_BODY_SIZE=16k \
    API_RATE_LIMIT=20 \
    BACKEND_HOST=backend \
    BACKEND_PORT=8081 \
    FRONTEND_HOST=frontend \
    FRONTEND_PORT=8080

COPY nginx.conf /etc/nginx/nginx.conf.template
COPY entrypoint.sh /usr/local/bin/entrypoint.sh

RUN sed -i 's/\r$//' /usr/local/bin/entrypoint.sh \
 && chmod 0755 /usr/local/bin/entrypoint.sh

USER app
EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q -O /dev/null "http://127.0.0.1:${PORT}/healthz" || exit 1

STOPSIGNAL SIGQUIT
ENTRYPOINT ["/sbin/tini", "--", "/usr/local/bin/entrypoint.sh"]
