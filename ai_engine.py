from openai import OpenAI
import json
from datetime import datetime, timedelta

class AIEngine:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key, http_client=None)

    def get_best_worker_for_task(self, task, workers):
        now = datetime.utcnow() - timedelta(hours=5)
        current_date = now.strftime('%Y-%m-%d')
        # Shift logic: 1=Morning, 2=Evening
        current_shift = 1 if now.hour < 15 else 2 
        
        prompt = f"""
        Assign best worker for: {task['description']}
        CURRENT DATE: {current_date} | CURRENT SHIFT: {'Morning' if current_shift == 1 else 'Evening'}
        WORKERS: {json.dumps(workers)}
        
        RULES:
        1. Worker MUST have the current date in their 'shifts' and the shift type must match.
        2. Job Title must fit Task nature.
        Return JSON: {{"worker_name": "Name" or null}}
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
