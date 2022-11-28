from invoke import task


@task
def network(c):
    """
    Create 'data' network if doesn't already exist
    """
    exists = not c.run(
        "docker network ls | grep data --quiet", warn=True
    ).exited
    print("'Data' network already exists") if exists else c.run(
        "docker network create data"
    )


@task
def devenv(c):
    """
    Start Redis in the background
    """
    c.run("docker-compose up -d")


@task
def build(c):
    """
    Build the line-server image
    """
    c.run("docker build -t line-server . ", pty=True)


@task
def start(c):
    """
    Run the line-server image as a container
    """
    c.run(
        "docker run \
        -it \
        --rm \
        --publish 8000:8000 \
        --mount type=bind,src=${PWD},dst=/app \
        --name line-server \
        line-server",
        pty=True,
    )


@task
def stop(c):
    """
    Stop the line-server container
    """
    c.run("docker stop line-server", pty=True)


@task
def lint(c):
    """
    Run all pre-commit checks
    """
    c.run(
        "poetry run pre-commit run --all-files",
        warn=True,
    )


@task
def devenv_test(c):
    """
    Build a line-server-test image
    """

    c.run("docker build -f Dockerfile.test -t line-server-test .")


@task
def test(c):
    """
    Run tests inside docker
    """

    c.run(
        "docker run --rm --mount type=bind,src=${PWD},dst=/app --network=data line-server-test python -m pytest --cov=line_server --cov-report term . -vvv -s"
    )
