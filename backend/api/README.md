# Library

## Getting started

### Building and running for development

**Steps:**

1. Create `.env` file at the project's root directory and fill it with necessary environment variables.
   You can find an example of `.env` file in `.env.example`.

2. Build and run docker container with `dev` env:

    ```commandline
   scripts/dev.sh up -d
    ```

3. Activate virtual environment:

    ```commandline
   poetry shell
    ```

4. Run `auth` service locally:

   ```commandline
   uvicorn src.main:app --reload
    ```

   or

   ```commandline
   python -m src.main
   ```

run tests

```commandline
pytest ./tests 
```

## Running database migrations

NOTE: First run your database inside of docker container

### Apply migrations

```
alembic upgrade head
```
