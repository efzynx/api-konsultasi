#!/bin/bash

# Deployment Testing Script
# This script helps test your deployment setup and monitor the application

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

# Function to test API endpoint
test_endpoint() {
    local url=$1
    local method=${2:-GET}
    local data=${3:-""}
    local expected_status=${4:-200}
    
    print_status "Testing $method $url"
    
    if [ -n "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" -H "Content-Type: application/json" -d "$data" "$url" || echo -e "\n000")
    else
        response=$(curl -s -w "\n%{http_code}" "$url" || echo -e "\n000")
    fi
    
    # Extract status code (last line)
    status_code=$(echo "$response" | tail -n1)
    # Extract response body (all but last line)
    body=$(echo "$response" | head -n -1)
    
    if [ "$status_code" -eq "$expected_status" ]; then
        print_success "✅ Status: $status_code"
        if [ -n "$body" ] && [ "$body" != "null" ]; then
            echo "   Response: $body"
        fi
        return 0
    else
        print_error "❌ Expected: $expected_status, Got: $status_code"
        if [ -n "$body" ] && [ "$body" != "null" ]; then
            echo "   Response: $body"
        fi
        return 1
    fi
}

# Function to test server connectivity
test_server_connectivity() {
    local server_url=$1
    print_status "Testing server connectivity to $server_url"
    
    if curl -s --connect-timeout 10 "$server_url" > /dev/null; then
        print_success "✅ Server is reachable"
        return 0
    else
        print_error "❌ Server is not reachable"
        return 1
    fi
}

# Function to run comprehensive API tests
run_api_tests() {
    local base_url=$1
    local test_passed=0
    local test_failed=0
    
    print_status "🧪 Running comprehensive API tests for $base_url"
    echo "=================================================="
    
    # Test 1: Health check
    if test_endpoint "$base_url/api/v1/auth/health" "GET" "" "200"; then
        ((test_passed++))
    else
        ((test_failed++))
    fi
    
    # Test 2: Register new user
    local test_username="test_$(date +%s)"
    local register_data="{\"username\":\"$test_username\",\"password\":\"test123456\",\"nama\":\"Test User\",\"nim\":\"$(date +%s)\"}"
    
    if test_endpoint "$base_url/api/v1/auth/register" "POST" "$register_data" "201"; then
        ((test_passed++))
        
        # Test 3: Login with registered user
        local login_data="{\"username\":\"$test_username\",\"password\":\"test123456\"}"
        if test_endpoint "$base_url/api/v1/auth/login" "POST" "$login_data" "200"; then
            ((test_passed++))
        else
            ((test_failed++))
        fi
    else
        ((test_failed++))
        print_warning "Skipping login test due to registration failure"
        ((test_failed++))
    fi
    
    # Test 4: Get dosen list
    if test_endpoint "$base_url/api/v1/dosen" "GET" "" "200"; then
        ((test_passed++))
    else
        ((test_failed++))
    fi
    
    # Test 5: Get mahasiswa list
    if test_endpoint "$base_url/api/v1/mahasiswa" "GET" "" "200"; then
        ((test_passed++))
    else
        ((test_failed++))
    fi
    
    # Test 6: Get booking list
    if test_endpoint "$base_url/api/v1/booking" "GET" "" "200"; then
        ((test_passed++))
    else
        ((test_failed++))
    fi
    
    echo ""
    print_status "📊 Test Results:"
    print_success "✅ Passed: $test_passed"
    if [ $test_failed -gt 0 ]; then
        print_error "❌ Failed: $test_failed"
    else
        print_success "❌ Failed: $test_failed"
    fi
    
    local total_tests=$((test_passed + test_failed))
    local success_rate=$((test_passed * 100 / total_tests))
    
    if [ $success_rate -ge 80 ]; then
        print_success "🎉 Overall: $success_rate% success rate - GOOD"
    elif [ $success_rate -ge 60 ]; then
        print_warning "⚠️  Overall: $success_rate% success rate - NEEDS ATTENTION"
    else
        print_error "🚨 Overall: $success_rate% success rate - CRITICAL"
    fi
    
    return $test_failed
}

# Function to monitor server resources
monitor_server() {
    local ssh_key=$1
    local ssh_user=$2
    local ssh_host=$3
    
    print_status "📊 Monitoring server resources on $ssh_host"
    echo "=============================================="
    
    ssh -i "$ssh_key" "$ssh_user@$ssh_host" << 'EOF'
echo "🖥️  System Information:"
echo "======================"
echo "Hostname: $(hostname)"
echo "Uptime: $(uptime -p)"
echo "Load Average: $(uptime | awk -F'load average:' '{print $2}')"
echo ""

echo "💾 Memory Usage:"
echo "==============="
free -h
echo ""

echo "💿 Disk Usage:"
echo "============="
df -h | grep -E '^/dev/'
echo ""

echo "🐳 Docker Status:"
echo "================"
if command -v docker >/dev/null 2>&1; then
    echo "Docker version: $(docker --version)"
    echo ""
    echo "Running containers:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    echo "Docker system info:"
    docker system df
else
    echo "Docker is not installed or not accessible"
fi
echo ""

echo "🌐 Network Connections:"
echo "======================"
netstat -tlnp | grep -E ':(5000|5001|3306|80|443)' || echo "No relevant ports found"
echo ""

echo "📈 System Processes (Top 10 by CPU):"
echo "===================================="
ps aux --sort=-%cpu | head -11
EOF
}

# Function to check deployment logs
check_deployment_logs() {
    local ssh_key=$1
    local ssh_user=$2
    local ssh_host=$3
    local environment=$4
    
    print_status "📋 Checking deployment logs for $environment environment"
    echo "========================================================"
    
    local server_path
    if [ "$environment" = "production" ]; then
        server_path="/www/wwwroot/api-konsultasi-prod"
    else
        server_path="/www/wwwroot/api-konsultasi-dev"
    fi
    
    ssh -i "$ssh_key" "$ssh_user@$ssh_host" << EOF
cd $server_path

echo "📁 Directory contents:"
ls -la

echo ""
echo "🐳 Docker containers in this directory:"
docker compose ps 2>/dev/null || docker-compose ps 2>/dev/null || echo "No docker-compose found"

echo ""
echo "📋 Recent application logs (last 50 lines):"
echo "==========================================="
docker compose logs --tail=50 2>/dev/null || docker-compose logs --tail=50 2>/dev/null || echo "No logs available"
EOF
}

# Main script
print_status "🧪 Deployment Testing & Monitoring Tool"
echo "========================================"

# Check prerequisites
if ! command_exists curl; then
    print_error "curl is not installed. Please install curl."
    exit 1
fi

if ! command_exists ssh; then
    print_error "SSH is not installed. Please install OpenSSH client."
    exit 1
fi

# Menu selection
echo ""
print_status "Select testing option:"
echo "1. Test Development/Staging Environment"
echo "2. Test Production Environment"
echo "3. Monitor Server Resources"
echo "4. Check Deployment Logs"
echo "5. Run Full Test Suite (Both Environments)"
echo "6. Exit"
echo ""

read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        read -p "Enter development server URL (e.g., https://dev-api.yourdomain.com): " dev_url
        run_api_tests "$dev_url"
        ;;
    2)
        read -p "Enter production server URL (e.g., https://api.yourdomain.com): " prod_url
        run_api_tests "$prod_url"
        ;;
    3)
        read -p "Enter SSH key path (default: ~/.ssh/aapanel_deploy_key): " ssh_key
        ssh_key=${ssh_key:-"$HOME/.ssh/aapanel_deploy_key"}
        read -p "Enter SSH username (default: root): " ssh_user
        ssh_user=${ssh_user:-"root"}
        read -p "Enter server host: " ssh_host
        
        if [ -f "$ssh_key" ]; then
            monitor_server "$ssh_key" "$ssh_user" "$ssh_host"
        else
            print_error "SSH key not found at $ssh_key"
            exit 1
        fi
        ;;
    4)
        read -p "Enter SSH key path (default: ~/.ssh/aapanel_deploy_key): " ssh_key
        ssh_key=${ssh_key:-"$HOME/.ssh/aapanel_deploy_key"}
        read -p "Enter SSH username (default: root): " ssh_user
        ssh_user=${ssh_user:-"root"}
        read -p "Enter server host: " ssh_host
        read -p "Enter environment (production/development): " environment
        
        if [ -f "$ssh_key" ]; then
            check_deployment_logs "$ssh_key" "$ssh_user" "$ssh_host" "$environment"
        else
            print_error "SSH key not found at $ssh_key"
            exit 1
        fi
        ;;
    5)
        read -p "Enter development server URL: " dev_url
        read -p "Enter production server URL: " prod_url
        
        echo ""
        print_status "🧪 Testing Development Environment"
        echo "=================================="
        run_api_tests "$dev_url"
        dev_result=$?
        
        echo ""
        print_status "🧪 Testing Production Environment"
        echo "================================="
        run_api_tests "$prod_url"
        prod_result=$?
        
        echo ""
        print_status "📊 Final Summary"
        echo "==============="
        if [ $dev_result -eq 0 ]; then
            print_success "✅ Development: All tests passed"
        else
            print_error "❌ Development: Some tests failed"
        fi
        
        if [ $prod_result -eq 0 ]; then
            print_success "✅ Production: All tests passed"
        else
            print_error "❌ Production: Some tests failed"
        fi
        ;;
    6)
        print_status "Goodbye! 👋"
        exit 0
        ;;
    *)
        print_error "Invalid choice. Please select 1-6."
        exit 1
        ;;
esac

echo ""
print_status "Testing completed. Check the results above."
