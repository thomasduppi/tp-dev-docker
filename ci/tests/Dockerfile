# Conteneur CI : tests unitaires (règles du jeu) + tests d'intégration de bout
# en bout à travers le reverse proxy (webserver -> backend / frontend).
FROM tictactoe/base:1.0

# python3 : unittest et urllib suffisent, aucune dépendance pip.
RUN apk add --no-cache python3

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    BASE_URL=http://webserver:8080 \
    BACKEND_SRC=/backend \
    TEST_TIMEOUT=5

WORKDIR /tests
COPY test_*.py ./

USER app

# unittest renvoie 0 si tous les tests passent, 1 sinon (utilisable en CI).
ENTRYPOINT ["/sbin/tini", "--", "python3", "-m", "unittest", "discover", "-v", "-s", "/tests"]
