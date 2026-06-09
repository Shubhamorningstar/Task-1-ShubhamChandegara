# Smart AI Chatbot

A Python terminal chatbot with two modes:

1. **AI mode (ChatGPT)** — answers almost any question, remembers the conversation, and can fetch **live weather** when you tell it a city.
2. **Basic mode** — simple rule-based replies when no API key is set.

## How It Works

| Feature | How |
|---------|-----|
| General questions | ChatGPT API (`gpt-4o-mini` by default) |
| "What's the weather?" | ChatGPT asks which city, then calls OpenWeatherMap |
| Conversation memory | Full chat history sent to ChatGPT each turn |
| Google / live web | **Not included** — ChatGPT uses its training + weather API only |

> **Note:** The ChatGPT API does not browse Google in real time. For live weather we use [OpenWeatherMap](https://openweathermap.org/api) (free). For news, stocks, or other live data you'd need additional APIs.

## Requirements

- Python 3.9+
- OpenAI API key ([platform.openai.com](https://platform.openai.com/api-keys))
- OpenWeatherMap API key (optional, for live weather — [openweathermap.org](https://openweathermap.org/api))

## Installation

```bash
cd smart-rule-based-ai-chatbot

python3 -m venv venv
source venv/bin/activate          # macOS / Linux
# venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

## Setup API Keys

1. Copy the example env file:

   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your keys:

   ```env
   OPENAI_API_KEY=sk-your-real-key-here
   OPENWEATHER_API_KEY=your-openweather-key-here
   ```

3. **Never commit `.env`** — it is already in `.gitignore`.

### Getting API Keys

| Key | Where | Cost |
|-----|-------|------|
| `OPENAI_API_KEY` | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) | Pay per use (~$0.15/1M tokens for gpt-4o-mini) |
| `OPENWEATHER_API_KEY` | [openweathermap.org/api](https://openweathermap.org/api) | Free tier available |

## Usage

```bash
python chatbot.py
```

### Example: Weather with follow-up

```
You: what's the weather?
Bot: Which city or place would you like the weather for?

You: Mumbai
Bot: Weather in Mumbai, IN:
      • Condition: Haze
      • Temperature: 32°C (feels like 38°C)
      • Humidity: 65%
```

### Example: General questions

```
You: explain Python lists in simple terms
Bot: A Python list is like a shopping bag that holds multiple items in order...
```

Type `exit` to quit.

## Project Structure

```
smart-rule-based-ai-chatbot/
├── chatbot.py           # Main entry point and chat loop
├── ai_engine.py         # ChatGPT integration + tool calling
├── weather_service.py   # Live weather via OpenWeatherMap
├── .env.example         # Template for API keys
├── requirements.txt     # Python dependencies
└── README.md
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Still in basic mode | Check `.env` exists and `OPENAI_API_KEY` is set |
| `pip install` errors | Use `python3 -m pip install -r requirements.txt` |
| Weather not working | Add `OPENWEATHER_API_KEY` to `.env` |
| OpenAI billing error | Add payment method at platform.openai.com |
| Wrong city weather | Spell the city clearly, e.g. "Mumbai" not "mumbai india weather now" |

## License

Free to use for learning and teaching.
