#!/bin/sh
# Lint du dépôt monté dans $SRC_DIR. Toutes les vérifications sont lancées,
# puis le script échoue si au moins une a échoué.
set -u

: "${SRC_DIR:=/src}"
: "${FLAKE8_MAX_LINE_LENGTH:=110}"
cd "$SRC_DIR" || exit 1
status=0

step() { printf '\n==> %s\n' "$1"; }

# Arrêt propre si on reçoit SIGTERM pendant le lint.
trap 'echo "SIGTERM reçu, arrêt du lint"; exit 143' TERM

step "Python (flake8)"
if flake8 --max-line-length="$FLAKE8_MAX_LINE_LENGTH" backend ci; then
    echo "OK"
else
    status=1
fi

step "Scripts shell (shellcheck)"
# Les fichiers peuvent avoir des fins de ligne Windows : on lint une copie LF.
tmp="$(mktemp -d)"
find . -name '*.sh' -not -path './frontend/node_modules/*' | while read -r f; do
    mkdir -p "$tmp/$(dirname "$f")"
    sed 's/\r$//' "$f" > "$tmp/$f"
done
if (cd "$tmp" && find . -name '*.sh' -exec shellcheck -s sh {} +); then
    echo "OK"
else
    status=1
fi

step "Modèles nginx (nginx -t)"
for dir in frontend webserver; do
    sed -e 's/__PORT__/8080/' -e 's/__WORKER_PROCESSES__/1/' \
        -e 's/__WORKER_CONNECTIONS__/64/' -e 's/__CLIENT_MAX_BODY_SIZE__/16k/' \
        -e 's/__API_RATE_LIMIT__/10/' -e 's/__[A-Z]*_HOST__/localhost/' \
        -e 's/__[A-Z]*_PORT__/8081/' "$dir/nginx.conf" > "$tmp/$dir.conf"
    if nginx -t -q -e /dev/stderr -c "$tmp/$dir.conf"; then
        echo "OK : $dir/nginx.conf"
    else
        status=1
    fi
done

step "Dockerfiles : aucune image Docker Hub"
# Seules "scratch" et nos propres images tictactoe/* sont autorisées.
bad="$(find . -name Dockerfile -not -path './frontend/node_modules/*' -exec grep -nHE '^FROM ' {} + \
    | grep -vE ':FROM (scratch|tictactoe/)')"
if [ -z "$bad" ]; then
    echo "OK"
else
    echo "$bad"
    status=1
fi

rm -rf "$tmp"
printf '\nLint %s\n' "$([ "$status" -eq 0 ] && echo 'réussi' || echo 'ÉCHOUÉ')"
exit "$status"
