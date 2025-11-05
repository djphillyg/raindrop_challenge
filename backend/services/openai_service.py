from openai import OpenAI
from dotenv import load_dotenv
import textwrap

load_dotenv()

class OpenAIClient:
    def __init__(self):
        self.client = OpenAI()

    def call(self, message: str) -> str:
        """Send a message to OpenAI and get a response."""
        response = self.client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content or ""
    
    def call_with_tool(self, input, tool):
        result = self.client.responses.create(
            model="gpt-5-mini",
            input=input,
            text={"format": {"type": "text"}},
            tools=[tool],
            parallel_tool_calls=False,
            timeout=60,
            reasoning={"effort": "medium"}
        )

        return result.output[1].input # type: ignore