# Local - Multi-Bot Repository

This repository contains both JavaScript Telegram bot and Python Messenger bot implementations.

## 🤖 Python Messenger Bot

An automated Messenger bot built with Selenium in Python, featuring sentiment analysis and SQLite database storage.

### ✨ Features

- **Selenium-based Messenger automation** - Automated web interactions with Facebook Messenger
- **Auto-login functionality** - Secure automated login with credential management
- **Sentiment analysis** - Real-time message sentiment analysis using TextBlob
- **SQLite database storage** - Persistent storage for messages and analytics
- **Auto-reply system** - Intelligent responses based on sentiment analysis
- **PEP 8 compliant** - Clean, readable Python code following best practices

### 📁 Project Structure

```
├── main.py                          # Main bot entry point
├── config/                          # Configuration files
│   ├── __init__.py
│   ├── settings.py                  # Bot settings and configuration
│   └── credentials_template.py      # Credentials template
├── database/                        # SQLite database storage
├── scripts/                         # Core bot modules
│   ├── __init__.py
│   ├── messenger_automation.py      # Main bot automation
│   ├── auto_login.py               # Login functionality
│   ├── sentiment_analysis.py       # Sentiment analysis module
│   └── database_manager.py         # Database operations
├── requirements.txt                 # Python dependencies
└── README.md                       # This file
```

### 🚀 Quick Start

#### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Download required NLTK data for sentiment analysis
python -c "import nltk; nltk.download('punkt'); nltk.download('vader_lexicon')"
```

#### 2. Configure Credentials

```bash
# Copy credentials template
cp config/credentials_template.py config/credentials.py

# Edit credentials.py with your Messenger login details
# DO NOT commit credentials.py to version control!
```

#### 3. Configure Settings

Edit `config/settings.py` to customize bot behavior:

- `headless_mode`: Run browser in headless mode (default: True)
- `auto_reply`: Enable automatic responses (default: True)
- `sentiment_analysis`: Enable sentiment analysis (default: True)
- `check_interval`: Message checking interval in seconds (default: 30)

#### 4. Run the Bot

```bash
python main.py
```

### 📊 Database Schema

The bot uses SQLite to store message data:

```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT NOT NULL,
    recipient TEXT NOT NULL,
    message TEXT NOT NULL,
    sentiment REAL,
    sentiment_label TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT 0,
    metadata TEXT
);
```

### 🔧 Configuration Options

#### Environment Variables

Set these environment variables to customize bot behavior:

```bash
export HEADLESS_MODE=true           # Run browser in headless mode
export WAIT_TIMEOUT=10              # Selenium wait timeout
export CHECK_INTERVAL=30            # Message check interval
export AUTO_REPLY=true              # Enable auto-replies
export SENTIMENT_ANALYSIS=true     # Enable sentiment analysis
export LOG_LEVEL=INFO               # Logging level
```

#### Credentials Configuration

Edit `config/credentials.py`:

```python
MESSENGER_CREDENTIALS = {
    'email': 'your_email@example.com',
    'password': 'your_secure_password'
}
```

### 🧠 Sentiment Analysis

The bot analyzes incoming messages and provides appropriate responses:

- **Positive messages** → Encouraging responses
- **Negative messages** → Supportive responses  
- **Neutral messages** → Standard acknowledgments

### 🛡️ Security Notes

- Never commit `config/credentials.py` to version control
- Use strong, unique passwords for Messenger accounts
- Consider using environment variables for sensitive data
- Run in headless mode on production servers

### 🔍 Monitoring and Logs

- Bot activities are logged to `messenger_bot.log`
- Database statistics available via `DatabaseManager.get_statistics()`
- Message history stored in SQLite database

### 🧪 Testing

```bash
# Install development dependencies
pip install pytest black flake8

# Run code formatting
black .

# Run linting
flake8 .

# Run tests (when implemented)
pytest
```

### ⚠️ Troubleshooting

#### Common Issues

1. **Login fails**: Check credentials and 2FA settings
2. **Chrome driver issues**: Install ChromeDriver or use webdriver-manager
3. **Selenium timeouts**: Increase `WAIT_TIMEOUT` environment variable
4. **TextBlob errors**: Run `python -c "import nltk; nltk.download('punkt')"`

#### Browser Requirements

- Chrome browser must be installed
- ChromeDriver compatible with your Chrome version
- Or use webdriver-manager for automatic driver management

### 📈 Performance Tips

- Use headless mode for better performance
- Adjust check intervals based on message volume
- Regular database cleanup for large message volumes
- Monitor memory usage for long-running instances

---

## 📱 JavaScript Telegram Bot

The repository also includes a JavaScript Telegram bot implementation in the `src/` directory.

### Features
- Telegram Bot API integration
- Google Sheets integration
- Read/write data commands

### Usage
```bash
npm start
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Follow PEP 8 for Python code
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is open source. Please check individual files for specific licensing information.

---

**Note**: This bot is for educational and automation purposes. Please ensure compliance with Messenger's Terms of Service and applicable laws when using automated tools.