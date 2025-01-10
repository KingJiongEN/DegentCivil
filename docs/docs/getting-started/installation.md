# Installation Guide

This guide will walk you through the process of setting up the Degent Civil on your system.

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8 or higher
- Docker and Docker Compose
- Git
- A text editor of your choice

## Step 1: Clone the Repository

```bash
git clone https://github.com/KingJiongEN/DegentCivil.git
cd DegentCivil
```

## Step 2: Set Up Python Environment

It's recommended to use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
pip install -r requirements.txt
```

## Step 3: Set Up Docker Services

### Milvus Setup

1. Create directories for Milvus:
```bash
mkdir milvus
mkdir milvus/db
mkdir milvus/minio
```

2. Start Milvus using Docker Compose:
```bash
docker-compose -f docker-compose_milvus.yml up -d
```

Milvus visualization will be available at:
- URL: `localhost:18000`
- Username: `minioadmin`
- Password: `minioadmin`

### Redis Setup

Start Redis using Docker:
```bash
docker pull redis
docker run --name my-redis -p 6379:6379 -d redis
```

For a secured Redis instance:
```bash
docker run --name my-redis-secured -p 6379:6379 -d -v ./redis.conf:/usr/local/etc/redis/redis.conf redis redis-server /usr/local/etc/redis/redis.conf
```

## Step 4: Configuration

1. Create OpenAI configuration:
```bash
# Create the config directory if it doesn't exist
mkdir -p config
# Create OAI_CONFIG_LIST file (you'll need to edit this with your API key)
touch config/OAI_CONFIG_LIST
```

2. Set up your OpenAI API key:
```bash
export OPENAI_API_KEY=your_api_key_here
```

## Step 5: Verify Installation

Run the memory demo to verify your installation:
```bash
export PYTHONPATH="{project_path}:$PYTHONPATH"
python -m app.models.memory
```

## Common Issues

### Docker Services

If you encounter issues with Docker services:

1. Ensure Docker daemon is running:
```bash
docker info
```

2. Check service status:
```bash
docker ps
```

3. View service logs:
```bash
docker logs my-redis
docker-compose -f docker-compose_milvus.yml logs
```

### Python Dependencies

If you encounter Python dependency issues:

1. Ensure you're using the correct Python version:
```bash
python --version
```

2. Update pip:
```bash
pip install --upgrade pip
```

3. Reinstall dependencies:
```bash
pip install -r requirements.txt --force-reinstall
```

## Next Steps

- Follow our [Quick Start Guide](quick-start.md) to begin using the service
- Read through [Core Concepts](../core-concepts/overview.md) to understand the system
- Check out [Examples](../examples/basic-usage.md) for common use cases 