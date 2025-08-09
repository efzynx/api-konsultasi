#!/bin/bash

# Setup Deployment Helper Script
# This script helps you set up deployment to aaPanel server

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
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
}

# Function to generate secret key
generate_secret_key() {
    python3 -c "import secrets; print(secrets.token_urlsafe(50))"
}

print_status "🚀 aaPanel Deployment Setup Helper"
echo "=================================="

# Check prerequisites
print_status "Checking prerequisites..."

if ! command_exists ssh; then
    print_error "SSH is not installed. Please install OpenSSH client."
    exit 1
fi

if ! command_exists ssh-keygen; then
    print_error "ssh-keygen is not installed. Please install OpenSSH client."
    exit 1
fi

if ! command_exists git; then
    print_error "Git is not installed. Please install Git."
    exit 1
fi

print_success "All prerequisites are installed."

# Get server information
echo ""
print_status "Server Configuration"
echo "===================="

read -p "Enter your aaPanel server IP or domain: " SERVER_HOST
read -p "Enter SSH username (usually 'root'): " SSH_USERNAME
read -p "Enter SSH port (default 22): " SSH_PORT
SSH_PORT=${SSH_PORT:-22}

# Generate SSH key if not exists
SSH_KEY_PATH="$HOME/.ssh/aapanel_deploy_key"
if [ ! -f "$SSH_KEY_PATH" ]; then
    print_status "Generating SSH key pair..."
    ssh-keygen -t rsa -b 4096 -C "github-deploy@$(hostname)" -f "$SSH_KEY_PATH" -N ""
    print_success "SSH key pair generated at $SSH_KEY_PATH"
else
    print_warning "SSH key already exists at $SSH_KEY_PATH"
fi

# Copy public key to server
echo ""
print_status "Setting up SSH access to server..."
print_warning "You will be prompted for your server password to copy the SSH key."

if ssh-copy-id -i "$SSH_KEY_PATH.pub" -p "$SSH_PORT" "$SSH_USERNAME@$SERVER_HOST"; then
    print_success "SSH key copied to server successfully."
else
    print_error "Failed to copy SSH key to server."
    print_status "Please manually copy the following public key to your server:"
    echo ""
    cat "$SSH_KEY_PATH.pub"
    echo ""
    print_status "Add it to ~/.ssh/authorized_keys on your server."
    read -p "Press Enter when done..."
fi

# Test SSH connection
print_status "Testing SSH connection..."
if ssh -i "$SSH_KEY_PATH" -p "$SSH_PORT" -o ConnectTimeout=10 "$SSH_USERNAME@$SERVER_HOST" "echo 'SSH connection successful'"; then
    print_success "SSH connection test passed."
else
    print_error "SSH connection test failed. Please check your configuration."
    exit 1
fi

# Setup server directories
print_status "Setting up server directories..."
ssh -i "$SSH_KEY_PATH" -p "$SSH_PORT" "$SSH_USERNAME@$SERVER_HOST" << 'EOF'
# Create directories
mkdir -p /www/wwwroot/api-konsultasi-prod
mkdir -p /www/wwwroot/api-konsultasi-dev

# Set permissions
chown -R www:www /www/wwwroot/api-konsultasi-prod 2>/dev/null || chown -R $USER:$USER /www/wwwroot/api-konsultasi-prod
chown -R www:www /www/wwwroot/api-konsultasi-dev 2>/dev/null || chown -R $USER:$USER /www/wwwroot/api-konsultasi-dev

echo "Server directories created successfully."
EOF

print_success "Server directories setup completed."

# Generate secrets
echo ""
print_status "Generating secure secrets..."

PROD_SECRET_KEY=$(generate_secret_key)
PROD_JWT_SECRET_KEY=$(generate_secret_key)
PROD_MYSQL_ROOT_PASSWORD=$(generate_password)
PROD_MYSQL_PASSWORD=$(generate_password)

DEV_SECRET_KEY=$(generate_secret_key)
DEV_JWT_SECRET_KEY=$(generate_secret_key)
DEV_MYSQL_ROOT_PASSWORD=$(generate_password)
DEV_MYSQL_PASSWORD=$(generate_password)

# Create secrets file
SECRETS_FILE="deployment-secrets.txt"
cat > "$SECRETS_FILE" << EOF
# GitHub Secrets Configuration
# Copy these values to your GitHub repository secrets

# ================================
# SERVER CONNECTION SECRETS
# ================================
AAPANEL_HOST=$SERVER_HOST
AAPANEL_USERNAME=$SSH_USERNAME
AAPANEL_SSH_KEY=<paste-private-key-content-here>

# ================================
# PRODUCTION ENVIRONMENT SECRETS
# ================================
PROD_SECRET_KEY=$PROD_SECRET_KEY
PROD_DATABASE_URL=mysql+pymysql://api_user_prod:$PROD_MYSQL_PASSWORD@db:3306/api_konsultasi_prod
PROD_JWT_SECRET_KEY=$PROD_JWT_SECRET_KEY
PROD_MYSQL_ROOT_PASSWORD=$PROD_MYSQL_ROOT_PASSWORD
PROD_MYSQL_DATABASE=api_konsultasi_prod
PROD_MYSQL_USER=api_user_prod
PROD_MYSQL_PASSWORD=$PROD_MYSQL_PASSWORD
PROD_SERVER_URL=https://api.yourdomain.com

# ================================
# DEVELOPMENT ENVIRONMENT SECRETS
# ================================
DEV_SECRET_KEY=$DEV_SECRET_KEY
DEV_DATABASE_URL=mysql+pymysql://api_user_dev:$DEV_MYSQL_PASSWORD@db:3306/api_konsultasi_dev
DEV_JWT_SECRET_KEY=$DEV_JWT_SECRET_KEY
DEV_MYSQL_ROOT_PASSWORD=$DEV_MYSQL_ROOT_PASSWORD
DEV_MYSQL_DATABASE=api_konsultasi_dev
DEV_MYSQL_USER=api_user_dev
DEV_MYSQL_PASSWORD=$DEV_MYSQL_PASSWORD
DEV_SERVER_URL=https://dev-api.yourdomain.com

# ================================
# PRIVATE SSH KEY CONTENT
# ================================
# Copy the content below and paste it as AAPANEL_SSH_KEY secret:

EOF

echo "" >> "$SECRETS_FILE"
cat "$SSH_KEY_PATH" >> "$SECRETS_FILE"

print_success "Secrets generated and saved to $SECRETS_FILE"

# Create GitHub secrets setup instructions
cat > "github-secrets-setup.md" << 'EOF'
# GitHub Secrets Setup Instructions

## Step 1: Access GitHub Secrets
1. Go to your GitHub repository
2. Click on **Settings** tab
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**

## Step 2: Add Each Secret
Copy each secret from `deployment-secrets.txt` and add them one by one:

### Server Connection Secrets:
- `AAPANEL_HOST`
- `AAPANEL_USERNAME` 
- `AAPANEL_SSH_KEY` (paste the entire private key content)

### Production Secrets:
- `PROD_SECRET_KEY`
- `PROD_DATABASE_URL`
- `PROD_JWT_SECRET_KEY`
- `PROD_MYSQL_ROOT_PASSWORD`
- `PROD_MYSQL_DATABASE`
- `PROD_MYSQL_USER`
- `PROD_MYSQL_PASSWORD`
- `PROD_SERVER_URL`

### Development Secrets:
- `DEV_SECRET_KEY`
- `DEV_DATABASE_URL`
- `DEV_JWT_SECRET_KEY`
- `DEV_MYSQL_ROOT_PASSWORD`
- `DEV_MYSQL_DATABASE`
- `DEV_MYSQL_USER`
- `DEV_MYSQL_PASSWORD`
- `DEV_SERVER_URL`

## Step 3: Update Server URLs
Update the `PROD_SERVER_URL` and `DEV_SERVER_URL` with your actual domain names.

## Step 4: Test Deployment
1. Push changes to `dev` branch to test staging deployment
2. If successful, merge to `main` branch for production deployment
EOF

echo ""
print_success "Setup completed successfully!"
echo ""
print_status "Next Steps:"
echo "1. 📝 Review the generated secrets in: $SECRETS_FILE"
echo "2. 🔐 Add secrets to GitHub repository (see: github-secrets-setup.md)"
echo "3. 🌐 Update server URLs in the secrets with your actual domains"
echo "4. 🧪 Test deployment by pushing to 'dev' branch"
echo "5. 🚀 Deploy to production by merging to 'main' branch"
echo ""
print_warning "Important: Keep the secrets file secure and delete it after setup!"
echo ""
print_status "Files created:"
echo "- $SECRETS_FILE (contains all secrets)"
echo "- github-secrets-setup.md (setup instructions)"
echo "- SSH key pair: $SSH_KEY_PATH and $SSH_KEY_PATH.pub"
