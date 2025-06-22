
import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_intent_from_prompt(prompt, schema={}):
    system_msg = (
        "You are a data assistant that converts user prompts into structured JSON task specs "
        "for dataset generation and preparation. Use fields: goal, data_requirements, location, "
        "timeframe (start_year, end_year), preferred_format, output_type. Only return JSON."
    )
    example = {
        "goal": "Analyze city air quality and traffic",
        "data_requirements": ["Air pollution index", "Vehicle density"],
        "location": "Los Angeles",
        "timeframe": {"start_year": 2015, "end_year": 2023},
        "preferred_format": "Tabular",
        "output_type": "CSV"
    }
    try:
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": f"Prompt: {prompt} \n Example: {json.dumps(example)}"}
            ],
            temperature=0.2
        )
        content = response.choices[0].message.content.strip()
        json_start = content.find("{")
        json_end = content.rfind("}")
        json_text = content[json_start:json_end + 1]
        return json.loads(json_text)
    except Exception as e:
        print(f"Groq intent parsing failed: {e}")
        return {
            "goal": prompt,
            "data_requirements": [],
            "location": None,
            "timeframe": None,
            "preferred_format": None,
            "output_type": None
        }
