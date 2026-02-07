from openai import OpenAI
import json
from datetime import datetime

class AIEngine:
    def __init__(self, api_key):
        # http_client=None ensures compatibility with cloud hosting environments
        self.client = OpenAI(api_key=api_key, http_client=None)

    def get_best_worker_for_task(self, task, workers):
        """
        AI evaluates the task nature and matches it against worker titles 
        and their scheduled bi-weekly availability.
        """
        # Get current date in the same format as the HTML date picker (YYYY-MM-DD)
        today = datetime.now().strftime('%Y-%m-%d')
        
        prompt = f"""
        Identify the single most qualified and available worker for this aerospace task.
        
        TASK TO ASSIGN:
        - Description: {task['description']}
        - Urgency Level: {task['urgency']} (1-5)
        
        CURRENT SYSTEM DATE: {today}
        
        PERSONNEL DIRECTORY:
        {json.dumps(workers)}
        
        ASSIGNMENT HIERARCHY:
        1. QUALIFICATIONS: The 'job_title' must logically align with the 'description'. 
           (e.g., A 'Janitor' cannot do 'Hydraulic Repair').
        2. AVAILABILITY: The CURRENT SYSTEM DATE must fall between the worker's 'start_date' and 'end_date'.
        3. URGENCY: If urgency is 4 or 5, prioritize workers with 'Senior' or 'Lead' in their titles.
        
        If no worker meets BOTH the qualification and the current schedule requirements, return null.
        
        Return JSON ONLY in this format:
        {{"worker_name": "Full Name Here"}}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a factory operations AI for Qarbon Aerospace."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"AI Engine Error: {e}")
            return None

    def assign_tasks_one_per_person(self, workers, tasks):
        """
        Bulk optimization for an entire shift.
        Matches available unassigned tasks to available scheduled workers.
        """
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Filter workers who are actually scheduled to work today
        available_workers = [
            w for w in workers 
            if w['start_date'] <= today <= w['end_date']
        ]
        
        # Filter for tasks that are not yet assigned or completed
        unassigned_tasks = [
            t for t in tasks 
            if not t['assigned_to'] and not t['date_completed']
        ]

        if not available_workers or not unassigned_tasks:
            return {}

        prompt = f"""
        Perform bulk task distribution for the current shift.
        DATE: {today}
        WORKERS: {json.dumps(available_workers)}
        TASKS: {json.dumps(unassigned_tasks)}
        
        RULES:
        - Assign a maximum of ONE task per person.
        - Match qualifications (Job Title) to the Task Description.
        - Prioritize high urgency tasks first.
        
        Return JSON ONLY: {{"WorkerName": [TaskRowNumber]}}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except:
            return {}
