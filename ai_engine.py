from openai import OpenAI
import json
from datetime import datetime, timedelta

class AIEngine:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key, http_client=None)

    def get_best_worker_for_task(self, task, workers):
        # Determine if current time is Morning or Evening shift
        now = datetime.utcnow() - timedelta(hours=5)
        current_date = now.strftime('%Y-%m-%d')
        current_shift = 1 if now.hour < 15 else 2 # Morning before 3PM, Else Evening
        
        prompt = f"""
        Assign best worker for: {task['description']}
        DATE: {current_date} | SHIFT REQ: {'Morning' if current_shift == 1 else 'Evening'}
        
        WORKERS: {json.dumps(workers)}
        
        LOGIC:
        1. Match Job Title to Task.
        2. Worker must have the current date in 'shifts' and the value must match shift req (1=AM, 2=PM).
        
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
