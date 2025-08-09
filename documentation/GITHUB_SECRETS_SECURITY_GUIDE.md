# GitHub Secrets & OIDC Security Guide

Panduan lengkap untuk menggunakan GitHub Secrets dengan aman dan implementasi OIDC untuk deployment ke AWS.

## 📋 Daftar Isi

1. [GitHub Secrets (Traditional Method)](#github-secrets-traditional-method)
2. [OIDC dengan AWS (Recommended)](#oidc-dengan-aws-recommended)
3. [Perbandingan Keamanan](#perbandingan-keamanan)
4. [Best Practices](#best-practices)
5. [Troubleshooting](#troubleshooting)

---

## 🔐 GitHub Secrets (Traditional Method)

### Mengapa GitHub Secrets Aman di Repository Public?

**✅ Keamanan GitHub Secrets:**
- **Encrypted at rest**: Secrets di-encrypt menggunakan AES-256-GCM
- **Encrypted in transit**: Semua komunikasi menggunakan TLS
- **Access control**: Hanya owner/admin repository yang bisa melihat secrets
- **Audit logs**: Semua akses ke secrets tercatat
- **Redacted in logs**: Secrets otomatis di-redact dari GitHub Actions logs
- **Environment protection**: Bisa dibatasi per environment (production/staging)

### Setup GitHub Secrets untuk AWS Lightsail

#### 1. Persiapan di AWS Lightsail

```bash
# 1. Download .pem key dari AWS Lightsail Console
# 2. Set permissions yang benar
chmod 400 ~/Downloads/your-lightsail-key.pem

# 3. Test koneksi SSH
ssh -i ~/Downloads/your-lightsail-key.pem ubuntu@your-lightsail-ip
```

#### 2. Setup Secrets di GitHub Repository

**Langkah-langkah:**
1. Buka GitHub Repository → **Settings**
2. Klik **Secrets and variables** → **Actions**
3. Klik **New repository secret**

**Required Secrets:**

```bash
# Server Connection
LIGHTSAIL_HOST=your-lightsail-ip-or-domain
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

#### 3. Cara Menambahkan SSH Key ke Secrets

```bash
# 1. Baca konten file .pem
cat ~/Downloads/your-lightsail-key.pem

# 2. Copy seluruh konten (termasuk -----BEGIN dan -----END)
# 3. Paste ke GitHub Secret dengan nama LIGHTSAIL_SSH_KEY
```

**Contoh konten .pem key:**
```
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA1234567890abcdef...
(banyak baris kode)
...xyz123456789
-----END RSA PRIVATE KEY-----
```

#### 4. GitHub Actions Workflow untuk Traditional Method

```yaml
name: Deploy to AWS Lightsail

on:
  push:
    branches: [ main, dev ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Setup SSH
      run: |
        mkdir -p ~/.ssh
        echo "${{ secrets.LIGHTSAIL_SSH_KEY }}" > ~/.ssh/lightsail_key
        chmod 600 ~/.ssh/lightsail_key
        ssh-keyscan -H ${{ secrets.LIGHTSAIL_HOST }} >> ~/.ssh/known_hosts
    
    - name: Deploy to server
      run: |
        ssh -i ~/.ssh/lightsail_key ${{ secrets.LIGHTSAIL_USERNAME }}@${{ secrets.LIGHTSAIL_HOST }} << 'EOF'
        cd /opt/api-konsultasi-prod
        git pull origin main
        docker compose down
        docker compose up -d --build
        EOF
```

---

## 🚀 OIDC dengan AWS (Recommended)

### Mengapa OIDC Lebih Aman?

**✅ Keuntungan OIDC:**
- **No long-lived credentials**: Tidak ada secret key yang disimpan
- **Temporary tokens**: Token akses bersifat sementara (15 menit - 12 jam)
- **Fine-grained permissions**: Kontrol akses yang sangat spesifik
- **Audit trail**: Semua akses tercatat di AWS CloudTrail
- **Automatic rotation**: Token otomatis di-refresh
- **Zero secret management**: Tidak perlu manage secret keys

### Setup OIDC untuk AWS

#### 1. Setup IAM Identity Provider di AWS

```bash
# 1. Login ke AWS Console
# 2. Buka IAM → Identity providers → Add provider
# 3. Pilih "OpenID Connect"
# 4. Provider URL: https://token.actions.githubusercontent.com
# 5. Audience: sts.amazonaws.com
```

**Atau menggunakan AWS CLI:**
```bash
aws iam create-open-id-connect-provider \
    --url https://token.actions.githubusercontent.com \
    --client-id-list sts.amazonaws.com \
    --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

#### 2. Buat IAM Role untuk GitHub Actions

**Trust Policy (trust-policy.json):**
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

**Permission Policy (permissions-policy.json):**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lightsail:*",
        "ec2:DescribeInstances",
        "ec2:DescribeImages",
        "ec2:DescribeSnapshots"
      ],
      "Resource": "*"
    }
  ]
}
```

**Buat Role:**
```bash
# 1. Buat role
aws iam create-role \
    --role-name GitHubActionsRole \
    --assume-role-policy-document file://trust-policy.json

# 2. Attach policy
aws iam put-role-policy \
    --role-name GitHubActionsRole \
    --policy-name GitHubActionsPolicy \
    --policy-document file://permissions-policy.json
```

#### 3. GitHub Actions Workflow dengan OIDC

```yaml
name: Deploy to AWS Lightsail (OIDC)

on:
  push:
    branches: [ main, dev ]

permissions:
  id-token: write   # Required for OIDC
  contents: read    # Required for checkout

env:
  AWS_REGION: us-east-1

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Configure AWS credentials using OIDC
      uses: aws-actions/configure-aws-credentials@v4
      with:
        role-to-assume: arn:aws:iam::${{ secrets.AWS_ACCOUNT_ID }}:role/GitHubActionsRole
        aws-region: ${{ env.AWS_REGION }}
        role-session-name: GitHubActions-${{ github.run_id }}
    
    - name: Get Lightsail instance info
      run: |
        # Get instance details
        aws lightsail get-instance --instance-name your-instance-name
        
        # Get instance IP
        INSTANCE_IP=$(aws lightsail get-instance --instance-name your-instance-name --query 'instance.publicIpAddress' --output text)
        echo "INSTANCE_IP=$INSTANCE_IP" >> $GITHUB_ENV
    
    - name: Setup SSH using AWS Systems Manager
      run: |
        # Install session manager plugin
        curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/ubuntu_64bit/session-manager-plugin.deb" -o "session-manager-plugin.deb"
        sudo dpkg -i session-manager-plugin.deb
    
    - name: Deploy using SSH
      run: |
        # Setup SSH key from AWS Parameter Store (optional)
        # atau gunakan SSH key yang sudah ada di server
        
        # Deploy aplikasi
        ssh -o StrictHostKeyChecking=no ubuntu@${{ env.INSTANCE_IP }} << 'EOF'
        cd /opt/api-konsultasi-prod
        git pull origin main
        
        # Setup environment variables
        cat > .env << ENVEOF
        SECRET_KEY=${{ secrets.PROD_SECRET_KEY }}
        DATABASE_URL=${{ secrets.PROD_DATABASE_URL }}
        JWT_SECRET_KEY=${{ secrets.PROD_JWT_SECRET_KEY }}
        MYSQL_ROOT_PASSWORD=${{ secrets.PROD_MYSQL_ROOT_PASSWORD }}
        MYSQL_DATABASE=${{ secrets.PROD_MYSQL_DATABASE }}
        MYSQL_USER=${{ secrets.PROD_MYSQL_USER }}
        MYSQL_PASSWORD=${{ secrets.PROD_MYSQL_PASSWORD }}
        FLASK_ENV=production
        ENVEOF
        
        # Deploy with Docker
        docker compose down
        docker compose up -d --build
        
        # Health check
        sleep 30
        curl -f http://localhost:5000/api/v1/auth/health || echo "Health check failed"
        EOF
```

#### 4. Required GitHub Secrets untuk OIDC

**Minimal secrets yang dibutuhkan:**
```bash
# AWS Account
AWS_ACCOUNT_ID=123456789012

# Application secrets (tetap diperlukan)
PROD_SECRET_KEY=your-secret-key
PROD_DATABASE_URL=mysql+pymysql://user:pass@db:3306/db
PROD_JWT_SECRET_KEY=your-jwt-secret
# ... dst
```

---

## ⚖️ Perbandingan Keamanan

| Aspek | GitHub Secrets | OIDC |
|-------|----------------|------|
| **Long-lived credentials** | ❌ Ya (SSH keys) | ✅ Tidak |
| **Automatic rotation** | ❌ Manual | ✅ Otomatis |
| **Fine-grained permissions** | ⚠️ Terbatas | ✅ Sangat detail |
| **Audit trail** | ✅ GitHub logs | ✅ AWS CloudTrail |
| **Setup complexity** | ✅ Mudah | ⚠️ Sedang |
| **Maintenance** | ⚠️ Manual rotation | ✅ Minimal |
| **Cost** | ✅ Gratis | ✅ Gratis |
| **Vendor lock-in** | ⚠️ GitHub only | ⚠️ AWS focused |

---

## 🛡️ Best Practices

### 1. Environment-based Secrets

```yaml
# Gunakan environment protection
jobs:
  deploy-staging:
    environment: staging
    # secrets khusus staging
    
  deploy-production:
    environment: production
    # secrets khusus production
    needs: deploy-staging
```

### 2. Secret Rotation Strategy

```bash
# Rotate secrets secara berkala
# 1. Generate secret baru
openssl rand -base64 32

# 2. Update di GitHub Secrets
# 3. Deploy aplikasi
# 4. Verify aplikasi berjalan
# 5. Hapus secret lama
```

### 3. Monitoring dan Alerting

```yaml
- name: Notify deployment status
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### 4. Backup Strategy

```bash
# Backup secrets ke secure location
# 1. Export secrets (encrypted)
# 2. Store di secure vault (1Password, Bitwarden, etc.)
# 3. Document recovery procedures
```

---

## 🔧 Troubleshooting

### Common Issues dengan GitHub Secrets

#### 1. SSH Key Format Error
```bash
# Problem: SSH key tidak terbaca
# Solution: Pastikan format benar
-----BEGIN RSA PRIVATE KEY-----
(konten key)
-----END RSA PRIVATE KEY-----
```

#### 2. Permission Denied
```bash
# Problem: SSH permission denied
# Solution: Check key permissions
chmod 600 ~/.ssh/private_key
```

#### 3. Secret Not Found
```bash
# Problem: Secret tidak ditemukan
# Solution: Verify secret name dan scope
echo "Secret value: ${{ secrets.SECRET_NAME }}"
```

### Common Issues dengan OIDC

#### 1. Trust Relationship Error
```bash
# Problem: AssumeRoleWithWebIdentity failed
# Solution: Check trust policy
aws iam get-role --role-name GitHubActionsRole
```

#### 2. Permission Denied
```bash
# Problem: Insufficient permissions
# Solution: Check IAM policy
aws iam list-attached-role-policies --role-name GitHubActionsRole
```

#### 3. Token Expiration
```bash
# Problem: Token expired
# Solution: Token otomatis refresh, check workflow timing
```

---

## 📚 Resources

### Documentation
- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [AWS OIDC Documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc.html)
- [GitHub OIDC Documentation](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)

### Tools
- [AWS CLI](https://aws.amazon.com/cli/)
- [GitHub CLI](https://cli.github.com/)
- [OpenSSL](https://www.openssl.org/)

### Security Checkers
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)
- [TruffleHog](https://github.com/trufflesecurity/trufflehog)
- [GitLeaks](https://github.com/zricethezav/gitleaks)

---

## 🎯 Rekomendasi

### Untuk Production:
1. **Gunakan OIDC** jika memungkinkan
2. **Environment protection** untuk production
3. **Secret rotation** setiap 90 hari
4. **Monitoring dan alerting** aktif
5. **Backup strategy** yang jelas

### Untuk Development:
1. **GitHub Secrets** sudah cukup
2. **Separate environments** (dev/staging/prod)
3. **Different credentials** per environment
4. **Regular testing** deployment process

### Security Checklist:
- ✅ Secrets tidak pernah di-commit ke repository
- ✅ Minimal required permissions
- ✅ Regular secret rotation
- ✅ Monitoring dan audit logs
- ✅ Backup dan recovery plan
- ✅ Team access control
- ✅ Environment separation

---

**🚨 Important Notes:**
- Jangan pernah commit secrets ke repository
- Gunakan environment variables untuk semua sensitive data
- Regular audit dan rotation secrets
- Monitor deployment logs untuk anomali
- Backup secrets di secure location
- Document semua procedures untuk team
