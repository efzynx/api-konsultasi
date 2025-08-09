# 🚀 Deployment Guide for aaPanel

## Prerequisites
- aaPanel installed and configured
- Python 3.11+ available
- MySQL/MariaDB database
- Domain/subdomain configured

## 1. Clone Repository on aaPanel Server

```bash
cd /www/wwwroot/your-domain.com
git clone https://github.com/efzynx/api-konsultasi.git .
git checkout dev  # Use the dev branch with CI/CD
```

## 2. Environment Setup

### Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Environment Variables
Copy and configure the environment file:
```bash
cp .env.example .env
```

Edit `.env` with your production settings:
```env
SECRET_KEY=your-super-secret-production-key-here
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/api_konsultasi
JWT_SECRET_KEY=your-jwt-secret-key-here
FLASK_ENV=production
```

## 3. Database Setup

### Create Database
In aaPanel MySQL manager or command line:
```sql
CREATE DATABASE api_konsultasi CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'api_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON api_konsultasi.* TO 'api_user'@'localhost';
FLUSH PRIVILEGES;
```

### Initialize Database
```bash
python -c "
from project import create_app
from project import db
app = create_app()
with app.app_context():
    db.create_all()
    print('Database tables created successfully!')
"
```

## 4. aaPanel Configuration

### Python App Setup
1. Go to **Website** → **Python Project**
2. Click **Add Python Project**
3. Configure:
   - **Project Name**: API Konsultasi
   - **Domain**: your-domain.com
   - **Project Path**: `/www/wwwroot/your-domain.com`
   - **Python Version**: 3.11+
   - **Framework**: Flask
   - **Startup File**: `wsgi.py`
   - **Module Name**: `app`

### Nginx Configuration
Add to your site's Nginx config:
```nginx
location / {
    proxy_pass http://127.0.0.1:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# Health check endpoint
location /health {
    proxy_pass http://127.0.0.1:5000/health;
    access_log off;
}
```

## 5. Production Optimizations

### Gunicorn Configuration
Create `gunicorn.conf.py`:
```python
bind = "127.0.0.1:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
```

### Start with Gunicorn
```bash
gunicorn -c gunicorn.conf.py wsgi:app
```

## 6. SSL Certificate
1. In aaPanel, go to **Website** → **SSL**
2. Enable **Let's Encrypt** for your domain
3. Force HTTPS redirect

## 7. Monitoring & Logs

### Health Check
Your API now includes a health check endpoint:
```bash
curl https://your-domain.com/health
```

### Log Files
- Application logs: `/www/wwwroot/your-domain.com/logs/`
- Nginx logs: `/www/wwwlogs/your-domain.com/`

## 8. Testing Deployment

### Test API Endpoints
```bash
# Health check
curl https://your-domain.com/health

# Register user
curl -X POST https://your-domain.com/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass","nama":"Test User","nim":"123456","role":"mahasiswa"}'

# Login
curl -X POST https://your-domain.com/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass"}'

# Get dosen list
curl https://your-domain.com/dosen
```

## 9. Continuous Deployment

### GitHub Webhook (Optional)
1. In aaPanel, create a webhook script:
```bash
#!/bin/bash
cd /www/wwwroot/your-domain.com
git pull origin dev
source venv/bin/activate
pip install -r requirements.txt
supervisorctl restart your-app-name
```

2. Add webhook URL to GitHub repository settings

## 10. Backup Strategy

### Database Backup
```bash
mysqldump -u api_user -p api_konsultasi > backup_$(date +%Y%m%d_%H%M%S).sql
```

### File Backup
```bash
tar -czf api_backup_$(date +%Y%m%d_%H%M%S).tar.gz /www/wwwroot/your-domain.com
```

## 🎉 Your API is Now Live!

Visit: `https://your-domain.com/health` to verify deployment

## Troubleshooting

### Common Issues:
1. **Database Connection**: Check DATABASE_URL in .env
2. **Permission Issues**: `chown -R www:www /www/wwwroot/your-domain.com`
3. **Python Path**: Ensure virtual environment is activated
4. **Port Conflicts**: Check if port 5000 is available

### Debug Mode (Development Only):
```bash
export FLASK_ENV=development
python run.py
```

## Security Checklist
- ✅ Strong SECRET_KEY and JWT_SECRET_KEY
- ✅ Database user with limited privileges
- ✅ SSL certificate enabled
- ✅ Firewall configured
- ✅ Regular backups scheduled
- ✅ Environment variables secured
