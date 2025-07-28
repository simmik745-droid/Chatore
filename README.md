# 🍽️ Chatore Discord Bot

A sophisticated Discord chatbot powered by Google's Gemini 2.5 Flash AI model with advanced personality customization, comprehensive memory system, tier-based features, and beautiful interactive interfaces.

## ✨ Key Features

### 🤖 AI-Powered Intelligence
- **Natural Conversations**: Powered by Gemini 2.5 Flash with 5 API keys for reliability
- **Context Awareness**: Remembers conversation history and user preferences
- **Bilingual Support**: Seamless English and Hinglish communication
- **Smart Responses**: Length-controlled answers (short/medium/long) for `/ask` command

### 🧠 Advanced Memory System
- **Permanent User Memories**: Store personal information that never gets deleted
- **Conversation Context**: Dynamic context limits (12-25 messages based on tier)
- **Memory Management**: Add, edit, delete specific memories with interactive buttons
- **Welcome Onboarding**: Systematic new user setup for better personalization

### 🎨 Premium Personality System
- **Custom Personality**: Premium users can fully customize bot behavior
- **Personality Presets**: Save and switch between 5 different personality configurations
- **Trait Customization**: Modify personality traits, humor style, speaking patterns
- **Behavior Control**: Adjust age, interests, quirks, and special characteristics

### 📊 Tier System
- **Free Tier**: 40 requests/12h, 12 message context, standard personality
- **Premium Tier**: 200 requests/12h, 25 message context, full personality customization
- **Usage Tracking**: Real-time monitoring with visual progress bars
- **Subscription Management**: Easy upgrade system with owner-managed payments

### 🎯 Interactive Features
- **Modern Help System**: Dropdown navigation with paginated command lists
- **Button Interfaces**: Interactive memory management, personality customization
- **Timeout Handling**: 30-second timeouts with disabled buttons for better UX
- **Welcome System**: Step-by-step onboarding for new users

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
chatore-bot/
├── main.py                     # Entry point
├── bot/
│   ├── __init__.py
│   ├── luna_bot.py            # Main bot class with AI integration
│   ├── memory/
│   │   ├── __init__.py
│   │   └── memory_manager.py  # Advanced memory & context management
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── tier_manager.py    # Subscription & rate limiting system
│   │   ├── personality_manager.py  # Premium personality system
│   │   └── emotion_detector.py     # Mood & emotion analysis
│   └── commands/
│       ├── __init__.py
│       ├── chat_commands.py        # Memory & conversation commands
│       ├── utility_commands.py     # Bot info & utility commands
│       ├── help_commands.py        # Interactive help system
│       ├── personality_commands.py # Premium personality customization
│       ├── subscription_commands.py # Tier management & subscriptions
│       ├── welcome_system.py       # New user onboarding
│       ├── language_commands.py    # Language switching system
│       └── owner_commands.py       # Owner-only administrative commands
├── readings/                       # Documentation & summaries
├── requirements.txt
├── setup.py
├── .env                           # Environment variables
├── bot_memory.json               # Persistent memory storage
└── user_tiers.json              # User subscription data
```

## 🛠️ Commands

### 💬 Memory & Chat Commands
- `/memory <text>` - Store permanent memory about yourself
- `/memories` - Interactive memory management (view, add, edit, delete)
- `/ask <question> [length]` - Ask formal questions with length control (short/medium/long)
- `/forget` - Clear all your data and start fresh

### 🎨 Personality System (Premium)
- `/personality` - View and customize bot personality
- **Customization Options:**
  - Personality traits and behavior
  - Speaking style and humor type
  - Interests and knowledge areas
  - Age/maturity level and quirks
- **Preset Management:**
  - Save up to 5 personality presets
  - Quick switching between personalities
  - Edit and delete existing presets

### 📊 Subscription & Tiers
- `/plan` - Check your current subscription and usage
- `/subscribe` - Upgrade to Premium for enhanced features
- `/activity` - View your activity status and memory cleanup info

### 🔧 Utility Commands
- `/help` - Modern dropdown-based help system
- `/language` - Switch between English and Hinglish
- `/langstatus` - Check your current language setting
- `/ping` - Check bot latency and connection status
- `/stats` - View comprehensive bot statistics
- `/owner` - Meet Abhinav Anand - the creator
- `/mood` - Check Chatore's current emotional state
- `/invite` - Get bot invite link for other servers

### 🔐 Owner Commands
- `/grant_premium <user> [months]` - Grant premium subscription
- `/tier_stats` - View tier distribution statistics
- `/apistatus` - Check API key rotation status

### 💬 Natural Conversations
- **Mention**: `@Chatore` for natural chat in servers
- **Direct Messages**: Full conversation support
- **Context Awareness**: Remembers recent messages (12-25 based on tier)
- **Bilingual**: Automatic language detection and response
- **Welcome System**: New users get guided onboarding

## 🧠 Advanced Memory System

### Permanent User Memories
- **Storage**: Set with `/memory` command, never auto-deleted
- **Management**: Interactive buttons to add, edit, delete specific memories
- **Context**: Used for long-term personalization and user understanding
- **Welcome Integration**: Systematic collection during onboarding

### Dynamic Conversation Context
- **Tier-Based Limits**: 12 messages (Free) / 25 messages (Premium)
- **Smart Context**: Recent conversation history for natural flow
- **Memory Integration**: Combines with permanent memories for rich context
- **Auto-Cleanup**: Inactive users cleaned up after 30 days

### Welcome Onboarding System
- **New User Detection**: Automatic welcome for first-time users
- **Step-by-Step Setup**: Guided collection of name, age, hobbies, preferences
- **Skip Options**: Users can skip any step they're uncomfortable with
- **Bilingual Support**: Welcome process adapts to user's language preference
- **Completion Tracking**: Ensures users complete setup before accessing advanced features

## 🎨 Premium Personality System

### Personality Customization
- **Full Control**: Customize traits, humor style, speaking patterns
- **Age & Maturity**: Set bot's apparent age and maturity level
- **Interests**: Define areas of knowledge and passion
- **Quirks**: Add unique catchphrases and behaviors

### Preset Management
- **5 Preset Slots**: Save different personality configurations
- **Quick Switching**: Instantly change between saved personalities
- **Preset Editing**: Modify existing presets without starting over
- **Backup System**: Presets are safely stored and persistent

### Personality Features
- **Trait System**: Funny, sarcastic, supportive, energetic, calm, witty
- **Speaking Styles**: Casual, formal, street slang, professional
- **Humor Types**: Sarcastic, wholesome, dark humor, punny, dry wit
- **Custom Quirks**: Personal catchphrases and unique behaviors

## 📊 Tier System & Subscriptions

### Free Tier Features
- 40 requests per 12 hours
- 12 message conversation context
- Basic AI responses with standard personality
- Full memory system access
- All utility commands
- Community support

### Premium Tier Features ($1.50/month)
- 200 requests per 12 hours (5x more)
- 25 message conversation context (2x more)
- **Full personality customization system**
- **5 personality preset slots**
- Priority AI response processing
- Enhanced memory system
- Premium support
- Early access to new features

### Usage Tracking
- **Real-time Monitoring**: Visual progress bars for usage
- **Reset Timers**: Clear indication of when limits reset
- **Statistics**: Total requests, member since date, activity status
- **Transparent Limits**: Always know your current usage status

## 🔧 Development & Architecture

### Core Systems

#### Memory Management (`bot/memory/memory_manager.py`)
- **Persistent Storage**: JSON-based storage with async operations
- **Context Generation**: Smart context building for AI responses
- **User Tracking**: Activity monitoring and cleanup systems
- **Welcome Integration**: New user detection and setup tracking
- **Language Support**: Per-user language preference storage

#### Tier Management (`bot/utils/tier_manager.py`)
- **Subscription Handling**: Premium tier management and expiration
- **Rate Limiting**: Request tracking with 12-hour windows
- **Usage Statistics**: Comprehensive usage analytics
- **Tier Configurations**: Flexible tier system with easy modifications

#### Personality System (`bot/utils/personality_manager.py`)
- **Custom Personalities**: Full personality customization for premium users
- **Preset Management**: Save/load/delete personality configurations
- **Trait System**: Comprehensive personality trait management
- **Persistence**: Secure storage of personality data

#### AI Integration (`bot/luna_bot.py`)
- **Multi-API Support**: 5 Gemini API keys with automatic rotation
- **Context Building**: Smart context generation from memory and conversation
- **Error Handling**: Robust fallback systems for API failures
- **Response Processing**: Length control and formatting

### Command Structure

#### Chat Commands (`bot/commands/chat_commands.py`)
- Memory management with interactive interfaces
- Ask command with length control and smart truncation
- Multi-embed support for long responses
- Welcome system integration

#### Personality Commands (`bot/commands/personality_commands.py`)
- Step-by-step personality customization
- Modal-based input collection
- Preset management interfaces
- Premium feature validation

#### Subscription Commands (`bot/commands/subscription_commands.py`)
- Tier status display with usage visualization
- Subscription management and upgrade flows
- Owner tools for tier administration
- Feature comparison displays

#### Welcome System (`bot/commands/welcome_system.py`)
- Guided onboarding for new users
- Step-by-step data collection
- Skip options and validation
- Bilingual support throughout

### Adding New Features

1. **New Commands**: Add to appropriate command file based on category
2. **Memory Features**: Extend `MemoryManager` class
3. **Tier Features**: Update `TierManager` configurations
4. **Personality Features**: Extend `PersonalityManager` system
5. **Help System**: Update `help_commands.py` with new command documentation

## 📋 Requirements & Setup

### System Requirements
- Python 3.8+
- Discord Bot Token
- Google Gemini API Keys (5 recommended for reliability)

### Dependencies
- discord.py 2.3.2+ (Discord API integration)
- google-generativeai 0.3.2+ (Gemini AI model)
- python-dotenv 1.0.0+ (Environment variable management)
- aiofiles 23.2.1+ (Async file operations)

### Environment Configuration
Create a `.env` file with:
```env
DISCORD_TOKEN=your_discord_bot_token
GEMINI_API_KEY_1=your_first_gemini_key
GEMINI_API_KEY_2=your_second_gemini_key
GEMINI_API_KEY_3=your_third_gemini_key
GEMINI_API_KEY_4=your_fourth_gemini_key
GEMINI_API_KEY_5=your_fifth_gemini_key
```

### Installation Steps
1. **Clone Repository**: `git clone <repository-url>`
2. **Install Dependencies**: `python setup.py` or `pip install -r requirements.txt`
3. **Configure Environment**: Set up `.env` file with tokens and API keys
4. **Run Bot**: `python main.py`
5. **Invite Bot**: Use Discord Developer Portal to invite to servers

## 🌟 Advanced Features

### Modern Interactive Interfaces
- **Dropdown Navigation**: Modern help system with categorized commands
- **Button Interactions**: Memory management, personality customization
- **Modal Forms**: Step-by-step data collection with validation
- **Timeout Handling**: 30-second timeouts with graceful degradation
- **Visual Feedback**: Progress bars, status indicators, confirmation messages

### AI Response Intelligence
- **Length Control**: Short (50-100 words), Medium (400-500 words), Long (800-1000 words)
- **Smart Truncation**: Sentence-aware truncation to prevent mid-sentence cuts
- **Multi-Message Support**: Automatic splitting for very long responses
- **Context Awareness**: Combines user memories with conversation history
- **Bilingual Processing**: Seamless English/Hinglish understanding and response

### Robust Data Management
- **Async Operations**: Non-blocking file I/O for better performance
- **Data Integrity**: Validation and error handling throughout
- **Backup Systems**: Redundant storage and recovery mechanisms
- **Statistics Tracking**: Comprehensive usage and performance metrics
- **Auto-Cleanup**: Inactive user data cleanup after 30 days

### Premium Experience
- **Personalization**: Complete personality customization system
- **Preset System**: Save and switch between 5 different personalities
- **Priority Processing**: Faster response times for premium users
- **Enhanced Limits**: 5x more requests, 2x more context
- **Exclusive Features**: Early access to new functionality

### Security & Privacy
- **User Isolation**: Each user's data is completely separate
- **Permission Checks**: Strict validation for interactive elements
- **Rate Limiting**: Prevents abuse with tier-based limits
- **Data Cleanup**: Automatic removal of inactive user data
- **Owner Controls**: Administrative commands for tier management

## 🚀 Recent Updates

### Version 2.0 - Major Feature Release
- **Premium Personality System**: Full personality customization with 5 preset slots
- **Welcome Onboarding**: Systematic new user setup process
- **Enhanced Memory System**: Interactive memory management with edit/delete
- **Improved Ask Command**: Length control (short/medium/long) with smart truncation
- **Modern Help System**: Dropdown navigation with paginated commands
- **Tier System**: Free and Premium tiers with usage tracking
- **Bilingual Support**: Seamless English and Hinglish communication
- **Multi-API Reliability**: 5 Gemini API keys for better uptime

### Recent Improvements
- Welcome setup redirect for memory and personality commands
- Smart response truncation to prevent cut-offs
- Enhanced premium feature marketing and value proposition
- Timeout handling for all interactive elements
- Comprehensive usage statistics and monitoring

## 🤝 Contributing

### Development Guidelines
1. **Fork Repository**: Create your own fork for development
2. **Feature Branches**: Create branches for specific features
3. **Code Quality**: Follow existing patterns and add comments
4. **Testing**: Test all interactive elements and edge cases
5. **Documentation**: Update README and add summary files in `readings/`
6. **Pull Request**: Submit with clear description of changes

### Areas for Contribution
- **New Personality Traits**: Expand personality customization options
- **Language Support**: Add more languages beyond English/Hinglish
- **Interactive Features**: Create new button/modal interfaces
- **AI Improvements**: Enhance context building and response quality
- **Performance**: Optimize database operations and memory usage

## 📊 Statistics & Performance

### Current Capabilities
- **Multi-User Support**: Handles unlimited concurrent users
- **Response Time**: < 3 seconds average response time
- **Uptime**: 99%+ uptime with multi-API redundancy
- **Memory Efficiency**: Automatic cleanup of inactive users
- **Scalability**: Tier system supports growth and monetization

### Usage Metrics
- **Free Tier**: 40 requests per 12 hours per user
- **Premium Tier**: 200 requests per 12 hours per user
- **Context Limits**: 12-25 messages based on tier
- **Memory Storage**: Unlimited permanent memories per user
- **Personality Presets**: 5 slots for premium users

### Credits
- **Creator**: Abhinav Anand
- **AI Model**: Google Gemini 2.5 Flash
- **Framework**: Discord.py
- **Language**: Python 3.8+

### Acknowledgments
- Google for Gemini AI API
- Discord for excellent bot platform
- Python community for amazing libraries
- Beta testers for feedback and suggestions

---

**Made with 💙 by Abhinav Anand**  
*Chatore - Your AI companion that grows with you*
