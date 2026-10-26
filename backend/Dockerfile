# Backend Python : API REST + historique des parties dans SQLite.
FROM tictactoe/base:1.0

# python3 depuis les dépôts Alpine (3.12), inclut les modules sqlite3 et
# http.server : aucune dépendance pip nécessaire.
RUN apk add --no-cache python3

# - PYTHONDONTWRITEBYTECODE : pas de fichiers .pyc (le code est en lecture seule).
# - PYTHONUNBUFFERED        : logs envoyés immédiatement sur stdout (docker logs).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=8081 \
    DB_PATH=/data/games.db \
    HISTORY_LIMIT=20 \
    REQUEST_QUEUE_SIZE=64

WORKDIR /app
COPY api.py game.py ./
COPY entrypoint.sh /usr/local/bin/entrypoint.sh

# - conversion CRLF -> LF (fichiers édités sous Windows) et droit d'exécution ;
# - /data appartient à l'utilisateur "app" : le volume nommé hérite de ces droits.
RUN sed -i 's/\r$//' /usr/local/bin/entrypoint.sh \
 && chmod 0755 /usr/local/bin/entrypoint.sh \
 && mkdir -p /data \
 && chown app:app /data

VOLUME ["/data"]
USER app
EXPOSE 8081

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q -O /dev/null "http://127.0.0.1:${PORT}/api/health" || exit 1

# tini (PID 1) relaie les signaux à entrypoint.sh, qui fait "exec python3".
ENTRYPOINT ["/sbin/tini", "--", "/usr/local/bin/entrypoint.sh"]
