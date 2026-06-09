"""
KrishnaBot AI — Professional Rule-Based AI Assistant
A single-file terminal chatbot with typing animation, weather, Ollama AI, and more.
Uses if-elif-else logic for core rule-based responses.
"""

import json
import os
import random
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

# ---------------------------------------------------------------------------
# Optional: load API keys from .env file (pip install python-dotenv)
# ---------------------------------------------------------------------------
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BOT_NAME = "KrishnaBot AI"
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
TYPING_SPEED = 0.02  # seconds per character for typing animation


# ---------------------------------------------------------------------------
# Quote & joke databases
# ---------------------------------------------------------------------------
MOTIVATIONAL_QUOTES = [
    "The only way to do great work is to love what you do. — Steve Jobs 💪",
    "Believe you can and you're halfway there. — Theodore Roosevelt 🌟",
    "Success is not final, failure is not fatal: it is the courage to continue that counts. — Churchill 🏆",
    "Don't watch the clock; do what it does. Keep going. — Sam Levenson ⏰",
    "The future belongs to those who believe in the beauty of their dreams. — Eleanor Roosevelt ✨",
    "It always seems impossible until it's done. — Nelson Mandela 🚀",
    "Your limitation—it's only your imagination. Push yourself! 💫",
]

KRISHNA_QUOTES = [
    "Whenever there is a decline in righteousness, I manifest myself. — Bhagavad Gita 4.7 🙏",
    "Set thy heart upon thy work, but never on its reward. — Bhagavad Gita 2.47 📿",
    "The soul is neither born, nor does it die. — Bhagavad Gita 2.20 ✨",
    "Perform your duty without attachment to results. — Bhagavad Gita 3.19 🌸",
    "I am the beginning, the middle, and the end of all creation. — Bhagavad Gita 10.20 🪷",
    "For one who has conquered the mind, the mind is the best of friends. — Bhagavad Gita 6.6 💛",
    "Change is the law of the universe. You can be a millionaire or a pauper in an instant. — Krishna 🌺",
]

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
    "Why did the developer go broke? Because he used up all his cache! 💸",
    "How many programmers does it take to change a light bulb? None — it's a hardware problem! 💡",
    "Why do Java developers wear glasses? Because they don't C#! 👓",
    "A SQL query walks into a bar, walks up to two tables and asks: 'Can I join you?' 🍻",
    "Why was the JavaScript developer sad? Because he didn't Node how to Express himself! 😄",
    "There are only 10 types of people: those who understand binary and those who don't. 1️⃣0️⃣",
]


# ---------------------------------------------------------------------------
# Session tracking — message count and duration
# ---------------------------------------------------------------------------
class Session:
    """Tracks chat session statistics."""

    def __init__(self):
        self.start_time = time.time()
        self.message_count = 0

    def record_message(self):
        """Increment the number of user messages exchanged."""
        self.message_count += 1

    def duration_seconds(self) -> int:
        """Return total session length in seconds."""
        return int(time.time() - self.start_time)


# ---------------------------------------------------------------------------
# UI helpers — welcome screen, separators, typing animation
# ---------------------------------------------------------------------------
def print_separator(char: str = "━", length: int = 54) -> None:
    """Print a horizontal separator line."""
    print(char * length)


def print_welcome() -> None:
    """Display the beautiful ASCII welcome screen."""
    print()
    print("╔════════════════════════════════════════════════════╗")
    print("║                                                    ║")
    print("║             🤖 KRISHNABOT AI 🤖                    ║")
    print("║                                                    ║")
    print("║         Rule Based Artificial Intelligence         ║")
    print("║                                                    ║")
    print("╚════════════════════════════════════════════════════╝")
    print()
    print("🙏 Jay Shree Krishna 🙏")
    print()
    print("Type 'help' to see available commands.")
    print("Type 'exit' to leave the chatbot.")

    # Remind user if weather API key is not configured yet
    if not os.getenv("OPENWEATHER_API_KEY", "").strip() or os.getenv(
        "OPENWEATHER_API_KEY", ""
    ).strip() == "your-openweather-key-here":
        print()
        print("⚠️  Weather: add OPENWEATHER_API_KEY to .env (free at openweathermap.org)")
    print()


def print_goodbye(session: Session) -> None:
    """Display goodbye message and session summary statistics."""
    print()
    print_separator()
    print("📊 SESSION SUMMARY")
    print_separator()
    print(f"Messages Exchanged : {session.message_count}")
    print(f"Session Duration   : {session.duration_seconds()} seconds")
    print_separator()
    print()
    print("🙏 Thank you for using KrishnaBot AI 🙏")
    print()


def type_text(text: str, prefix: str = "") -> None:
    """
    Print text with a typing animation effect.
    prefix is printed first without animation (e.g. bot label).
    """
    try:
        if prefix:
            print(prefix, end="", flush=True)
        for char in text:
            print(char, end="", flush=True)
            time.sleep(TYPING_SPEED)
        print()
    except (KeyboardInterrupt, EOFError):
        # If interrupted, still show full text so user isn't left hanging
        print(text)


def bot_reply(message: str) -> None:
    """Show bot label and type out the response with animation."""
    print()
    print("🤖 KrishnaBot is typing...")
    print()
    type_text(message, "🤖 KrishnaBot AI: ")


def print_help() -> None:
    """Display the full help menu with all available commands."""
    help_text = (
        "📋 KRISHNABOT AI — COMMAND MENU\n"
        "\n"
        "  Greetings & Chat\n"
        "  ─────────────────\n"
        "  hi / hello / hey     → Greet the bot\n"
        "  how are you          → Ask how the bot is doing\n"
        "  who are you          → Learn about KrishnaBot\n"
        "  what can you do      → See capabilities\n"
        "  bye / goodbye        → Farewell message\n"
        "\n"
        "  Inspiration & Fun\n"
        "  ─────────────────\n"
        "  motivation           → Random motivational quote\n"
        "  krishna              → Random Krishna quote 🙏\n"
        "  joke                 → Random programming joke 😄\n"
        "\n"
        "  Utilities\n"
        "  ─────────────────\n"
        "  date                 → Show today's date 📅\n"
        "  time                 → Show current time ⏰\n"
        "  weather              → Live weather (asks for city) 🌤️\n"
        "  ai                   → Ask Llama3 via Ollama (local AI) 🧠\n"
        "\n"
        "  Other\n"
        "  ─────────────────\n"
        "  help                 → Show this menu\n"
        "  exit                 → Quit and see session stats"
    )
    bot_reply(help_text)


# ---------------------------------------------------------------------------
# Feature functions — date, time, weather, Ollama AI
# ---------------------------------------------------------------------------
def get_current_date() -> str:
    """Return today's date in a friendly format."""
    now = datetime.now()
    return now.strftime("📅 Today is %A, %B %d, %Y.")


def get_current_time() -> str:
    """Return the current local time in a friendly format."""
    now = datetime.now()
    return now.strftime("⏰ Current time: %I:%M:%S %p.")


def extract_city_from_weather_query(message: str) -> str:
    """
    Pull a city name from phrases like:
    'weather ahmedabad', 'weather in mumbai', 'what is the weather in delhi'
    Returns empty string if no city found.
    """
    try:
        if message.startswith("weather in "):
            return message[len("weather in ") :].strip()
        if message.startswith("weather "):
            city = message[len("weather ") :].strip()
            if city and city not in ("forecast", "check"):
                return city
        if "weather in " in message:
            return message.split("weather in ", 1)[1].strip()
    except (AttributeError, IndexError):
        pass
    return ""


def fetch_weather(city: str) -> str:
    """
    Fetch live weather from OpenWeatherMap API.
    Requires OPENWEATHER_API_KEY in environment or .env file.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY", "").strip()

    if not api_key:
        return (
            "🌤️ Weather service is not configured.\n"
            "   Please add your free API key to a .env file:\n"
            "   OPENWEATHER_API_KEY=your_key_here\n"
            "   Get one at: https://openweathermap.org/api"
        )

    if not city or not city.strip():
        return "Please enter a valid city name. 🏙️"

    try:
        params = urllib.parse.urlencode(
            {"q": city.strip(), "appid": api_key, "units": "metric"}
        )
        url = f"{WEATHER_API_URL}?{params}"

        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        if "main" not in data or "weather" not in data:
            return f"Could not read weather data for '{city}'. Please try again."

        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        condition = data["weather"][0]["description"].title()
        place = data.get("name", city)
        country = data.get("sys", {}).get("country", "")

        location = f"{place}, {country}" if country else place

        return (
            f"🌤️ Weather in {location}:\n"
            f"   • Condition : {condition}\n"
            f"   • Temperature: {temp}°C\n"
            f"   • Humidity  : {humidity}%"
        )

    except urllib.error.HTTPError as error:
        if error.code == 404:
            return f"🏙️ City '{city}' not found. Please check the spelling and try again."
        if error.code == 401:
            return "🔑 Invalid weather API key. Please check your OPENWEATHER_API_KEY in .env."
        return f"Weather service returned an error (HTTP {error.code}). Please try again later."

    except urllib.error.URLError:
        return "🌐 Could not connect to the weather service. Check your internet connection."

    except (json.JSONDecodeError, KeyError, TimeoutError, OSError):
        return "Something went wrong while fetching weather. Please try again. 🙏"

    except Exception:
        return "An unexpected error occurred. Please try again later. 🙏"


def ask_ollama(question: str) -> str:
    """
    Send a question to local Ollama Llama3 model.
    Returns AI response or a friendly fallback if Ollama is unavailable.
    """
    if not question or not question.strip():
        return "Please type a question for the AI. 🧠"

    payload = json.dumps(
        {
            "model": OLLAMA_MODEL,
            "prompt": question.strip(),
            "stream": False,
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))

        answer = data.get("response", "").strip()
        if answer:
            return f"🧠 AI Response:\n\n{answer}"
        return "The AI returned an empty response. Please try rephrasing your question."

    except urllib.error.URLError:
        return (
            "🧠 Ollama is not available on this machine.\n"
            "   To use AI mode:\n"
            "   1. Install Ollama from https://ollama.com\n"
            "   2. Run: ollama pull llama3\n"
            "   3. Make sure Ollama is running, then try 'ai' again."
        )

    except json.JSONDecodeError:
        return "Received an invalid response from Ollama. Please try again."

    except (TimeoutError, OSError):
        return "Ollama took too long to respond. Please try a shorter question."

    except Exception:
        return "Something went wrong with AI mode. Please try again later. 🙏"


# ---------------------------------------------------------------------------
# Core rule engine — if-elif-else logic (original chatbot requirements)
# ---------------------------------------------------------------------------
def normalize_input(user_input: str) -> str:
    """Convert input to lowercase and strip whitespace/punctuation."""
    try:
        message = user_input.lower().strip()
        while message and message[-1] in "?!.,;:":
            message = message[:-1].strip()
        return message
    except (AttributeError, TypeError):
        return ""


def get_rule_response(message: str) -> str:
    """
    Process user message using if-elif-else rules only.
    Returns a response string, or empty string if a special command
    (weather / ai / help) should be handled by the main loop instead.
    """
    # --- Greetings ---
    if message in ("hi", "hello", "hey"):
        return "Hello dear! 😊 How can I help you today?"

    # --- How are you ---
    elif message in ("how are you", "how r u", "how're you", "how are you doing"):
        return (
            "I'm doing wonderful, thank you for asking! 😊 "
            "I'm always here and ready to help you. 🙏"
        )

    # --- Who are you ---
    elif message in ("who are you", "what are you", "your name"):
        return (
            "I am KrishnaBot AI 🤖 — your friendly rule-based assistant! "
            "I can chat, share quotes, tell jokes, check weather, and more. "
            "Type 'help' to see everything I can do. 🙏"
        )

    # --- What can you do ---
    elif message in ("what can you do", "what do you do", "capabilities"):
        return (
            "I can do many things! 🌟\n"
            "  • Greet and chat with you\n"
            "  • Share motivation & Krishna quotes\n"
            "  • Tell jokes, show date & time\n"
            "  • Fetch live weather for any city\n"
            "  • Answer questions via Ollama AI\n"
            "Type 'help' for the full command list!"
        )

    # --- Motivation ---
    elif message in ("motivation", "motivate me", "motivate", "inspire me"):
        return f"💪 {random.choice(MOTIVATIONAL_QUOTES)}"

    # --- Krishna quotes ---
    elif message in ("krishna", "krishna quote", "gita", "bhagavad gita"):
        return f"🙏 {random.choice(KRISHNA_QUOTES)}"

    # --- Jokes ---
    elif message in ("joke", "jokes", "funny", "tell me a joke"):
        return f"😄 {random.choice(JOKES)}"

    # --- Date ---
    elif message in ("date", "today", "today's date", "what is the date"):
        return get_current_date()

    # --- Time ---
    elif message in ("time", "what time", "what is the time", "current time"):
        return get_current_time()

    # --- Goodbye (chat continues; use 'exit' to quit program) ---
    elif message in ("bye", "goodbye", "see you", "see ya", "farewell"):
        return "Goodbye dear! 👋 May Lord Krishna bless you. Come back anytime! 🙏"

    # --- Help — handled separately in main loop for formatted menu ---
    elif message in ("help", "help me", "commands", "menu"):
        return ""  # Signal: main loop will call print_help()

    # --- Weather — handled separately (two-step flow in main loop) ---
    elif message in ("weather", "weather forecast", "check weather"):
        return ""  # Signal: main loop will start weather flow

    # --- AI mode — handled separately (two-step flow in main loop) ---
    elif message in ("ai", "ask ai", "ai mode", "llama"):
        return ""  # Signal: main loop will start AI flow

    # --- Unknown input — graceful fallback ---
    else:
        return (
            "Hmm, I'm not sure about that. 🤔\n"
            "   Try 'help' to see what I understand, "
            "or type 'ai' to ask our local AI brain!"
        )


# ---------------------------------------------------------------------------
# Main chat loop
# ---------------------------------------------------------------------------
def main() -> None:
    """Run KrishnaBot AI until the user types 'exit'."""
    session = Session()
    pending_action = None  # None | "weather" | "ai"

    print_welcome()

    while True:
        try:
            user_input = input("\n👤 You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            bot_reply("Session interrupted. Goodbye! 🙏")
            print_goodbye(session)
            break

        # --- Exit command ---
        if normalize_input(user_input) == "exit":
            bot_reply("Goodbye dear! 🙏 Until we meet again!")
            print_goodbye(session)
            break

        # --- Skip empty input ---
        if not user_input:
            bot_reply("Please type something! I'm here to help. 😊")
            continue

        session.record_message()
        message = normalize_input(user_input)

        # --- Handle pending two-step flows (weather / ai) ---
        if pending_action == "weather":
            pending_action = None
            bot_reply(fetch_weather(user_input))
            continue

        if pending_action == "ai":
            pending_action = None
            bot_reply(ask_ollama(user_input))
            continue

        # --- Special commands that need extra handling ---
        if message in ("help", "help me", "commands", "menu"):
            print_help()
            continue

        # One-line weather: "weather mumbai" or "what is the weather in ahmedabad"
        city = extract_city_from_weather_query(message)
        if city:
            bot_reply(fetch_weather(city))
            continue

        if message in ("weather", "weather forecast", "check weather"):
            pending_action = "weather"
            bot_reply("🌤️ Which city would you like the weather for?")
            continue

        if message in ("ai", "ask ai", "ai mode", "llama"):
            pending_action = "ai"
            bot_reply("🧠 What would you like to ask the AI? (Powered by Ollama Llama3)")
            continue

        # --- Standard if-elif-else rule responses ---
        try:
            response = get_rule_response(message)
            bot_reply(response)
        except Exception:
            bot_reply(
                "Oops! Something unexpected happened, but I'm still here. "
                "Please try again. 🙏"
            )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("\n🙏 KrishnaBot encountered an error. Please restart the program.")
        sys.exit(1)
