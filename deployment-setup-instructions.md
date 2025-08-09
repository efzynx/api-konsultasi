# Deployment Setup Instructions

## Quick Start

1. **Add GitHub Variables:**
   - Go to: Settings → Secrets and variables → Actions → Variables
   - Add: `DEPLOYMENT_METHOD=traditional`
   - Add: `LIGHTSAIL_INSTANCE_NAME=api-konsultasi-server`

2. **Add GitHub Secrets:**
   - Go to: Settings → Secrets and variables → Actions → Secrets
   - Copy secrets from: `github-secrets-20250809-175359.txt`
   - Add each secret individually

3. **Setup AWS Lightsail Server:**
   ```bash
   # SSH to your server
   ssh -i your-key.pem ubuntu@18.140.105.226
   
   # Run server setup
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker ubuntu
   
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   
   # Create directories
   sudo mkdir -p /opt/api-konsultasi-prod /opt/api-konsultasi-dev
   sudo chown -R ubuntu:ubuntu /opt/api-konsultasi-*
   ```

4. **Test Deployment:**
   ```bash
   # Push to dev branch for testing
   git checkout dev
   git push origin dev
   
   # Check GitHub Actions for deployment status
   # If successful, deploy to production:
   git checkout main
   git merge dev
   git push origin main
   ```

## Files Created:
- `github-secrets-20250809-175359.txt` - GitHub secrets configuration
- `.env.production.template` - Production environment template
- `.env.development.template` - Development environment template  
- `.env.local.template` - Local development template
- `docker-compose.local.yml` - Local development override
- `deployment-setup-instructions.md` - This file

## Security Notes:
- Keep `github-secrets-20250809-175359.txt` secure and delete after setup
- Never commit .env files to repository
- Use different passwords for production and development
- Regular rotation of secrets (every 90 days)

## Next Steps:
1. Review generated secrets
2. Add secrets to GitHub repository
3. Setup AWS Lightsail server
4. Test deployment process
5. Setup monitoring and backups
