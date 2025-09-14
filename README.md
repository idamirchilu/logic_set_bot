# Logic Set Bot

A Telegram bot for learning mathematical logic and set theory, powered by Ollama (free LLM) and SQLite.

## Features

- 🤖 **Intelligent Q&A** - Ask questions about mathematical logic and set theory
- 📚 **Educational Content** - Learn propositional logic, Boolean algebra, and set operations
- 🎯 **Interactive Exercises** - Practice with generated problems and get instant feedback
- 📊 **Progress Tracking** - Monitor your learning progress and achievements
- 🔄 **Caching System** - Fast responses with intelligent caching
- 🌐 **Persian Language** - Full support for Persian/Farsi interface

## Tech Stack

- **Backend**: Python 3.11+
- **Bot Framework**: python-telegram-bot
- **Database**: SQLite (with aiosqlite)
- **LLM**: Ollama (free, local)
- **Math Engine**: SymPy
- **Visualization**: Matplotlib + Pillow
- **Caching**: Built-in with cachetools

## Quick Start

### Prerequisites

1. **Python 3.11+**
2. **Telegram Bot Token** - Get from [@BotFather](https://t.me/botfather)
3. **Ollama** - Free LLM server (optional, has fallback)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd logic_set_bot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup Ollama (optional)**
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Start Ollama
   ollama serve
   
   # Pull a model (in another terminal)
   ollama pull llama3.2
   
   # Or use the setup script
   python scripts/setup_ollama.py
   ```

5. **Setup SQLite database**
   ```bash
   python scripts/setup_sqlite.py
   ```

6. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your bot token
   ```

7. **Run the bot**
   ```bash
   python run_bot.py
   ```

## Configuration

### Environment Variables

Create a `.env` file with:

```env
# Required
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Ollama (optional)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
OLLAMA_MAX_TOKENS=800
OLLAMA_TEMPERATURE=0.3

# Database (SQLite)
DATABASE_URL=sqlite+aiosqlite:///./logic_bot.db
DATABASE_DRIVER=aiosqlite

# Optional
DEBUG=False
LOG_LEVEL=INFO
CACHE_TTL=300
CACHE_MAXSIZE=100
```

### Database Options

The bot uses SQLite by default, which requires no additional setup. The database file will be created automatically at `./logic_bot.db`.

## Docker Setup

### Using Docker Compose

1. **Create `.env` file** with your bot token
2. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

### Manual Docker

1. **Build the image**
   ```bash
   docker build -t logic-set-bot .
   ```

2. **Run the container**
   ```bash
   docker run -d \
     --name logic-bot \
     -e TELEGRAM_BOT_TOKEN=your_token \
     -v $(pwd)/data:/app/data \
     logic-set-bot
   ```

## Usage

### Bot Commands

- `/start` - Start the bot and show main menu
- `/help` - Show help information
- `/about` - Show bot information
- `/progress` - View your learning progress

### Main Features

1. **Ask Questions** - Type any question about logic or set theory
2. **Practice Exercises** - Generate and solve practice problems
3. **Learn Concepts** - Get explanations of mathematical concepts
4. **Track Progress** - Monitor your learning journey

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
│   ├── models/        # Database models
│   ├── services/      # Business logic services
│   ├── utils/         # Utility functions
│   ├── config.py      # Configuration
│   ├── database.py    # Database manager
│   └── main.py        # Application entry point
├── scripts/           # Setup and utility scripts
├── data/              # SQLite database (created automatically)
├── docker-compose.yml # Docker configuration
├── Dockerfile         # Docker image definition
└── requirements.txt   # Python dependencies
```

## Development

### Setup Development Environment

1. **Install development dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run database migrations**
   ```bash
   python scripts/init_db.py
   ```

3. **Run tests**
   ```bash
   python scripts/test_ollama.py
   python scripts/setup_sqlite.py
   ```

### Adding New Features

1. **Database Models** - Add to `app/models/`
2. **Bot Handlers** - Add to `app/bot/handlers.py`
3. **Services** - Add to `app/services/`
4. **Utilities** - Add to `app/utils/`

## Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check bot token in `.env`
   - Verify bot is running
   - Check logs for errors

2. **Database errors**
   - Run `python scripts/setup_sqlite.py`
   - Check file permissions
   - Verify database file exists

3. **Ollama not working**
   - Check if Ollama is running: `curl http://localhost:11434/api/tags`
   - Verify model is pulled: `ollama list`
   - Bot will use fallback responses if Ollama is unavailable

### Logs

Check logs for debugging:
```bash
# View logs
tail -f logs/bot.log

# Or run with debug mode
DEBUG=True python run_bot.py
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
- Review the migration guides

