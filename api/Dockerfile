# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.9.7
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
# Download dependencies
RUN pip install -r ./requirements.txt

COPY . .

# Expose the port that the application listens on.
EXPOSE 8000

# Run the application
CMD FLASK_APP=chatbot.py flask run --host=0.0.0.0