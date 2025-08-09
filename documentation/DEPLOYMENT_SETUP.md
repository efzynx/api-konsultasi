# Setup Deployment Otomatis ke aaPanel

Dokumentasi ini menjelaskan cara setup deployment otomatis dari GitHub ke server aaPanel menggunakan GitHub Actions.

## 🏗️ Arsitektur Deployment

```
GitHub Repository
    ↓ (Push ke branch)
CI Pipeline (.github/workflows/ci.yaml)
    ↓ (Semua tests passed)
Deploy Pipeline (.github/workflows/deploy.yaml)
    ↓ (SSH ke server)
aaPanel Server
    ↓ (Docker Compose)
Running Application
```

## 📋 Prerequisites

### 1. Server aaPanel
- ✅ Server dengan aaPanel terinstall
- ✅ Docker dan Docker Compose terinstall
- ✅ SSH access ke server
- ✅ Git terinstall di server

### 2. GitHub Repository
- ✅ Repository dengan kode aplikasi
- ✅ Branch `main` untuk production
- ✅ Branch `dev` untuk staging/development

## 🔐 Setup SSH Key untuk Deployment

### Opsi A: AWS Lightsail (.pem key) - RECOMMENDED untuk AWS
```bash
# 1. Download .pem key dari AWS Lightsail Console
# 2. Set proper permissions
chmod 400 ~/Downloads/your-lightsail-key.pem

# 3. Test SSH connection
ssh -i ~/Downloads/your-lightsail-key.pem ubuntu@your-server-ip
# atau
ssh -i ~/Downloads/your-lightsail-key.pem ec2-user@your-server-ip
```

### Opsi B: Generate SSH Key Pair (untuk server non-AWS)
```bash
# Di komputer lokal Anda
ssh-keygen -t rsa -b 4096 -C "github-deploy@yourdomain.com"
# Simpan sebagai: ~/.ssh/aapanel_deploy_key

# Copy public key ke server
ssh-copy-id -i ~/.ssh/aapanel_deploy_key.pub root@your-server-ip

# Test SSH Connection
ssh -i ~/.ssh/aapanel_deploy_key root@your-server-ip
```

## 🔑 Setup GitHub Secrets

**⚠️ PENTING untuk Repository Public:**
- GitHub Secrets AMAN digunakan di repository public
- Secrets di-encrypt dan tidak terlihat di logs atau oleh user lain
- Hanya owner/admin repository yang bisa melihat secrets
- Secrets tidak pernah di-expose di GitHub Actions logs

Masuk ke GitHub Repository → Settings → Secrets and variables → Actions

### Required Secrets:

#### **Server Connection (AWS Lightsail):**
```
AAPANEL_HOST=your-lightsail-ip-or-domain
AAPANEL_USERNAME=ubuntu
# atau ec2-user tergantung AMI yang digunakan
AAPANEL_SSH_KEY=<isi dengan konten file .pem dari AWS Lightsail>
```

#### **Server Connection (Non-AWS):**
```
AAPANEL_HOST=your-server-ip-or-domain
AAPANEL_USERNAME=root
AAPANEL_SSH_KEY=<isi dengan private key dari ~/.ssh/aapanel_deploy_key>
```

#### **Production Environment:**
```
PROD_SECRET_KEY=your-very-long-and-secure-secret-key-for-production
PROD_DATABASE_URL=mysql+pymysql://prod_user:prod_password@db:3306/prod_database
PROD_JWT_SECRET_KEY=your-jwt-secret-key-for-production
PROD_MYSQL_ROOT_PASSWORD=very-secure-root-password
PROD_MYSQL_DATABASE=api_konsultasi_prod
PROD_MYSQL_USER=api_user_prod
PROD_MYSQL_PASSWORD=secure-database-password
PROD_SERVER_URL=https://your-production-domain.com
```

#### **Development/Staging Environment:**
```
DEV_SECRET_KEY=your-secret-key-for-development
DEV_DATABASE_URL=mysql+pymysql://dev_user:dev_password@db:3306/dev_database
DEV_JWT_SECRET_KEY=your-jwt-secret-key-for-development
DEV_MYSQL_ROOT_PASSWORD=dev-root-password
DEV_MYSQL_DATABASE=api_konsultasi_dev
DEV_MYSQL_USER=api_user_dev
DEV_MYSQL_PASSWORD=dev-database-password
DEV_SERVER_URL=https://dev.your-domain.com
```

## 🚀 Setup Server Directory Structure

### 1. Login ke Server
```bash
# AWS Lightsail
ssh -i ~/Downloads/your-lightsail-key.pem ubuntu@your-server-ip

# Non-AWS
ssh root@your-server-ip
```

### 2. Install Docker (jika belum ada)
```bash
# Update system
sudo apt update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group (AWS Lightsail)
sudo usermod -aG docker ubuntu
# atau untuk ec2-user:
# sudo usermod -aG docker ec2-user

# Restart untuk apply group changes
sudo systemctl restart docker
```

### 3. Create Directory Structure
```bash
# Untuk Production
sudo mkdir -p /opt/api-konsultasi-prod
sudo chown -R $USER:$USER /opt/api-konsultasi-prod

# Untuk Development/Staging  
sudo mkdir -p /opt/api-konsultasi-dev
sudo chown -R $USER:$USER /opt/api-konsultasi-dev
```

### 3. Setup Nginx (Opsional)
Jika ingin menggunakan domain/subdomain, setup reverse proxy di aaPanel:

**Production (api.yourdomain.com):**
```nginx
location / {
    proxy_pass http://127.0.0.1:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

**Development (dev-api.yourdomain.com):**
```nginx
location / {
    proxy_pass http://127.0.0.1:5001;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

## 🔄 Workflow Deployment

### Automatic Deployment Triggers:

1. **Push ke branch `main`** → Deploy ke Production
2. **Push ke branch `dev`** → Deploy ke Staging
3. **Manual trigger** → Deploy ke environment yang dipilih

### Deployment Process:

1. ✅ **CI Pipeline berjalan** (tests, linting, security scan)
2. ✅ **Semua checks passed**
3. 🚀 **Deploy Pipeline triggered**
4. 📥 **Code di-pull ke server**
5. 🐳 **Docker containers di-build dan di-start**
6. 🏥 **Health check**
7. 🧪 **Post-deployment tests**
8. ✅ **Deployment complete**

### Rollback Process:
Jika deployment gagal, sistem akan otomatis rollback ke versi sebelumnya.

## 📊 Monitoring Deployment

### 1. GitHub Actions
- Lihat status di tab "Actions" di GitHub repository
- Monitor logs untuk setiap step

### 2. Server Monitoring
```bash
# Check running containers
docker ps

# Check application logs
docker logs <container-name>

# Check system resources
htop
df -h
```

### 3. Application Health
```bash
# Test API endpoint
curl http://localhost:5000/api/v1/auth/health

# Test from external
curl https://your-domain.com/api/v1/auth/health
```

## 🛠️ Troubleshooting

### Common Issues:

#### 1. SSH Connection Failed
```bash
# Test SSH connection
ssh -i ~/.ssh/aapanel_deploy_key root@your-server-ip

# Check SSH key permissions
chmod 600 ~/.ssh/aapanel_deploy_key
```

#### 2. Docker Build Failed
```bash
# Check Docker status on server
systemctl status docker

# Check disk space
df -h

# Clean up Docker
docker system prune -f
```

#### 3. Database Connection Failed
```bash
# Check MySQL container
docker logs <mysql-container-name>

# Test database connection
docker exec -it <mysql-container> mysql -u root -p
```

#### 4. Port Already in Use
```bash
# Check what's using the port
lsof -i :5000

# Kill process if needed
sudo kill -9 <PID>
```

## 🔧 Manual Deployment (Backup Method)

Jika auto-deployment gagal, Anda bisa deploy manual:

```bash
# 1. SSH ke server
ssh root@your-server-ip

# 2. Navigate to project directory
cd /www/wwwroot/api-konsultasi-prod  # atau -dev

# 3. Pull latest changes
git pull origin main  # atau dev

# 4. Rebuild containers
docker compose down
docker compose up -d --build

# 5. Check status
docker ps
curl http://localhost:5000/api/v1/auth/health
```

## 📈 Best Practices

1. **Always test di dev branch** sebelum merge ke main
2. **Monitor logs** setelah deployment
3. **Backup database** secara berkala
4. **Update secrets** secara berkala
5. **Monitor server resources** (CPU, RAM, Disk)
6. **Setup SSL certificate** untuk production
7. **Enable firewall** dan security measures
8. **Regular security updates** untuk server

## 🎯 Next Steps

Setelah setup selesai:

1. ✅ Test deployment dengan push ke dev branch
2. ✅ Verify aplikasi berjalan di staging
3. ✅ Test semua API endpoints
4. ✅ Deploy ke production (merge dev ke main)
5. ✅ Setup monitoring dan alerting
6. ✅ Setup backup strategy
7. ✅ Documentation untuk team

---

**🚨 Important Notes:**
- Selalu backup sebelum deployment
- Test di staging sebelum production
- Monitor aplikasi setelah deployment
- Keep secrets secure dan update berkala
