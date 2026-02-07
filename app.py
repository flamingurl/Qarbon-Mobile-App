from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from database_handler import DatabaseHandler
from ai_engine import AIEngine
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__, static_folder='static')
CORS(app)

db = DatabaseHandler()
ai_engine = AIEngine(os.getenv("OPENAI_API_KEY"))

@app.route('/')
def route_index(): 
    return send_from_directory(app.static_folder, 'manager.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks(): return jsonify(db.read_tasks())

@app.route('/api/workers', methods=['GET'])
def get_workers(): return jsonify(db.read_workers())

@app.route('/api/add-worker', methods=['POST'])
def add_worker():
    d = request.json
    db.add_worker(d['name'], d['job_title'], d['worker_schedule'])
    return jsonify({'success': True})

@app.route('/api/add-task', methods=['POST'])
def add_task():
    d = request.json
    db.add_task(d['urgency'], d['description'])
    return jsonify({'success': True})

@app.route('/api/assign-task-to-best', methods=['POST'])
def assign_task_to_best():
    task_id = request.json.get('task_id')
    tasks = db.read_tasks()
    workers = db.read_workers()
    target_task = next((t for t in tasks if t['row_number'] == task_id), None)
    
    result = ai_engine.get_best_worker_for_task(target_task, workers)
    if result and result.get('worker_name'):
        db.assign_task_to_worker(task_id, result['worker_name'])
        return jsonify({'success': True, 'worker': result['worker_name']})
    return jsonify({'success': False, 'message': 'No qualified personnel scheduled for the current shift.'})

@app.route('/api/assign-worker-to-best', methods=['POST'])
def assign_worker_to_best():
    worker_name = request.json.get('worker_name')
    workers = db.read_workers()
    tasks = db.read_tasks()
    target_worker = next((w for w in workers if w['name'] == worker_name), None)
    
    # AI finds the best unassigned task for this specific person
    result = ai_engine.get_best_task_for_worker(target_worker, tasks)
    if result and result.get('task_id'):
        db.assign_task_to_worker(result['task_id'], worker_name)
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'No suitable unassigned tasks found for this worker today.'})

@app.route('/api/assign-tasks-bulk', methods=['POST'])
def assign_bulk():
    workers = db.read_workers()
    tasks = db.read_tasks()
    assignments = ai_engine.assign_tasks_one_per_person(workers, tasks)
    for name, task_ids in assignments.items():
        if task_ids: db.assign_task_to_worker(task_ids[0], name)
    return jsonify({'success': True})

@app.route('/api/complete-task', methods=['POST'])
def complete_task():
    db.update_task_completion(request.json['row_number'])
    return jsonify({'success': True})

@app.route('/api/delete-task/<int:row>', methods=['DELETE'])
def delete_task(row):
    db.delete_task(row)
    return jsonify({'success': True})

@app.route('/api/delete-worker/<name>', methods=['DELETE'])
def delete_worker(name):
    db.delete_worker(name)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
