"""
ChatGPT-powered conversation engine with live weather tool support.
"""

import json
import os

from openai import OpenAI

from weather_service import get_weather

# Tool definition — tells ChatGPT it can look up real weather
WEATHER_TOOL = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": (
            "Get current live weather for a city or place. "
            "Call this only when the user has given a location name."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City or place name, e.g. Mumbai, London, New York",
                }
            },
            "required": ["city"],
        },
    },
}

SYSTEM_PROMPT = """You are a friendly, helpful AI assistant in a terminal chatbot.

Your job:
- Answer questions clearly and conversationally on any topic you know.
- When the user asks about weather but does NOT give a city or place, ask which location they want.
- When they provide a location, use the get_weather tool for live, accurate weather data.
- Keep replies concise but warm. Use plain text (no markdown headers).
- If you cannot verify live data (news, stock prices, etc.), say so honestly and share general knowledge when helpful.

You are NOT browsing Google in real time — you use your knowledge plus the weather tool for live weather."""


class AIChatEngine:
    """Manages ChatGPT conversation with memory and tool calls."""

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set")

        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    def _run_tool(self, tool_name: str, arguments: str) -> str:
        """Execute a tool call requested by ChatGPT."""
        if tool_name == "get_weather":
            args = json.loads(arguments)
            return get_weather(args.get("city", ""))
        return f"Unknown tool: {tool_name}"

    def chat(self, user_message: str) -> str:
        """Send a user message and return the assistant's reply."""
        self.messages.append({"role": "user", "content": user_message})

        # Loop handles tool calls (e.g. weather lookup) until we get a text reply
        while True:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=[WEATHER_TOOL],
                tool_choice="auto",
            )

            assistant_message = response.choices[0].message

            # ChatGPT wants to call a tool (e.g. get_weather)
            if assistant_message.tool_calls:
                self.messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_message.content,
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments,
                                },
                            }
                            for tc in assistant_message.tool_calls
                        ],
                    }
                )

                for tool_call in assistant_message.tool_calls:
                    result = self._run_tool(
                        tool_call.function.name,
                        tool_call.function.arguments,
                    )
                    self.messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result,
                        }
                    )
                continue

            # Normal text reply
            reply = assistant_message.content or "I'm not sure how to respond to that."
            self.messages.append({"role": "assistant", "content": reply})
            return reply
