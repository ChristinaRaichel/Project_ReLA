import json
from pathlib import Path
from langchain_core.prompts import PromptTemplate

def load_agent_prompts(json_path: str = "attachment-style-roleplay/prompts/agent_profiles.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        profiles = json.load(f)

    prompt_templates = {}
    for style, data in profiles.items():
        prompt_templates[style] = PromptTemplate.from_template(
            f"{data['prompt']}\n\You: {{input}}\nPartner:"
        )
    
    return prompt_templates
