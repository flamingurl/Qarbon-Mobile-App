from openai import OpenAI
import json
from datetime import datetime

class AIEngine:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key, http_client=None)

    def get_best_worker_for_task(self, task, workers):
        today = datetime.now().strftime('%Y-%m-%d')
        
        prompt = f"""
        Identify the best qualified worker for: "{task['description']}"
        CURRENT DATE: {today}
        
        WORKERS LIST (including their specific working dates):
        {json.dumps(workers)}
        
        RULES:
        1. A worker is ONLY available if CURRENT DATE is in their 'dates' list.
        2. Job title must match the task nature.
        
        Return JSON ONLY: {{"worker_name": "Name" or null}}
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except:
            return None
