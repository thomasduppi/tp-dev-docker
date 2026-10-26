#!/bin/sh
# Point d'entrée du reverse proxy : génère la config nginx à partir des
# arguments reçus au run, la valide, puis "exec nginx" (signaux relayés par tini).
set -eu

: "${PORT:=8080}"
: "${WORKER_PROCESSES:=1}"
: "${WORKER_CONNECTIONS:=512}"
: "${CLIENT_MAX_BODY_SIZE:=16k}"
: "${API_RATE_LIMIT:=20}"
: "${BACKEND_HOST:=backend}"
: "${BACKEND_PORT:=8081}"
: "${FRONTEND_HOST:=frontend}"
: "${FRONTEND_PORT:=8080}"

case "$WORKER_PROCESSES" in
    auto) ;;
    ''|*[!0-9]*) echo "Erreur : WORKER_PROCESSES doit valoir 'auto' ou un entier" >&2; exit 1 ;;
esac
require_int() {
    case "$2" in
        ''|*[!0-9]*) echo "Erreur : $1 doit être un entier (reçu '$2')" >&2; exit 1 ;;
    esac
}
require_host() {
    case "$2" in
        ''|*[!a-zA-Z0-9._-]*) echo "Erreur : $1 doit être un nom d'hôte (reçu '$2')" >&2; exit 1 ;;
    esac
}
require_int PORT "$PORT"
require_int WORKER_CONNECTIONS "$WORKER_CONNECTIONS"
require_int API_RATE_LIMIT "$API_RATE_LIMIT"
require_int BACKEND_PORT "$BACKEND_PORT"
require_int FRONTEND_PORT "$FRONTEND_PORT"
require_host BACKEND_HOST "$BACKEND_HOST"
require_host FRONTEND_HOST "$FRONTEND_HOST"
case "$CLIENT_MAX_BODY_SIZE" in
    ''|*[!0-9kKmM]*) echo "Erreur : CLIENT_MAX_BODY_SIZE invalide (ex: 16k, 1m)" >&2; exit 1 ;;
esac

sed -e "s/__PORT__/$PORT/" \
    -e "s/__WORKER_PROCESSES__/$WORKER_PROCESSES/" \
    -e "s/__WORKER_CONNECTIONS__/$WORKER_CONNECTIONS/" \
    -e "s/__CLIENT_MAX_BODY_SIZE__/$CLIENT_MAX_BODY_SIZE/" \
    -e "s/__API_RATE_LIMIT__/$API_RATE_LIMIT/" \
    -e "s/__BACKEND_HOST__/$BACKEND_HOST/" \
    -e "s/__BACKEND_PORT__/$BACKEND_PORT/" \
    -e "s/__FRONTEND_HOST__/$FRONTEND_HOST/" \
    -e "s/__FRONTEND_PORT__/$FRONTEND_PORT/" \
    /etc/nginx/nginx.conf.template > /tmp/nginx.conf

echo "webserver: PORT=$PORT WORKERS=$WORKER_PROCESSES x $WORKER_CONNECTIONS conn," \
     "api=${BACKEND_HOST}:${BACKEND_PORT} ($API_RATE_LIMIT req/s), front=${FRONTEND_HOST}:${FRONTEND_PORT}"
nginx -t -q -e /dev/stderr -c /tmp/nginx.conf
exec nginx -e /dev/stderr -c /tmp/nginx.conf -g 'daemon off;'
