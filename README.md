# line-server

The line-server service serves line out of the `text.txt` file to network clients via [HTTP API](#http-api). The contents of the `text.txt` file is store in a Redis data store.

- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Development](#development)
- [HTTP API](#http-api)

### Prerequisites

The following needs to be installed:

- [docker](https://docs.docker.com/get-docker/)
- [docker-compose](https://docs.docker.com/compose/install/)
- [poetry](https://python-poetry.org/docs/#installation)
- [pyinvoke](https://www.pyinvoke.org/installing.html) ([homebrew](https://formulae.brew.sh/formula/pyinvoke) can also be used to install this)

## Configuration

### Environment variables

`.env.example` contains the available environment variables and some default
values for development.

Creates a `.env` based of the `.env.example` file.

```
cp .env.example .env
```

| Env Var      | Default                | Comment                            |
| ------------ | ---------------------- | ---------------------------------- |
| `REDIS_HOST` | `host.docker.internal` |                                    |
| `REDIS_PORT` | `6379`                 |                                    |
| `PORT`       | `8000`                 | Port on which the service listens. |

## Development

This service uses [pyinvoke](http://docs.pyinvoke.org/en/1.2/index.html) to run scripts more easily. For a full list of invoke commands run `invoke --list`.

### Run service inside docker

```
sh run.sh
```

The `run.sh` script does the following:

- Creates a `data` network
- Runs a redis container
- Builds the line-server image
- Runs the line-server image as a container

### Install Dependencies

```
poetry install

# Activate the project’s virtualenv.
poetry shell

```

### Run tests

Tests run outside of docker. Please make sure you [install dependencies](#install-dependencies) first. The below invoke task runs a redis container needed for testing and run tests.

```
invoke test
```

## HTTP API

### Get a line

```
GET /lines/:line_index

# Response

200 OK

"A line text"

```

If a line request is beyond the end of the file a status code of `413` is returned.
