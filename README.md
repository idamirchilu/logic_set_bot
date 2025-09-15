# Logic Set Bot

A Telegram bot for learning mathematical logic and set theory, powered by OpenRouter (free/low-cost LLM) and stateless operation.

## Features

- 🤖 **Intelligent Q&A** - Ask questions about mathematical logic and set theory
- 📚 **Educational Content** - Learn propositional logic, Boolean algebra, and set operations
- 🎯 **Interactive Exercises** - Practice with generated problems and get instant feedback
- 🔄 **Caching System** - Fast responses with intelligent caching
- 🌐 **Persian Language** - Full support for Persian/Farsi interface

## Tech Stack

- **Backend**: Python 3.11+
- **Bot Framework**: python-telegram-bot
- **LLM**: OpenRouter (cloud, free/low-cost)
- **Math Engine**: SymPy
- **Visualization**: Matplotlib + Pillow
- **Caching**: Built-in with cachetools

## Quick Start

### Prerequisites

1. **Python 3.11+**
2. **Telegram Bot Token** - Get from [@BotFather](https://t.me/botfather)
3. **OpenRouter API Key** - Get from [OpenRouter](https://openrouter.ai/)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd logic_set_bot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install httpx
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your bot token and OpenRouter API key
   ```

5. **Run the bot**
   ```bash
   python run_bot.py
   ```

## Configuration

### Environment Variables

Create a `.env` file with:

```env
# Required
TELEGRAM_BOT_TOKEN=your_bot_token_here
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Optional
DEBUG=False
LOG_LEVEL=INFO
CACHE_TTL=300
CACHE_MAXSIZE=100
```

## Usage

### Bot Commands

- `/start` - Start the bot and show main menu
- `/help` - Show help information
- `/about` - Show bot information

### Main Features

1. **Ask Questions** - Type any question about logic or set theory
2. **Practice Exercises** - Generate and solve practice problems
3. **Learn Concepts** - Get explanations of mathematical concepts

### Example Interactions

```
User: ساده کن (p ∧ q) ∨ (p ∧ ¬q)
Bot: این عبارت را می‌توان به صورت زیر ساده کرد:
     p ∧ q ∨ p ∧ ¬q = p ∧ (q ∨ ¬q) = p ∧ T = p

User: جدول درستی برای p → q
Bot: [Generates truth table]

User: محاسبه کن A ∪ B که A={1,2}, B={2,3}
Bot: A ∪ B = {1, 2, 3}
```

## Project Structure

```
logic_set_bot/
├── app/
│   ├── bot/           # Bot handlers and keyboards
│   ├── services/      # Business logic services
│   ├── utils/         # Utility functions
│   ├── config.py      # Configuration
│   └── main.py        # Application entry point
├── scripts/           # Setup and utility scripts
├── docker-compose.yml # Docker configuration
├── Dockerfile         # Docker image definition
└── requirements.txt   # Python dependencies
```

## Development

### Setup Development Environment

1. **Install development dependencies**
   ```bash
   pip install -r requirements.txt
   pip install httpx
   ```

2. **Run tests**
   ```bash
   python scripts/test_sqlite_simple.py
   ```

### Adding New Features

1. **Bot Handlers** - Add to `app/bot/handlers.py`
2. **Services** - Add to `app/services/`
3. **Utilities** - Add to `app/utils/`

## Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check bot token and OpenRouter API key in `.env`
   - Verify bot is running
   - Check logs for errors

2. **LLM not working**
   - Check your internet connection
   - Bot will use fallback responses if LLM is unavailable

### Logs

Check logs for debugging:
```bash
# View logs
# (Add your logging setup here)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section

