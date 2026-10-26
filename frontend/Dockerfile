# Frontend React : build multi-étapes, les deux étapes partent de notre base.

# --- Étape 1 : compilation de l'application React avec Vite -----------------
FROM tictactoe/base:1.0 AS build

# Node.js + npm depuis les dépôts Alpine, uniquement pour compiler. Ils ne se
# retrouvent pas dans l'image finale.
RUN apk add --no-cache nodejs npm

WORKDIR /app
# package.json copié seul d'abord : la couche "npm install" reste en cache tant
# que les dépendances ne changent pas.
COPY package.json ./
RUN npm install --no-audit --no-fund
COPY index.html vite.config.js ./
COPY src ./src
RUN npm run build

# --- Étape 2 : image d'exécution, nginx sert les fichiers statiques ---------
FROM tictactoe/base:1.0

# nginx depuis les dépôts Alpine. On supprime la config par défaut : la nôtre
# est générée au démarrage par entrypoint.sh.
RUN apk add --no-cache nginx \
 && rm -f /etc/nginx/http.d/default.conf

ENV PORT=8080 \
    WORKER_PROCESSES=1 \
    WORKER_CONNECTIONS=256

COPY nginx.conf /etc/nginx/nginx.conf.template
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
COPY --from=build /app/dist /usr/share/nginx/html

RUN sed -i 's/\r$//' /usr/local/bin/entrypoint.sh \
 && chmod 0755 /usr/local/bin/entrypoint.sh

# Non-root : d'où le port 8080 (> 1024, pas besoin de CAP_NET_BIND_SERVICE).
USER app
EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q -O /dev/null "http://127.0.0.1:${PORT}/healthz" || exit 1

# nginx : SIGTERM = arrêt brutal, SIGQUIT = arrêt gracieux (finit les requêtes).
STOPSIGNAL SIGQUIT
ENTRYPOINT ["/sbin/tini", "--", "/usr/local/bin/entrypoint.sh"]
