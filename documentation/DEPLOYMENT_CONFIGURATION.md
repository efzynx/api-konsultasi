# Konfigurasi Deployment AWS Lightsail

Panduan lengkap untuk mengkonfigurasi deployment otomatis ke AWS Lightsail menggunakan GitHub Actions.

## 📋 Daftar Isi

1. [Pilihan Metode Deployment](#pilihan-metode-deployment)
2. [Konfigurasi Traditional SSH Method](#konfigurasi-traditional-ssh-method)
3. [Konfigurasi OIDC Method](#konfigurasi-oidc-method)
4. [GitHub Variables dan Secrets](#github-variables-dan-secrets)
5. [Testing Deployment](#testing-deployment)
6. [Troubleshooting](#troubleshooting)

---

## 🚀 Pilihan Metode Deployment

Anda dapat memilih salah satu dari dua metode deployment:

### 1. **Traditional SSH Method** (Mudah Setup)
- ✅ Setup cepat dan mudah
- ✅ Tidak perlu konfigurasi AWS IAM yang kompleks
- ⚠️ Menggunakan long-lived SSH keys
- ⚠️ Perlu manual rotation SSH keys

### 2. **OIDC Method** (Recommended untuk Production)
- ✅ Lebih aman (no long-lived credentials)
- ✅ Automatic token rotation
- ✅ Fine-grained AWS permissions
- ⚠️ Setup lebih kompleks
- ⚠️ Perlu konfigurasi AWS IAM

---

## 🔐 Konfigurasi Traditional SSH Method

### Step 1: Persiapan AWS Lightsail Instance

```bash
# 1. Login ke AWS Lightsail instance
ssh -i ~/Downloads/your-lightsail-key.pem ubuntu@your-instance-ip

# 2. Install Docker dan Docker Compose
sudo apt update
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 3. Install Git
sudo apt install git -y

# 4. Create deployment directories
sudo mkdir -p /opt/api-konsultasi-prod
sudo mkdir -p /opt/api-konsultasi-dev
sudo chown -R ubuntu:ubuntu /opt/api-konsultasi-*

# 5. Clone repository (initial setup)
cd /opt/api-konsultasi-prod
git clone -b main https://github.com/YOUR-USERNAME/YOUR-REPO.git .

cd /opt/api-konsultasi-dev
git clone -b dev https://github.com/YOUR-USERNAME/YOUR-REPO.git .

# 6. Logout dan login kembali untuk apply docker group
exit
```

### Step 2: Setup GitHub Repository Variables

**Repository Variables** (Settings → Secrets and variables → Actions → Variables):

```bash
# Deployment method
DEPLOYMENT_METHOD=traditional

# Instance information (optional, for documentation)
LIGHTSAIL_INSTANCE_NAME=your-instance-name
```

### Step 3: Setup GitHub Repository Secrets

**Repository Secrets** (Settings → Secrets and variables → Actions → Secrets):

```bash
# Server Connection
LIGHTSAIL_HOST=your-lightsail-public-ip
LIGHTSAIL_USERNAME=ubuntu
LIGHTSAIL_SSH_KEY=<paste konten file .pem di sini>

# Production Environment
PROD_SECRET_KEY=your-very-secure-secret-key-min-32-chars
PROD_DATABASE_URL=mysql+pymysql://prod_user:prod_pass@db:3306/prod_db
PROD_JWT_SECRET_KEY=your-jwt-secret-key-min-32-chars
PROD_MYSQL_ROOT_PASSWORD=very-secure-root-password
PROD_MYSQL_DATABASE=api_konsultasi_prod
PROD_MYSQL_USER=api_user_prod
PROD_MYSQL_PASSWORD=secure-database-password

# Development Environment
DEV_SECRET_KEY=dev-secret-key-min-32-chars
DEV_DATABASE_URL=mysql+pymysql://dev_user:dev_pass@db:3306/dev_db
DEV_JWT_SECRET_KEY=dev-jwt-secret-key-min-32-chars
DEV_MYSQL_ROOT_PASSWORD=dev-root-password
DEV_MYSQL_DATABASE=api_konsultasi_dev
DEV_MYSQL_USER=api_user_dev
DEV_MYSQL_PASSWORD=dev-database-password
```

### Step 4: Cara Menambahkan SSH Key ke GitHub Secrets

```bash
# 1. Baca konten file .pem
cat ~/Downloads/your-lightsail-key.pem

# 2. Copy seluruh konten (termasuk header dan footer)
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
(banyak baris)
...
-----END RSA PRIVATE KEY-----

# 3. Paste ke GitHub Secret dengan nama LIGHTSAIL_SSH_KEY
```

---

## 🌐 Konfigurasi OIDC Method

### Step 1: Setup AWS IAM Identity Provider

```bash
# Login ke AWS Console
# 1. Buka IAM → Identity providers → Add provider
# 2. Provider type: OpenID Connect
# 3. Provider URL: https://token.actions.githubusercontent.com
# 4. Audience: sts.amazonaws.com
# 5. Thumbprint: 6938fd4d98bab03faadb97b34396831e3780aea1

# Atau menggunakan AWS CLI:
aws iam create-open-id-connect-provider \
    --url https://token.actions.githubusercontent.com \
    --client-id-list sts.amazonaws.com \
    --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

### Step 2: Create IAM Role untuk GitHub Actions

**Trust Policy** (`trust-policy.json`):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::YOUR-ACCOUNT-ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:YOUR-USERNAME/YOUR-REPO:*"
        }
      }
    }
  ]
}
```

**Permission Policy** (`permissions-policy.json`):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lightsail:GetInstance",
        "lightsail:GetInstances",
        "ssm:SendCommand",
        "ssm:DescribeInstanceInformation",
        "ssm:GetCommandInvocation"
      ],
      "Resource": "*"
    }
  ]
}
```

**Create Role:**
```bash
# 1. Create role
aws iam create-role \
    --role-name GitHubActionsRole \
    --assume-role-policy-document file://trust-policy.json

# 2. Attach policy
aws iam put-role-policy \
    --role-name GitHubActionsRole \
    --policy-name GitHubActionsPolicy \
    --policy-document file://permissions-policy.json
```

### Step 3: Setup GitHub Repository Variables (OIDC)

```bash
# Deployment method
DEPLOYMENT_METHOD=oidc

# Instance information
LIGHTSAIL_INSTANCE_NAME=your-instance-name

# Server URLs (optional)
PROD_SERVER_URL=https://api.yourdomain.com
DEV_SERVER_URL=https://dev-api.yourdomain.com
```

### Step 4: Setup GitHub Repository Secrets (OIDC)

```bash
# AWS Account
AWS_ACCOUNT_ID=123456789012

# Application secrets (tetap diperlukan)
PROD_SECRET_KEY=your-secret-key
PROD_DATABASE_URL=mysql+pymysql://user:pass@db:3306/db
PROD_JWT_SECRET_KEY=your-jwt-secret
PROD_MYSQL_ROOT_PASSWORD=root-password
PROD_MYSQL_DATABASE=api_konsultasi_prod
PROD_MYSQL_USER=api_user_prod
PROD_MYSQL_PASSWORD=db-password

# Development secrets
DEV_SECRET_KEY=dev-secret-key
DEV_DATABASE_URL=mysql+pymysql://dev_user:dev_pass@db:3306/dev_db
DEV_JWT_SECRET_KEY=dev-jwt-secret
DEV_MYSQL_ROOT_PASSWORD=dev-root-password
DEV_MYSQL_DATABASE=api_konsultasi_dev
DEV_MYSQL_USER=api_user_dev
DEV_MYSQL_PASSWORD=dev-db-password
```

---

## 📝 GitHub Variables dan Secrets

### Repository Variables

| Variable Name | Description | Example |
|---------------|-------------|---------|
| `DEPLOYMENT_METHOD` | Metode deployment (`traditional` atau `oidc`) | `traditional` |
| `LIGHTSAIL_INSTANCE_NAME` | Nama instance di AWS Lightsail | `my-api-server` |
| `PROD_SERVER_URL` | URL production server (optional) | `https://api.domain.com` |
| `DEV_SERVER_URL` | URL development server (optional) | `https://dev-api.domain.com` |

### Repository Secrets

#### Server Connection (Traditional Method):
| Secret Name | Description | Example |
|-------------|-------------|---------|
| `LIGHTSAIL_HOST` | IP atau domain server | `1.2.3.4` |
| `LIGHTSAIL_USERNAME` | Username SSH | `ubuntu` |
| `LIGHTSAIL_SSH_KEY` | Private key (.pem) content | `-----BEGIN RSA...` |

#### Server Connection (OIDC Method):
| Secret Name | Description | Example |
|-------------|-------------|---------|
| `AWS_ACCOUNT_ID` | AWS Account ID | `123456789012` |

#### Application Secrets (Both Methods):
| Secret Name | Description |
|-------------|-------------|
| `PROD_SECRET_KEY` | Flask secret key untuk production |
| `PROD_DATABASE_URL` | Database URL production |
| `PROD_JWT_SECRET_KEY` | JWT secret key production |
| `PROD_MYSQL_ROOT_PASSWORD` | MySQL root password production |
| `PROD_MYSQL_DATABASE` | Database name production |
| `PROD_MYSQL_USER` | Database user production |
| `PROD_MYSQL_PASSWORD` | Database password production |
| `DEV_SECRET_KEY` | Flask secret key untuk development |
| `DEV_DATABASE_URL` | Database URL development |
| `DEV_JWT_SECRET_KEY` | JWT secret key development |
| `DEV_MYSQL_ROOT_PASSWORD` | MySQL root password development |
| `DEV_MYSQL_DATABASE` | Database name development |
| `DEV_MYSQL_USER` | Database user development |
| `DEV_MYSQL_PASSWORD` | Database password development |

---

## 🧪 Testing Deployment

### 1. Test Traditional SSH Method

```bash
# 1. Set DEPLOYMENT_METHOD variable ke 'traditional'
# 2. Push ke dev branch untuk test staging
git checkout dev
git add .
git commit -m "test: deployment to staging"
git push origin dev

# 3. Monitor di GitHub Actions tab
# 4. Jika berhasil, merge ke main untuk production
git checkout main
git merge dev
git push origin main
```

### 2. Test OIDC Method

```bash
# 1. Set DEPLOYMENT_METHOD variable ke 'oidc'
# 2. Pastikan AWS IAM role sudah dikonfigurasi
# 3. Push ke dev branch
git checkout dev
git add .
git commit -m "test: OIDC deployment to staging"
git push origin dev

# 4. Monitor di GitHub Actions tab
```

### 3. Manual Testing

```bash
# Test API endpoints setelah deployment
curl http://your-server-ip:5000/api/v1/auth/health
curl http://your-server-ip:5001/api/v1/auth/health  # dev environment

# Test registration
curl -X POST http://your-server-ip:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123","nama":"Test User","nim":"123456"}'
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. SSH Permission Denied (Traditional Method)
```bash
# Problem: SSH key tidak bisa digunakan
# Solution: Check format dan permissions
# - Pastikan konten .pem key lengkap (dengan header/footer)
# - Pastikan tidak ada extra spaces atau newlines
```

#### 2. Docker Permission Denied
```bash
# Problem: Docker command permission denied
# Solution: Add user to docker group
sudo usermod -aG docker ubuntu
# Logout dan login kembali
```

#### 3. Port Already in Use
```bash
# Problem: Port 5000/5001 sudah digunakan
# Solution: Stop existing containers
docker ps
docker stop <container-id>
```

#### 4. OIDC Role Assumption Failed
```bash
# Problem: Cannot assume IAM role
# Solution: Check trust policy dan repository settings
# - Verify AWS_ACCOUNT_ID secret
# - Check trust policy repository path
# - Verify OIDC provider configuration
```

#### 5. Health Check Failed
```bash
# Problem: Application tidak respond di health check
# Solution: Check application logs
docker logs <container-name>

# Check if application is running
docker ps
netstat -tlnp | grep 5000
```

### Debug Commands

```bash
# Check deployment logs di server
ssh -i your-key.pem ubuntu@your-server-ip
cd /opt/api-konsultasi-prod
docker compose logs

# Check container status
docker ps -a

# Check system resources
free -h
df -h
```

---

## 📚 Quick Start Checklist

### Traditional SSH Method:
- [ ] Download .pem key dari AWS Lightsail
- [ ] Setup server (Docker, Git, directories)
- [ ] Add GitHub Variables: `DEPLOYMENT_METHOD=traditional`
- [ ] Add GitHub Secrets: `LIGHTSAIL_HOST`, `LIGHTSAIL_USERNAME`, `LIGHTSAIL_SSH_KEY`
- [ ] Add Application Secrets: `PROD_*`, `DEV_*`
- [ ] Test deployment dengan push ke dev branch
- [ ] Deploy ke production dengan push ke main branch

### OIDC Method:
- [ ] Setup AWS IAM Identity Provider
- [ ] Create IAM Role dengan trust policy
- [ ] Add GitHub Variables: `DEPLOYMENT_METHOD=oidc`, `LIGHTSAIL_INSTANCE_NAME`
- [ ] Add GitHub Secrets: `AWS_ACCOUNT_ID`
- [ ] Add Application Secrets: `PROD_*`, `DEV_*`
- [ ] Test deployment dengan push ke dev branch
- [ ] Deploy ke production dengan push ke main branch

---

## 🎯 Best Practices

1. **Always test di dev branch** sebelum deploy ke production
2. **Monitor GitHub Actions logs** untuk setiap deployment
3. **Setup health checks** untuk verify deployment success
4. **Use environment-specific secrets** untuk production dan development
5. **Regular backup** database dan application data
6. **Monitor server resources** (CPU, RAM, Disk)
7. **Setup alerting** untuk deployment failures
8. **Document rollback procedures** untuk emergency situations

---

**🚨 Security Reminders:**
- Jangan commit secrets ke repository
- Use strong passwords untuk database
- Regular rotation untuk secrets
- Monitor access logs
- Setup firewall rules di AWS Lightsail
- Enable HTTPS untuk production
