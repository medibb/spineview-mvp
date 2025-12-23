# Deployment Guide: PNUH Lumbo-Pelvic Analysis Dashboard

## Synology NAS Deployment with Docker

### Prerequisites

1. **Synology NAS Requirements**:
   - DSM 7.0 or higher
   - Docker package installed (from Package Center)
   - Minimum 2GB RAM recommended
   - SSH access enabled (Control Panel > Terminal & SNMP)

2. **Local Machine Requirements**:
   - Git installed
   - SSH client (built-in on Windows 10+, Mac, Linux)

### Step 1: Prepare Synology NAS

1. **Install Docker**:
   - Open Package Center
   - Search for "Docker" or "Container Manager"
   - Click Install

2. **Create Project Directory**:
   ```bash
   # SSH into your Synology NAS
   ssh admin@your-nas-ip
   
   # Create directory for the application
   sudo mkdir -p /volume1/docker/spineview
   cd /volume1/docker/spineview
   ```

### Step 2: Clone Repository

```bash
# On your Synology NAS (via SSH)
cd /volume1/docker/spineview
git clone https://github.com/medibb/spineview-mvp.git .

# Or upload files via File Station
```

### Step 3: Configure Environment

1. **Create .env file**:
   ```bash
   cp .env.example .env
   nano .env  # or use File Station text editor
   ```

2. **Generate SECRET_KEY**:
   ```bash
   python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

3. **Update .env**:
   ```
   SECRET_KEY=<paste-generated-key-here>
   DEBUG=False
   ALLOWED_HOSTS=192.168.1.100,nas.local,localhost
   ```
   Replace `192.168.1.100` with your NAS IP address.

### Step 4: Build and Run with Docker Compose

```bash
# Build the Docker image
docker-compose build

# Start the container
docker-compose up -d

# Check logs
docker-compose logs -f web
```

### Step 5: Access the Dashboard

Open your browser and navigate to:
- `http://your-nas-ip:8000`
- `http://nas.local:8000` (if hostname is configured)

### Step 6: Verify Installation

1. Upload test CSV files (spine_dot.csv and pelvis_dot.csv)
2. Check analysis results display correctly
3. Test print functionality

## Alternative: Docker CLI (without docker-compose)

```bash
# Build image
docker build -t spineview:latest .

# Run container
docker run -d \
  --name spineview-dashboard \
  -p 8000:8000 \
  -v $(pwd)/uploads:/app/uploads \
  --env-file .env \
  --restart unless-stopped \
  spineview:latest
```

## Updating the Application

```bash
# Pull latest changes
cd /volume1/docker/spineview
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs web

# Common issues:
# - Missing .env file: Copy from .env.example
# - Port 8000 already in use: Change port in docker-compose.yml
# - Permission issues: Check uploads/ directory permissions
```

### Can't access from browser
```bash
# Check if container is running
docker ps

# Check firewall on Synology
# Control Panel > Security > Firewall

# Verify port 8000 is open
netstat -an | grep 8000
```

### Upload files not persisting
```bash
# Check volume mount
docker inspect spineview-dashboard | grep -A 10 Mounts

# Ensure uploads directory exists and has correct permissions
chmod 755 uploads
```

## Security Recommendations

1. **Change default SECRET_KEY** in .env
2. **Use HTTPS** with reverse proxy (Synology has built-in)
3. **Restrict network access** to hospital/research network only
4. **Regular backups** of uploads/ directory
5. **Update regularly** with `git pull` + rebuild

## Performance Tuning

For better performance on Synology NAS:

1. **Adjust workers** in Dockerfile:
   ```dockerfile
   CMD ["gunicorn", "config.wsgi:application", \
        "--workers", "4", \  # Increase for more CPU cores
        "--threads", "2", \
        ...
   ```

2. **Allocate more memory** to Docker:
   - Package Center > Docker > Settings
   - Increase memory limit

## Backup Strategy

```bash
# Backup uploads directory
tar -czf spineview-uploads-$(date +%Y%m%d).tar.gz uploads/

# Backup to another location
cp spineview-uploads-*.tar.gz /volume1/backups/
```

## Monitoring

```bash
# View logs
docker-compose logs -f web

# Check container status
docker-compose ps

# Resource usage
docker stats spineview-dashboard
```

## Support

For issues or questions:
- GitHub Issues: https://github.com/medibb/spineview-mvp/issues
- Email: [Your contact email]
