FROM --platform=$BUILDPLATFORM python:3.9-bullseye as base

FROM base as builder

RUN mkdir /install
WORKDIR /install

COPY poetry.lock pyproject.toml /install/

# install poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python - 
ENV PATH="${PATH}:/root/.poetry/bin"

# upgrade pip
RUN pip install --upgrade pip setuptools wheel

# install requirements
RUN poetry export -f requirements.txt --without-hashes --output requirements.txt --extras container --dev
RUN pip install --prefix=/install -r requirements.txt

FROM --platform=$BUILDPLATFORM python:3.9-slim-bullseye

COPY --from=builder /install /usr/local
COPY todo_app /app/todo_app

EXPOSE 8000

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

WORKDIR /app
ENTRYPOINT [ "gunicorn", "todo_app:app" ]
CMD ["--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]