# Local

This repository contains multiple bot implementations:

## JavaScript/Node.js Telegram Bot
- Located in `src/` directory
- Integration with Google Sheets
- Run with: `npm start`

## Python Messenger Bot

A Selenium-based Facebook Messenger bot with sentiment analysis and conversation memory.

### Features
1. **Message Reading**: Automatically reads messages from Facebook Messenger using Selenium
2. **Message Replying**: Responds to messages with sentiment-aware replies
3. **Memory**: Stores conversation history in SQLite database
4. **Emotional Intelligence**: Analyzes sentiment using TextBlob and provides appropriate responses

### Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Download TextBlob corpora:
```bash
python -c "import nltk; nltk.download('punkt')"
```

### Usage

1. **Basic Bot Setup**:
```python
from messenger_bot import MessengerBot

bot = MessengerBot(headless=False)  # Set True for headless mode
bot.setup_driver()
```

2. **Login and Monitor**:
```python
# Login to Facebook
bot.login_to_messenger("your_email@example.com", "your_password")

# Monitor a specific conversation
bot.monitor_and_respond("Friend Name")
```

3. **Manual Testing**:
```python
# Test sentiment analysis
from sentiment_analyzer import SentimentAnalyzer
analyzer = SentimentAnalyzer()
response, score, label = analyzer.analyze_and_respond("I'm having a great day!")
print(f"Response: {response}, Sentiment: {label} ({score})")
```

### Components

- `messenger_bot.py`: Main bot implementation with Selenium automation
- `database.py`: SQLite database manager for conversation memory
- `sentiment_analyzer.py`: TextBlob-based sentiment analysis
- `config.py`: Configuration settings
- `test_bot.py`: Unit tests for core components

### Configuration

Edit `config.py` to customize:
- Response templates for different sentiments
- Database settings
- Selenium timeouts and options
- Sentiment analysis thresholds

### Testing

Run tests with:
```bash
python test_bot.py
```

### Language Support

**Note**: TextBlob sentiment analysis works best with English text. For Indonesian or other languages, consider using language-specific sentiment analysis libraries like:
- `sastrawi` for Indonesian text processing
- `polyglot` for multilingual sentiment analysis
- Or translation services to convert to English first

### Security Notes

⚠️ **Important**: Never commit your Facebook credentials to version control. Use environment variables or secure configuration files for sensitive data.

### Requirements

- Python 3.7+
- Chrome/Chromium browser
- Valid Facebook account
- Internet connection