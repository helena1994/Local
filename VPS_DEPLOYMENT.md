# VPS Deployment Guide

This guide will help you deploy the Facebook Messenger Bot on a Virtual Private Server (VPS) for 24/7 automated operation.

## 🚀 Quick Start

### Prerequisites

- VPS with Ubuntu 20.04+ or Debian 11+
- At least 1GB RAM and 10GB disk space
- Root or sudo access
- Facebook account credentials

### Automated Installation

1. **Clone the repository** on your VPS:
```bash
git clone <repository-url>
cd Local
```

2. **Run the installation script**:
```bash
chmod +x install_vps.sh
./install_vps.sh
```

3. **Configure credentials**:
```bash
nano /opt/messenger-bot/.env
```

4. **Test the configuration**:
```bash
cd /opt/messenger-bot
source venv/bin/activate
python3 run_bot.py --headless --check-config
```

5. **Start the bot**:
```bash
python3 run_bot.py --headless --daemon
```

## 🐳 Docker Deployment (Recommended)

### Using Docker Compose

1. **Clone and configure**:
```bash
git clone <repository-url>
cd Local
cp .env.example .env
nano .env  # Add your credentials
```

2. **Deploy with Docker Compose**:
```bash
docker-compose up -d
```

3. **Monitor logs**:
```bash
docker-compose logs -f
```

4. **Check health**:
```bash
docker-compose exec messenger-bot python3 health_check.py
```

### Manual Docker Build

```bash
# Build image
docker build -t messenger-bot .

# Run container
docker run -d \
  --name messenger-bot \
  --restart unless-stopped \
  -e FACEBOOK_EMAIL="your_email@example.com" \
  -e FACEBOOK_PASSWORD="your_password" \
  -e HEADLESS_MODE=true \
  -e DAEMON_MODE=true \
  -v ./logs:/app/logs \
  messenger-bot
```

## ⚙️ Manual Installation

### 1. System Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv \
    chromium-browser chromium-chromedriver \
    xvfb wget curl git
```

### 2. Application Setup

```bash
# Create app directory
sudo mkdir -p /opt/messenger-bot
sudo chown $USER:$USER /opt/messenger-bot

# Clone repository
git clone <repository-url> /opt/messenger-bot
cd /opt/messenger-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Create logs directory
mkdir -p logs
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

**Required environment variables:**
```env
FACEBOOK_EMAIL=your_facebook_email@example.com
FACEBOOK_PASSWORD=your_facebook_password
HEADLESS_MODE=true
DAEMON_MODE=true
CHECK_INTERVAL=300
```

### 4. Systemd Service (Optional)

```bash
# Install service
sudo cp messenger-bot.service /etc/systemd/system/
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable messenger-bot
sudo systemctl start messenger-bot

# Check status
sudo systemctl status messenger-bot
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default | VPS Recommended |
|----------|-------------|---------|-----------------|
| `FACEBOOK_EMAIL` | Facebook login email | - | Required |
| `FACEBOOK_PASSWORD` | Facebook password | - | Required |
| `AUTO_REPLY_MESSAGE` | Message to send as reply | "Terima kasih..." | Custom message |
| `HEADLESS_MODE` | Run browser without GUI | false | **true** |
| `DAEMON_MODE` | Continuous monitoring | false | **true** |
| `CHECK_INTERVAL` | Check frequency (seconds) | 300 | 300-600 |
| `MAX_RETRIES` | Max retry attempts | 3 | 3-5 |
| `RETRY_DELAY` | Delay after max retries | 60 | 60-300 |

### Command Line Options

```bash
# Run once in headless mode
python3 run_bot.py --headless

# Run in daemon mode
python3 run_bot.py --headless --daemon

# Custom check interval (10 minutes)
python3 run_bot.py --headless --daemon --interval 600

# Check configuration only
python3 run_bot.py --check-config
```

## 📊 Monitoring and Maintenance

### Health Checks

```bash
# Manual health check
python3 health_check.py

# Check bot status
./check_status.sh

# View logs
tail -f logs/messenger_bot.log
```

### Log Management

- Logs are automatically rotated daily
- Keep 7 days of logs by default
- Location: `/opt/messenger-bot/logs/`

### Common Commands

```bash
# Start bot
cd /opt/messenger-bot && source venv/bin/activate
python3 run_bot.py --headless --daemon

# Stop bot
pkill -f messenger_bot.py

# Restart systemd service
sudo systemctl restart messenger-bot

# View service logs
sudo journalctl -u messenger-bot -f

# Docker commands
docker-compose restart
docker-compose logs -f
```

## 🔒 Security Considerations

### 1. Facebook Account Security

- **Use app-specific password** if 2FA is enabled
- **Monitor login notifications** from Facebook
- **Consider using a dedicated Facebook account** for the bot

### 2. VPS Security

```bash
# Update system regularly
sudo apt update && sudo apt upgrade -y

# Configure firewall (if needed)
sudo ufw enable
sudo ufw allow ssh

# Secure credentials
chmod 600 /opt/messenger-bot/.env
```

### 3. Resource Limits

The bot includes resource limits:
- Memory: 1GB max
- CPU: 50% max
- Automatic restart on failure

## 🐛 Troubleshooting

### Common Issues

**1. Chrome/ChromeDriver errors:**
```bash
# Reinstall Chrome
sudo apt reinstall chromium-browser chromium-chromedriver

# Clear Chrome cache
rm -rf ~/.cache/chromium
```

**2. Facebook login issues:**
- Check if 2FA is enabled (use app password)
- Verify credentials in `.env` file
- Check Facebook security notifications

**3. Memory issues:**
```bash
# Check memory usage
free -h

# Add swap if needed
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

**4. Permission errors:**
```bash
# Fix ownership
sudo chown -R $USER:$USER /opt/messenger-bot

# Fix permissions
chmod +x /opt/messenger-bot/*.sh
```

### Debug Mode

```bash
# Run with verbose logging
PYTHONPATH=src python3 -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from messenger_bot import MessengerBot
bot = MessengerBot()
bot.run_bot()
"
```

## 🔄 Updates and Maintenance

### Updating the Bot

```bash
cd /opt/messenger-bot
git pull origin main
source venv/bin/activate
pip install -r requirements.txt

# Restart service
sudo systemctl restart messenger-bot
```

### Backup Configuration

```bash
# Backup configuration
cp .env .env.backup.$(date +%Y%m%d)

# Backup logs
tar -czf logs_backup_$(date +%Y%m%d).tar.gz logs/
```

## 📈 Performance Tips

### VPS Optimization

1. **Use SSD storage** for better I/O performance
2. **Enable swap** for memory stability
3. **Monitor resource usage** regularly
4. **Use headless mode** to save memory
5. **Adjust check interval** based on needs

### Bot Optimization

```env
# Longer intervals for less frequent checking
CHECK_INTERVAL=600  # 10 minutes

# Reduce timeouts for faster failures
IMPLICIT_WAIT=5
PAGE_LOAD_TIMEOUT=20
```

## 📞 Support

If you encounter issues:

1. Check the logs: `tail -f logs/messenger_bot.log`
2. Run health check: `python3 health_check.py`
3. Verify configuration: `python3 run_bot.py --check-config`
4. Check system resources: `htop` or `free -h`

For additional help, please create an issue in the repository.