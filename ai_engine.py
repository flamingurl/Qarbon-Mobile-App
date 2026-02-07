from openai import OpenAI
import json
from datetime import datetime, timedelta

class AIEngine:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key, http_client=None)

    def _get_current_context(self):
        now = datetime.utcnow() - timedelta(hours=5)
        return now.strftime('%Y-%m-%d'), (1 if now.hour < 15 else 2)

    def get_best_worker_for_task(self, task, workers):
        date, shift = self._get_current_context()
        prompt = f"""Match the best worker for: {task['description']}
        Date: {date} | Shift: {'AM' if shift==1 else 'PM'}
        Workers: {json.dumps(workers)}
        Rules: Match by Job Title and Shift. Return JSON {{"worker_name": "Name" or null}}"""
        return self._call_ai(prompt)

    def get_best_task_for_worker(self, worker, tasks):
        date, shift = self._get_current_context()
        unassigned = [t for t in tasks if not t['assigned_to'] and not t['date_completed']]
        prompt = f"""Find the best task for {worker['name']} ({worker['job_title']})
        Date: {date} | Shift: {'AM' if shift==1 else 'PM'}
        Tasks: {json.dumps(unassigned)}
        Return JSON {{"task_id": ID or null}}"""
        return self._call_ai(prompt)

    def assign_tasks_one_per_person(self, workers, tasks):
        date, shift = self._get_current_context()
        prompt = f"""Bulk assign workers to tasks for {date} (Shift {shift}).
        Workers: {json.dumps(workers)} | Tasks: {json.dumps(tasks)}
        Return JSON: {{"WorkerName": [TaskID]}}"""
        return self._call_ai(prompt)

    def _call_ai(self, prompt):
        try:
            res = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(res.choices[0].message.content)
        except: return {}
