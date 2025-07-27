#!/bin/bash
# VPS Installation Script for Facebook Messenger Bot
# Run this script on your VPS to install and configure the bot

set -e  # Exit on any error

echo "🚀 Installing Facebook Messenger Bot on VPS..."
echo "================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons."
   print_status "Please run as a regular user with sudo privileges."
   exit 1
fi

# Update system packages
print_status "Updating system packages..."
sudo apt-get update

# Install required system packages
print_status "Installing system dependencies..."
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    wget \
    gnupg \
    unzip \
    curl \
    git \
    chromium-browser \
    chromium-chromedriver \
    xvfb

# Install Docker (optional but recommended)
read -p "Do you want to install Docker? (recommended for easier deployment) [y/N]: " install_docker
if [[ $install_docker =~ ^[Yy]$ ]]; then
    print_status "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    
    print_status "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    print_warning "Please log out and log back in to use Docker without sudo."
fi

# Create application directory
APP_DIR="/opt/messenger-bot"
print_status "Creating application directory at $APP_DIR..."
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Clone repository (if not already in directory)
if [ ! -f "requirements.txt" ]; then
    print_status "Please run this script from the messenger bot directory."
    print_status "Or clone the repository first: git clone <repository-url>"
    exit 1
fi

# Copy files to application directory
print_status "Copying application files..."
cp -r . $APP_DIR/
cd $APP_DIR

# Create Python virtual environment
print_status "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create logs directory
mkdir -p logs

# Create environment file
if [ ! -f ".env" ]; then
    print_status "Creating environment configuration file..."
    cp .env.example .env
    
    print_warning "Please edit .env file with your Facebook credentials:"
    print_warning "  nano $APP_DIR/.env"
    print_warning ""
    print_warning "Required variables:"
    print_warning "  FACEBOOK_EMAIL=your_email@example.com"
    print_warning "  FACEBOOK_PASSWORD=your_password"
    print_warning ""
fi

# Install systemd service (optional)
read -p "Do you want to install systemd service for automatic startup? [y/N]: " install_service
if [[ $install_service =~ ^[Yy]$ ]]; then
    print_status "Installing systemd service..."
    
    # Update service file with correct paths
    sed "s|/opt/messenger-bot|$APP_DIR|g" messenger-bot.service > /tmp/messenger-bot.service
    sed -i "s|python3|$APP_DIR/venv/bin/python3|g" /tmp/messenger-bot.service
    
    sudo cp /tmp/messenger-bot.service /etc/systemd/system/
    sudo systemctl daemon-reload
    
    print_status "Service installed. To enable automatic startup:"
    print_status "  sudo systemctl enable messenger-bot"
    print_status "  sudo systemctl start messenger-bot"
    print_status ""
    print_status "To check status:"
    print_status "  sudo systemctl status messenger-bot"
    print_status "  sudo journalctl -u messenger-bot -f"
fi

# Set up log rotation
print_status "Setting up log rotation..."
sudo tee /etc/logrotate.d/messenger-bot > /dev/null <<EOF
$APP_DIR/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    copytruncate
}
EOF

# Create a simple status check script
cat > $APP_DIR/check_status.sh << 'EOF'
#!/bin/bash
# Simple status check script
echo "=== Messenger Bot Status ==="
echo "Bot process:"
pgrep -f "messenger_bot.py" || echo "Bot not running"
echo
echo "Recent logs:"
tail -n 5 logs/messenger_bot.log 2>/dev/null || echo "No logs found"
echo
echo "Health check:"
python3 health_check.py && echo "✅ Healthy" || echo "❌ Unhealthy"
EOF

chmod +x $APP_DIR/check_status.sh

# Final instructions
print_status "Installation completed! 🎉"
echo
print_status "Next steps:"
print_status "1. Edit configuration: nano $APP_DIR/.env"
print_status "2. Test the bot: cd $APP_DIR && source venv/bin/activate && python3 run_bot.py --headless --check-config"
print_status "3. Run the bot: python3 run_bot.py --headless --daemon"
echo
print_status "Useful commands:"
print_status "  - Check status: $APP_DIR/check_status.sh"
print_status "  - View logs: tail -f $APP_DIR/logs/messenger_bot.log"
print_status "  - Stop bot: pkill -f messenger_bot.py"
echo
if [[ $install_docker =~ ^[Yy]$ ]]; then
    print_status "Docker deployment (alternative):"
    print_status "  - cd $APP_DIR && docker-compose up -d"
    print_status "  - docker-compose logs -f"
fi
echo
print_warning "Don't forget to configure your Facebook credentials in .env file!"
print_warning "The bot will NOT work without proper Facebook email and password."