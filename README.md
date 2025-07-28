# 🍽️ Chatore Discord Bot

A sophisticated Discord chatbot powered by Google's Gemini 2.5 Flash AI model with personality, memory, and beautiful interactive features.

## ✨ Features

- **AI-Powered Conversations**: Natural chat using Gemini 2.5 Flash
- **Memory System**: Permanent user memories + conversation context (last 10 messages)
- **Interactive Help**: Beautiful button-based help system
- **Private Questions**: `!ask` command sends responses via DM
- **Beautiful Embeds**: All responses use Discord embeds with proper formatting
- **Personality**: Friendly, witty, and engaging conversation style

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   python setup.py
   ```

2. **Configure environment:**
   - Ensure your `.env` file has:
     ```
     DISCORD_TOKEN=your_discord_bot_token
     GEMINI_API_KEY=your_gemini_api_key
     ```

3. **Run the bot:**
   ```bash
   python main.py
   ```

## 📁 Project Structure

```
luna-bot/
├── main.py                 # Entry point
├── bot/
│   ├── __init__.py
│   ├── luna_bot.py         # Main bot class
│   ├── memory/
│   │   ├── __init__.py
│   │   └── memory_manager.py   # Memory management
│   └── commands/
│       ├── __init__.py
│       ├── chat_commands.py    # Memory & conversation commands
│       ├── utility_commands.py # Bot info & utility commands
│       └── help_commands.py    # Interactive help system
├── requirements.txt
├── setup.py
├── .env                    # Environment variables
└── bot_memory.json        # Persistent memory storage
```

## 🛠️ Commands

### 💬 Chat Commands (Slash Commands)
- `/memory <text>` - Store permanent memory about yourself
- `/memories` - View what Chatore remembers about you
- `/ask <question>` - Ask formal questions (private DM response)
- `/forget` - Clear all your data

### 🔧 Utility Commands (Slash Commands)
- `/help` - Interactive help system with buttons
- `/personality` - Learn about Chatore's personality
- `/language` - Switch between English and Hinglish
- `/langstatus` - Check your current language setting
- `/ping` - Check bot latency
- `/stats` - View bot statistics
- `/msgcount` - Debug message count info
- `/activity` - Check your activity status
- `/apistatus` - Check API key status
- `/owner` - Meet Abhinav Anand - the owner and creator
- `/mood` - Check Chatore's current mood and emotional state

### 💬 Natural Chat
- Mention `@Chatore` or DM for natural conversations
- Chatore remembers context and responds with personality
- Both prefix commands (!) and slash commands (/) supported

## 🧠 Memory System

**Permanent Memories:**
- Set with `/memory` command
- Never automatically deleted
- Used for long-term user context

**Conversation Context:**
- Automatically stores last 10 messages per user
- Provides recent conversation context
- Helps maintain natural flow

## 🔧 Development

### Adding New Commands

1. **Chat Commands**: Add to `bot/commands/chat_commands.py`
2. **Utility Commands**: Add to `bot/commands/utility_commands.py`
3. **Help System**: Update `bot/commands/help_commands.py`

### Memory Management

The `MemoryManager` class handles:
- Persistent storage in `bot_memory.json`
- User memory management
- Conversation history tracking
- Context generation for AI

### Bot Configuration

Main bot settings in `bot/luna_bot.py`:
- Personality configuration
- AI model settings
- Event handlers
- Error handling

## 📋 Requirements

- Python 3.8+
- discord.py 2.3.2+
- google-generativeai 0.3.2+
- python-dotenv 1.0.0+
- aiofiles 23.2.1+

## 🌟 Features in Detail

### Interactive Help System
- Button-based navigation
- Multiple categories
- Timeout handling
- Beautiful embeds

### AI Integration
- Gemini 2.5 Flash model
- Context-aware responses
- Personality-driven conversations
- Error handling and fallbacks

### Memory Persistence
- JSON-based storage
- Async file operations
- Data integrity checks
- Statistics tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source. Feel free to use and modify as needed.

---

Made with 💙 by Luna Bot Team
