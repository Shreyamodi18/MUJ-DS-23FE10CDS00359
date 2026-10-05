import json
import os
import time

import yaml
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class LLMClient:
    def __init__(self, config_path="config.yaml", prompts_path="prompts.yaml"):
        self.config = load_yaml(config_path)
        self.prompts = load_yaml(prompts_path)

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found. Check your .env file.")
        self.client = genai.Client(api_key=api_key)

    def build_prompt(self, resume, job_description):
        prompt = self.prompts["task_prompt"]
        replacements = {
            "{output_schema}": self.prompts["output_schema"],
            "{few_shot_example}": self.prompts["few_shot_example"],
            "{resume}": resume,
            "{job_description}": job_description,
        }
        for key, value in replacements.items():
            prompt = prompt.replace(key, value)
        return prompt

    def analyze(self, resume, job_description):
        prompt = self.build_prompt(resume, job_description)
        retries = self.config["max_retries"]

        for attempt in range(1, retries + 1):
            try:
                response = self.client.models.generate_content(
                    model=self.config["model"],
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=self.prompts["system_prompt"],
                        temperature=self.config["temperature"],
                        max_output_tokens=self.config["max_output_tokens"],
                        response_mime_type="application/json",
                        thinking_config=types.ThinkingConfig(thinking_budget=0),
                    ),
                )
                return self._parse_json(response.text)
            except Exception as e:
                print(f"Attempt {attempt}/{retries} failed: {e}")
                if attempt == retries:
                    raise
                time.sleep(self.config["retry_delay_seconds"] * attempt)

    @staticmethod
    def _parse_json(text):
        text = text.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.lower().startswith("json"):
                text = text[4:]
        return json.loads(text)