# Use an official Python runtime as a parent image
FROM python:3.11.3-slim

RUN apt-get update && apt-get install -y curl

# Set the working directory in the container
WORKDIR /app

# Install Poetry (Python dependency manager)
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    mv /root/.local/bin/poetry /usr/local/bin/poetry

# Copy the poetry.lock and pyproject.toml files
COPY pyproject.toml poetry.lock /app/

# Install dependencies using Poetry
RUN poetry install --no-interaction --no-ansi --no-root

# Copy the rest of the application code
COPY ollama_summarizer/app /app/

# Expose the FastAPI app port
EXPOSE 8000

# Run FastAPI app with Uvicorn when the container starts
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
