FROM python:3.13-alpine
RUN pip install poetry==2.1.2

# Set the working directory
WORKDIR /app
# Copy the files
COPY pyproject.toml poetry.lock .env ./
COPY dropdock ./dropdock
RUN touch README.md
RUN poetry install
ENTRYPOINT [ "poetry", "run", "dockdrop" ]
