# Docker Deployment Guide

## Quick Start

### Option 1: Docker Compose (Recommended for Development)

```bash
# 1. Make sure your .env file has the required variables
cp backend/.env.example backend/.env  # If needed
# Edit backend/.env with your credentials

# 2. Build and run
docker-compose up --build

# 3. API will be available at http://localhost:8000
```

### Option 2: Docker Build & Run (Manual)

```bash
# 1. Build the image
cd backend
docker build -t cfg-sql-backend .

# 2. Run the container
docker run -d \
  --name cfg-sql-api \
  -p 8000:8000 \
  -e OPENAI_API_KEY="your-key" \
  -e CLICKHOUSE_HOST="your-host" \
  -e CLICKHOUSE_PORT="8443" \
  -e CLICKHOUSE_USER="default" \
  -e CLICKHOUSE_PASSWORD="your-password" \
  cfg-sql-backend

# 3. Check logs
docker logs -f cfg-sql-api
```

## Dockerfile Options

### Development: `Dockerfile`
- Single stage
- Faster builds
- Includes all dependencies
- Good for development and testing

**Usage:**
```bash
docker build -t cfg-sql-backend:dev .
```

### Production: `Dockerfile.prod`
- Multi-stage build
- Smaller image size (~40% smaller)
- Production optimized
- Multiple workers

**Usage:**
```bash
docker build -f Dockerfile.prod -t cfg-sql-backend:prod .
```

## Environment Variables

Required environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-5 | `sk-...` |
| `CLICKHOUSE_HOST` | ClickHouse Cloud host | `xxx.aws.clickhouse.cloud` |
| `CLICKHOUSE_PORT` | ClickHouse port | `8443` |
| `CLICKHOUSE_USER` | ClickHouse username | `default` |
| `CLICKHOUSE_PASSWORD` | ClickHouse password | `your-password` |

## Docker Compose Commands

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Rebuild and start
docker-compose up --build

# Stop services
docker-compose down

# View logs
docker-compose logs -f backend

# Restart service
docker-compose restart backend
```

## Deployment to Production

### Railway

1. **Connect Repository:**
   - Go to [Railway](https://railway.app)
   - Create new project from GitHub repo
   - Select `backend` as root directory

2. **Set Environment Variables:**
   Add all required env vars in Railway dashboard

3. **Railway will auto-detect Dockerfile and deploy**

### Fly.io

```bash
# 1. Install flyctl
curl -L https://fly.io/install.sh | sh

# 2. Login
flyctl auth login

# 3. Launch app (from backend directory)
cd backend
flyctl launch

# 4. Set secrets
flyctl secrets set OPENAI_API_KEY="your-key"
flyctl secrets set CLICKHOUSE_HOST="your-host"
# ... set other secrets

# 5. Deploy
flyctl deploy
```

### Docker Hub

```bash
# 1. Build production image
docker build -f backend/Dockerfile.prod -t yourusername/cfg-sql-backend:latest backend/

# 2. Push to Docker Hub
docker push yourusername/cfg-sql-backend:latest

# 3. Pull and run on server
docker pull yourusername/cfg-sql-backend:latest
docker run -d -p 8000:8000 \
  --env-file .env \
  yourusername/cfg-sql-backend:latest
```

## Health Checks

The Docker containers include health checks:

```bash
# Check health status
docker ps
# Look for "healthy" in STATUS column

# Manual health check
curl http://localhost:8000/health
```

## Troubleshooting

### Container won't start
```bash
# View logs
docker logs cfg-sql-api

# Interactive shell
docker exec -it cfg-sql-api /bin/bash
```

### Connection issues
```bash
# Test from inside container
docker exec -it cfg-sql-api python -c "
from services.clickhouse_service import ClickhouseClient
ch = ClickhouseClient()
print('Connected!')
"
```

### Rebuild from scratch
```bash
# Remove old containers and images
docker-compose down
docker rmi cfg-sql-backend

# Rebuild
docker-compose up --build
```

## Performance Tuning

### Production Settings (Dockerfile.prod)

```dockerfile
# Increase workers for better concurrency
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Adjust workers based on CPU cores:
- 2 cores = 2-4 workers
- 4 cores = 4-8 workers
- Formula: `(2 x CPU cores) + 1`

## Security Notes

1. **Never commit `.env` files** - Use Docker secrets or env vars
2. **Use non-root user** - Already configured in Dockerfile
3. **Keep base image updated** - Regularly rebuild with latest Python image
4. **Scan for vulnerabilities:**
   ```bash
   docker scan cfg-sql-backend
   ```

## File Structure

```
backend/
├── Dockerfile           # Development Dockerfile
├── Dockerfile.prod      # Production Dockerfile (multi-stage)
├── .dockerignore        # Files to exclude from build
├── requirements.txt     # Python dependencies
├── app.py              # FastAPI application
└── services/           # Service modules
```

## Next Steps

- [ ] Set up CI/CD pipeline (GitHub Actions)
- [ ] Configure monitoring (Prometheus, Grafana)
- [ ] Add rate limiting
- [ ] Set up SSL/TLS certificates
- [ ] Configure logging (structured JSON logs)