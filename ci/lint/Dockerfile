# Conteneur CI : analyse statique de tout le dépôt (monté en lecture seule).
FROM tictactoe/base:1.0

# - py3-flake8 : lint Python (PEP 8, imports inutilisés, erreurs de syntaxe).
# - shellcheck : lint des scripts shell (entrypoints), bugs POSIX courants.
# - nginx      : uniquement pour "nginx -t", valider la syntaxe des modèles.
RUN apk add --no-cache py3-flake8 shellcheck nginx

ENV SRC_DIR=/src \
    FLAKE8_MAX_LINE_LENGTH=110

COPY lint.sh /usr/local/bin/lint.sh
RUN sed -i 's/\r$//' /usr/local/bin/lint.sh \
 && chmod 0755 /usr/local/bin/lint.sh

USER app
WORKDIR /src

# Conteneur "one-shot" : code de sortie 0 = OK, 1 = au moins une erreur.
ENTRYPOINT ["/sbin/tini", "--", "/usr/local/bin/lint.sh"]
