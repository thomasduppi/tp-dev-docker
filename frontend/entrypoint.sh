#!/bin/sh
# Point d'entrée du frontend : génère la config nginx à partir des arguments
# reçus au run, la valide, puis "exec nginx" pour que tini lui relaie les signaux.
set -eu

: "${PORT:=8080}"
: "${WORKER_PROCESSES:=1}"
: "${WORKER_CONNECTIONS:=256}"

case "$WORKER_PROCESSES" in
    auto) ;;
    ''|*[!0-9]*) echo "Erreur : WORKER_PROCESSES doit valoir 'auto' ou un entier" >&2; exit 1 ;;
esac
require_int() {
    case "$2" in
        ''|*[!0-9]*) echo "Erreur : $1 doit être un entier (reçu '$2')" >&2; exit 1 ;;
    esac
}
require_int PORT "$PORT"
require_int WORKER_CONNECTIONS "$WORKER_CONNECTIONS"

sed -e "s/__PORT__/$PORT/" \
    -e "s/__WORKER_PROCESSES__/$WORKER_PROCESSES/" \
    -e "s/__WORKER_CONNECTIONS__/$WORKER_CONNECTIONS/" \
    /etc/nginx/nginx.conf.template > /tmp/nginx.conf

echo "frontend: PORT=$PORT WORKER_PROCESSES=$WORKER_PROCESSES WORKER_CONNECTIONS=$WORKER_CONNECTIONS"
nginx -t -q -e /dev/stderr -c /tmp/nginx.conf
exec nginx -e /dev/stderr -c /tmp/nginx.conf -g 'daemon off;'
