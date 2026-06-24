import json
import re

def extract_json(text: str) -> dict | list:
    text = text.strip()
 
    fenced = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fenced:
        text = fenced.group(1).strip()

    return json.loads(text)