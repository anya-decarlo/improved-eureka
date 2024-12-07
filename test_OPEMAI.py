from typing import List, Dict, Union, Optional
from dataclasses import dataclass
import openai
import os

@dataclass
class Message:
    role: str  # can be "user", "assistant", or "system"
    content: str

@dataclass
class SendMessageOptions:
    messages: List[Message]
    max_tokens: int = 3000

@dataclass
class StructuredMessage:
    explanation: str
    decision: bool

async def send_message(options: SendMessageOptions) -> StructuredMessage:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    client = openai.OpenAI()
    
    messages = [{"role": msg.role, "content": msg.content} for msg in options.messages]
    
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=options.max_tokens
    )
    
    # Process the response and return structured message
    # You'll need to implement the logic to extract explanation and decision
    # from the response based on your specific needs
    return StructuredMessage(
        explanation=response.choices[0].message.content,
        decision=True  # You might want to modify this based on the response
    )