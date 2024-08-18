# Flight Manifest File Generator

This project features a Python Django REST API , designed to generate files for Flight Manifest.

## Running the App with Docker

### 1. Build the Docker Image

Build the Docker image with the current version (v0.01):

```bash
docker build -t flight_manifest_maker:v0.01 .
```

### 1. Run the Docker container

Run the Docker container with environment variables:

```bash
docker run --env-file .env -p 8000:8000 flight_manifest_maker:v0.01
```

