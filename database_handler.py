import sqlite3
import json
from datetime import datetime, timedelta
import os

class DatabaseHandler:
    def __init__(self, db_path='data/qarbon_app.db'):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_dir, db_path)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._create_tables()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _create_tables(self):
        with self._get_connection() as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS workers 
                            (name TEXT PRIMARY KEY, job_title TEXT, dates_json TEXT)''')
            conn.execute('''CREATE TABLE IF NOT EXISTS tasks 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, urgency INTEGER, description TEXT, 
                             date_assigned TEXT, date_completed TEXT, assigned_to TEXT)''')

    def read_workers(self):
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM workers").fetchall()
            workers = []
            for r in rows:
                w = dict(r)
                w['shifts'] = json.loads(w['dates_json']) if w['dates_json'] else {}
                workers.append(w)
            return workers

    def read_tasks(self):
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT id as row_number, * FROM tasks").fetchall()
            return [dict(r) for r in rows]

    def add_worker(self, name, job_title, shifts_dict):
        with self._get_connection() as conn:
            conn.execute("INSERT OR REPLACE INTO workers VALUES (?, ?, ?)", 
                         (name, job_title, json.dumps(shifts_dict)))

    def add_task(self, urgency, description):
        est_date = (datetime.utcnow() - timedelta(hours=5)).strftime('%m/%d/%Y')
        with self._get_connection() as conn:
            conn.execute("INSERT INTO tasks (urgency, description, date_assigned, date_completed, assigned_to) VALUES (?, ?, ?, '', '')", 
                         (urgency, description, est_date))

    def assign_task_to_worker(self, row_number, worker_name):
        with self._get_connection() as conn:
            conn.execute("UPDATE tasks SET assigned_to = ? WHERE id = ?", (worker_name, row_number))

    def update_task_completion(self, row_number):
        est_time = (datetime.utcnow() - timedelta(hours=5)).strftime('%m/%d/%Y %I:%M %p')
        with self._get_connection() as conn:
            conn.execute("UPDATE tasks SET date_completed = ? WHERE id = ?", (est_time, row_number))

    def delete_task(self, row_number):
        with self._get_connection() as conn:
            conn.execute("DELETE FROM tasks WHERE id = ?", (row_number,))

    def delete_worker(self, name):
        with self._get_connection() as conn:
            conn.execute("DELETE FROM workers WHERE name = ?", (name,))
