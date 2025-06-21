import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

def get_intent_from_prompt(user_input, current_state=None):
    system_prompt = "You are a helpful AI data assistant."

    base_instruction = """
You are an intelligent assistant helping a user define a data task for AI model development.
You will be given:
1. The current structured task spec (if any).
2. A new user message.

Your job is to return an updated JSON task spec that merges in the new information.

ONLY update the relevant fields, and DO NOT lose earlier information. Always return a complete JSON object.

Keys:
- goal
- data_requirements (list)
- location
- timeframe (can be string or {start_year, end_year})
- preferred_format
- output_type
"""

    current_state_json = current_state if current_state else {}

    user_message = f"""
Current task spec:
{current_state_json}

User message:
"{user_input}"

Return ONLY a full JSON object.
"""

    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=500,
        temperature=0.2,
        system=system_prompt,
        messages=[{"role": "user", "content": base_instruction + user_message}]
    )

    return response.content[0].text
