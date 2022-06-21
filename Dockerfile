FROM python:3.10

WORKDIR /app

RUN set -eu ;\
  apt-get update ;\
  apt-get install -y libicu-dev ;\
  apt-get clean all ;\
  rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock /app/

RUN set -eu; \
  python -m pip install --upgrade pip; \
  pip install poetry==1.1.7 poetry-core==1.0.4; \
  poetry config virtualenvs.create false; \
  poetry install --no-dev --no-interaction --no-ansi; \
  pip uninstall --yes poetry; \
  rm -rf /root/.cache

COPY . /app

RUN useradd --create-home line-server
USER line-server

CMD ["python", "-m", "line_server.server"]
