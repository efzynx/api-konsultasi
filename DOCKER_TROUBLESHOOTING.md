# 🐳 Docker Troubleshooting Guide

## Common Issues and Solutions

### 1. Port Already in Use Error
**Error**: `failed to bind host port for 0.0.0.0:5000:172.21.0.2:5000/tcp: address already in use`

**Solutions**:

#### Option A: Use the Docker Helper Script (Recommended)
```bash
# Kill processes on port 5000
./docker-helper.sh kill-port 5000

# Start on alternative port
./docker-helper.sh start 5001
```

#### Option B: Manual Port Management
```bash
# Find what's using port 5000
lsof -i :5000

# Kill the process (replace PID with actual process ID)
kill -9 <PID>

# Or kill all Python processes
pkill -f python
```

#### Option C: Use Different Port in Docker Compose
```bash
# Start with custom port mapping
docker-compose up --build -d
# Then access via http://localhost:5001 (as configured in docker-compose.override.yml)
```

### 2. Docker Permission Denied
**Error**: `permission denied while trying to connect to the Docker daemon socket`

**Solutions**:

#### Option A: Add User to Docker Group
```bash
sudo usermod -aG docker $USER
newgrp docker
```

#### Option B: Use Sudo (Temporary)
```bash
sudo ./docker-helper.sh test
sudo docker-compose up --build
```

#### Option C: Fix Docker Socket Permissions
```bash
sudo chmod 666 /var/run/docker.sock
```

### 3. Container Won't Start
**Symptoms**: Container exits immediately or fails to respond

**Debugging Steps**:
```bash
# Check container logs
docker logs api_konsultasi-server-1

# Check if container is running
docker ps -a

# Inspect container
docker inspect api_konsultasi-server-1

# Test with interactive mode
docker run -it --rm api-konsultasi:latest /bin/bash
```

### 4. Database Connection Issues
**Error**: Database connection failures in container

**Solutions**:
```bash
# Check environment variables
docker exec api_konsultasi-server-1 env | grep DATABASE

# Test database connectivity
docker exec api_konsultasi-server-1 python -c "from project import create_app; app = create_app(); print('DB OK')"

# Reset database
docker-compose down -v
docker-compose up --build
```

## Quick Commands Reference

### Port Management
```bash
# Check port usage
./docker-helper.sh port-check 5000

# Free up port
./docker-helper.sh kill-port 5000

# Find available port starting from 5000
for port in {5000..5010}; do
  if ! lsof -Pi :$port -sTCP:LISTEN -t >/dev/null; then
    echo "Port $port is available"
    break
  fi
done
```

### Container Management
```bash
# Clean up all containers
./docker-helper.sh cleanup

# Stop all services
./docker-helper.sh stop

# View logs
./docker-helper.sh logs

# Restart services
docker-compose restart
```

### Testing
```bash
# Run comprehensive tests locally
pytest test_api_comprehensive.py -v

# Test Docker container
./docker-helper.sh test

# Test specific endpoint
curl http://localhost:5001/api/v1/auth/health
```

## Environment-Specific Solutions

### Development Environment
```bash
# Use override file for development
cp docker-compose.override.yml.example docker-compose.override.yml
# Edit ports and volumes as needed
docker-compose up --build
```

### CI/CD Environment
The GitHub Actions workflow automatically handles:
- Port conflict detection and resolution
- Container cleanup between runs
- Alternative port usage (5001 if 5000 is busy)
- Proper error handling and logging

### Production Environment
```bash
# Use production compose file
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Monitor with health checks
docker-compose ps
curl http://localhost:5000/api/v1/auth/health
```

## Prevention Tips

1. **Always cleanup after testing**:
   ```bash
   ./docker-helper.sh stop
   ```

2. **Use different ports for different environments**:
   - Development: 5001
   - Testing: 5002
   - Production: 5000

3. **Check ports before starting**:
   ```bash
   ./docker-helper.sh port-check 5000
   ```

4. **Use the helper script for consistent management**:
   ```bash
   ./docker-helper.sh help
   ```

## Getting Help

If you encounter issues not covered here:

1. **Check container logs**:
   ```bash
   docker-compose logs server
   ```

2. **Verify environment**:
   ```bash
   docker-compose config
   ```

3. **Test basic functionality**:
   ```bash
   pytest test_api_comprehensive.py::TestHealthCheck::test_health_check -v
   ```

4. **Reset everything**:
   ```bash
   ./docker-helper.sh stop
   docker system prune -f
   ./docker-helper.sh start
