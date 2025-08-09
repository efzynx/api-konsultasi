#!/bin/bash

# Generate Secure Secrets Script
# This script generates secure secrets for deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to generate secure password
generate_password() {
    local length=${1:-32}
    if command_exists openssl; then
        openssl rand -base64 $((length * 3 / 4)) | tr -d "=+/" | cut -c1-$length
    elif command_exists python3; then
        python3 -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range($length)))"
    else
        # Fallback method
        cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w $length | head -n 1
    fi
}

# Function to generate Flask secret key
generate_flask_secret() {
    if command_exists python3; then
        python3 -c "import secrets; print(secrets.token_urlsafe(50))"
    else
        generate_password 64
    fi
}

# Function to generate JWT secret
generate_jwt_secret() {
    if command_exists python3; then
        python3 -c "import secrets; print(secrets.token_urlsafe(32))"
    else
        generate_password 43
    fi
}

print_status "🔐 Secure Secrets Generator"
echo "=========================="

# Check prerequisites
print_status "Checking prerequisites..."

if ! command_exists openssl && ! command_exists python3; then
    print_warning "Neither OpenSSL nor Python3 found. Using fallback method."
    print_warning "For better security, install OpenSSL or Python3."
fi

print_success "Prerequisites check completed."

# Get deployment information
echo ""
print_status "Deployment Configuration"
echo "========================"

read -p "Enter your project name (default: api-konsultasi): " PROJECT_NAME
PROJECT_NAME=${PROJECT_NAME:-"api-konsultasi"}

read -p "Enter your AWS Lightsail instance IP: " LIGHTSAIL_IP
read -p "Enter your domain name (optional, press Enter to skip): " DOMAIN_NAME

# Generate all secrets
echo ""
print_status "Generating secure secrets..."

# Flask secrets
PROD_SECRET_KEY=$(generate_flask_secret)
DEV_SECRET_KEY=$(generate_flask_secret)

# JWT secrets
PROD_JWT_SECRET_KEY=$(generate_jwt_secret)
DEV_JWT_SECRET_KEY=$(generate_jwt_secret)

# Database passwords
PROD_MYSQL_ROOT_PASSWORD=$(generate_password 32)
PROD_MYSQL_PASSWORD=$(generate_password 32)
DEV_MYSQL_ROOT_PASSWORD=$(generate_password 32)
DEV_MYSQL_PASSWORD=$(generate_password 32)

# Database names and users
PROD_DB_NAME="${PROJECT_NAME}_prod"
PROD_DB_USER="${PROJECT_NAME}_user_prod"
DEV_DB_NAME="${PROJECT_NAME}_dev"
DEV_DB_USER="${PROJECT_NAME}_user_dev"

print_success "All secrets generated successfully."

# Create secrets file
SECRETS_FILE="github-secrets-$(date +%Y%m%d-%H%M%S).txt"
cat > "$SECRETS_FILE" << EOF
# GitHub Secrets Configuration
# Generated on: $(date)
# Project: $PROJECT_NAME

# ================================
# GITHUB REPOSITORY VARIABLES
# ================================
# Add these in: Settings → Secrets and variables → Actions → Variables

DEPLOYMENT_METHOD=traditional
LIGHTSAIL_INSTANCE_NAME=$PROJECT_NAME-server
EOF

if [ -n "$DOMAIN_NAME" ]; then
cat >> "$SECRETS_FILE" << EOF
PROD_SERVER_URL=https://api.$DOMAIN_NAME
DEV_SERVER_URL=https://dev-api.$DOMAIN_NAME
EOF
fi

cat >> "$SECRETS_FILE" << EOF

# ================================
# GITHUB REPOSITORY SECRETS
# ================================
# Add these in: Settings → Secrets and variables → Actions → Secrets

# Server Connection (Traditional SSH Method)
LIGHTSAIL_HOST=$LIGHTSAIL_IP
LIGHTSAIL_USERNAME=ubuntu
LIGHTSAIL_SSH_KEY=<paste-your-pem-key-content-here>

# Production Environment Secrets
PROD_SECRET_KEY=$PROD_SECRET_KEY
PROD_DATABASE_URL=mysql+pymysql://$PROD_DB_USER:$PROD_MYSQL_PASSWORD@db:3306/$PROD_DB_NAME
PROD_JWT_SECRET_KEY=$PROD_JWT_SECRET_KEY
PROD_MYSQL_ROOT_PASSWORD=$PROD_MYSQL_ROOT_PASSWORD
PROD_MYSQL_DATABASE=$PROD_DB_NAME
PROD_MYSQL_USER=$PROD_DB_USER
PROD_MYSQL_PASSWORD=$PROD_MYSQL_PASSWORD

# Development Environment Secrets
DEV_SECRET_KEY=$DEV_SECRET_KEY
DEV_DATABASE_URL=mysql+pymysql://$DEV_DB_USER:$DEV_MYSQL_PASSWORD@db:3306/$DEV_DB_NAME
DEV_JWT_SECRET_KEY=$DEV_JWT_SECRET_KEY
DEV_MYSQL_ROOT_PASSWORD=$DEV_MYSQL_ROOT_PASSWORD
DEV_MYSQL_DATABASE=$DEV_DB_NAME
DEV_MYSQL_USER=$DEV_DB_USER
DEV_MYSQL_PASSWORD=$DEV_MYSQL_PASSWORD

# ================================
# FOR OIDC METHOD (Alternative)
# ================================
# If using OIDC instead of traditional SSH:
# AWS_ACCOUNT_ID=your-aws-account-id

# ================================
# LOCAL DEVELOPMENT .env FILES
# ================================

EOF

# Create local .env files
print_status "Creating local development environment files..."

# Production .env template
cat > ".env.production.template" << EOF
# Production Environment Variables
# Copy this to .env for production deployment

SECRET_KEY=$PROD_SECRET_KEY
DATABASE_URL=mysql+pymysql://$PROD_DB_USER:$PROD_MYSQL_PASSWORD@db:3306/$PROD_DB_NAME
JWT_SECRET_KEY=$PROD_JWT_SECRET_KEY
MYSQL_ROOT_PASSWORD=$PROD_MYSQL_ROOT_PASSWORD
MYSQL_DATABASE=$PROD_DB_NAME
MYSQL_USER=$PROD_DB_USER
MYSQL_PASSWORD=$PROD_MYSQL_PASSWORD
FLASK_ENV=production
EOF

# Development .env template
cat > ".env.development.template" << EOF
# Development Environment Variables
# Copy this to .env for local development

SECRET_KEY=$DEV_SECRET_KEY
DATABASE_URL=mysql+pymysql://$DEV_DB_USER:$DEV_MYSQL_PASSWORD@localhost:3306/$DEV_DB_NAME
JWT_SECRET_KEY=$DEV_JWT_SECRET_KEY
MYSQL_ROOT_PASSWORD=$DEV_MYSQL_ROOT_PASSWORD
MYSQL_DATABASE=$DEV_DB_NAME
MYSQL_USER=$DEV_DB_USER
MYSQL_PASSWORD=$DEV_MYSQL_PASSWORD
FLASK_ENV=development
EOF

# Create local development .env (SQLite for simplicity)
cat > ".env.local.template" << EOF
# Local Development Environment Variables (SQLite)
# Copy this to .env for local development with SQLite

SECRET_KEY=$DEV_SECRET_KEY
DATABASE_URL=sqlite:///instance/local_dev.db
JWT_SECRET_KEY=$DEV_JWT_SECRET_KEY
FLASK_ENV=development
EOF

# Create docker-compose override for local development
cat > "docker-compose.local.yml" << EOF
# Docker Compose override for local development
# Usage: docker-compose -f compose.yaml -f docker-compose.local.yml up

version: '3.8'

services:
  web:
    environment:
      - DATABASE_URL=sqlite:///instance/local_dev.db
    volumes:
      - ./instance:/app/instance
    ports:
      - "5000:5000"
  
  # Remove database service for local SQLite development
  db:
    profiles:
      - disabled
EOF

# Create setup instructions
cat > "deployment-setup-instructions.md" << EOF
# Deployment Setup Instructions

## Quick Start

1. **Add GitHub Variables:**
   - Go to: Settings → Secrets and variables → Actions → Variables
   - Add: \`DEPLOYMENT_METHOD=traditional\`
   - Add: \`LIGHTSAIL_INSTANCE_NAME=$PROJECT_NAME-server\`

2. **Add GitHub Secrets:**
   - Go to: Settings → Secrets and variables → Actions → Secrets
   - Copy secrets from: \`$SECRETS_FILE\`
   - Add each secret individually

3. **Setup AWS Lightsail Server:**
   \`\`\`bash
   # SSH to your server
   ssh -i your-key.pem ubuntu@$LIGHTSAIL_IP
   
   # Run server setup
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker ubuntu
   
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-\$(uname -s)-\$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   
   # Create directories
   sudo mkdir -p /opt/$PROJECT_NAME-prod /opt/$PROJECT_NAME-dev
   sudo chown -R ubuntu:ubuntu /opt/$PROJECT_NAME-*
   \`\`\`

4. **Test Deployment:**
   \`\`\`bash
   # Push to dev branch for testing
   git checkout dev
   git push origin dev
   
   # Check GitHub Actions for deployment status
   # If successful, deploy to production:
   git checkout main
   git merge dev
   git push origin main
   \`\`\`

## Files Created:
- \`$SECRETS_FILE\` - GitHub secrets configuration
- \`.env.production.template\` - Production environment template
- \`.env.development.template\` - Development environment template  
- \`.env.local.template\` - Local development template
- \`docker-compose.local.yml\` - Local development override
- \`deployment-setup-instructions.md\` - This file

## Security Notes:
- Keep \`$SECRETS_FILE\` secure and delete after setup
- Never commit .env files to repository
- Use different passwords for production and development
- Regular rotation of secrets (every 90 days)

## Next Steps:
1. Review generated secrets
2. Add secrets to GitHub repository
3. Setup AWS Lightsail server
4. Test deployment process
5. Setup monitoring and backups
EOF

print_success "Setup files created successfully!"

echo ""
print_status "📁 Files Created:"
echo "- $SECRETS_FILE (GitHub secrets)"
echo "- .env.production.template (Production environment)"
echo "- .env.development.template (Development environment)"
echo "- .env.local.template (Local development)"
echo "- docker-compose.local.yml (Local development override)"
echo "- deployment-setup-instructions.md (Setup guide)"

echo ""
print_status "🔐 Security Summary:"
echo "- Generated $(echo "$PROD_SECRET_KEY" | wc -c) character Flask secret keys"
echo "- Generated $(echo "$PROD_JWT_SECRET_KEY" | wc -c) character JWT secret keys"
echo "- Generated 32 character database passwords"
echo "- All secrets use cryptographically secure random generation"

echo ""
print_warning "⚠️  Important Security Notes:"
echo "1. Keep $SECRETS_FILE secure and delete after GitHub setup"
echo "2. Never commit .env files to your repository"
echo "3. Use different secrets for production and development"
echo "4. Rotate secrets every 90 days"
echo "5. Monitor access logs regularly"

echo ""
print_status "📋 Next Steps:"
echo "1. 📖 Read deployment-setup-instructions.md"
echo "2. 🔐 Add secrets to GitHub repository"
echo "3. 🖥️  Setup AWS Lightsail server"
echo "4. 🧪 Test deployment with dev branch"
echo "5. 🚀 Deploy to production"

echo ""
print_success "🎉 Secret generation completed!"
print_status "Happy deploying! 🚀"
