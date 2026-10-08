FROM public.ecr.aws/docker/library/python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=8081

WORKDIR /app
COPY api.py ./api.py

USER 10001:10001
EXPOSE 8081
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD ["python3", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8081/health', timeout=2)"]

ENTRYPOINT ["python3", "/app/api.py"]
