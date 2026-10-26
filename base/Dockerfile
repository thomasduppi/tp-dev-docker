# Image de base commune à TOUS les services du projet.
# Aucune image Docker Hub : on part de "scratch" (image vide, réservée par Docker)
# et on y décompresse le rootfs officiel d'Alpine Linux, téléchargé depuis
# dl-cdn.alpinelinux.org (voir fetch-rootfs.sh, checksum SHA-256 vérifié).
FROM scratch

ARG ALPINE_VERSION=3.21.3
ARG ALPINE_ARCH=x86_64

# ADD décompresse automatiquement une archive locale à la racine "/".
ADD alpine-minirootfs-${ALPINE_VERSION}-${ALPINE_ARCH}.tar.gz /

# Une image "scratch" n'a aucune variable d'environnement : on les définit.
ENV PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
    LANG=C.UTF-8 \
    TZ=Europe/Paris

# - tini          : mini-init (PID 1) qui relaie SIGTERM/SIGQUIT aux process et
#                   récupère les zombies. Indispensable pour un arrêt propre.
# - ca-certificates : certificats racine pour les téléchargements HTTPS (apk, npm).
# - tzdata        : fuseau horaire (horodatage des parties / des logs).
# - utilisateur "app" (uid/gid 10001), sans shell ni home : les services
#   tournent en non-root.
RUN apk upgrade --no-cache \
 && apk add --no-cache tini ca-certificates tzdata \
 && cp /usr/share/zoneinfo/Europe/Paris /etc/localtime \
 && addgroup -S -g 10001 app \
 && adduser -S -D -H -u 10001 -G app -s /sbin/nologin app

LABEL org.opencontainers.image.title="tictactoe/base" \
      org.opencontainers.image.description="Alpine ${ALPINE_VERSION} construite depuis scratch + tini" \
      org.opencontainers.image.base.name="scratch"

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["/bin/sh"]
