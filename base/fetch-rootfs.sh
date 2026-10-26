#!/bin/sh
# Télécharge le rootfs Alpine officiel utilisé par base/Dockerfile et vérifie
# son empreinte SHA-256. L'archive x86_64 est déjà versionnée dans le dépôt ;
# ce script sert à la régénérer ou à récupérer une autre architecture :
#   ./fetch-rootfs.sh            -> x86_64
#   ./fetch-rootfs.sh aarch64    -> ARM64 (puis ALPINE_ARCH=aarch64 au build)
set -eu

VERSION="${ALPINE_VERSION:-3.21.3}"
ARCH="${1:-x86_64}"
BRANCH="v$(echo "$VERSION" | cut -d. -f1,2)"
FILE="alpine-minirootfs-${VERSION}-${ARCH}.tar.gz"
URL="https://dl-cdn.alpinelinux.org/alpine/${BRANCH}/releases/${ARCH}/${FILE}"

cd "$(dirname "$0")"
curl -fsSLO "$URL"
curl -fsSL "${URL}.sha256" | sha256sum -c -
echo "OK : ${FILE}"
