#!/bin/sh
# Point d'entrée du backend : valide les arguments reçus au run puis remplace
# le shell par Python (exec) pour que tini lui transmette directement SIGTERM.
set -eu

: "${PORT:=8081}"
: "${DB_PATH:=/data/games.db}"
: "${HISTORY_LIMIT:=20}"
: "${REQUEST_QUEUE_SIZE:=64}"
export PORT DB_PATH HISTORY_LIMIT REQUEST_QUEUE_SIZE

require_int() {
    case "$2" in
        ''|*[!0-9]*) echo "Erreur : $1 doit être un entier (reçu '$2')" >&2; exit 1 ;;
    esac
}
require_int PORT "$PORT"
require_int HISTORY_LIMIT "$HISTORY_LIMIT"
require_int REQUEST_QUEUE_SIZE "$REQUEST_QUEUE_SIZE"

db_dir="$(dirname "$DB_PATH")"
if [ ! -w "$db_dir" ]; then
    echo "Erreur : le dossier $db_dir n'est pas accessible en écriture" >&2
    exit 1
fi

echo "backend: PORT=$PORT DB_PATH=$DB_PATH HISTORY_LIMIT=$HISTORY_LIMIT REQUEST_QUEUE_SIZE=$REQUEST_QUEUE_SIZE"
exec python3 /app/api.py "$@"
