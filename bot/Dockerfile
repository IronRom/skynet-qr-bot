FROM ghcr.io/withlogicco/poetry:1.7.1-python-3.12

WORKDIR /app

COPY bot ./bot
COPY app.py .
COPY config.py .
COPY poetry.lock .
COPY pyproject.toml .

RUN poetry install --no-interaction --no-cache --no-root


CMD ["poetry", "run", "python", "app.py"]