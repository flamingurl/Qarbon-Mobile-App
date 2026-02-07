from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from database_handler import DatabaseHandler
from ai_engine import AIEngine
import os
from dotenv import load_dotenv

load_dotenv()
# Set static_folder to 'static' to match your folder tree
app = Flask(__name__, static_folder='static')
CORS(app)

db = DatabaseHandler()
ai_engine = AIEngine(os.getenv("OPENAI_API_KEY"))

@app.route('/')
def route_index(): 
    return send_from_directory(app.static_folder, 'manager.html')

@app.route('/manager')
def route_manager(): 
    return send_from_directory(app.static_folder, 'manager.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks(): 
    return jsonify(db.read_tasks())

@app.route('/api/workers', methods=['GET'])
def get_workers(): 
    return jsonify(db.read_workers())

@app.route('/api/add-worker', methods=['POST'])
def add_worker():
    d = request.json
    db.add_worker(d['name'], d['job_title'], d['worker_schedule'])
    return jsonify({'success': True})

@app.route('/api/add-task', methods=['POST'])
def add_task():
    d = request.json
    # Logic Fix: Ensuring keys match the JavaScript fetch request
    db.add_task(d['urgency'], d['description'])
    return jsonify({'success': True})

@app.route('/api/assign-task-to-best', methods=['POST'])
def assign_to_best():
    task_id = request.json.get('task_id')
    tasks = db.read_tasks()
    workers = db.read_workers()
    target_task = next((t for t in tasks if t['row_number'] == task_id), None)
    result = ai_engine.get_best_worker_for_task(target_task, workers)
    if result and result.get('worker_name'):
        db.assign_task_to_worker(task_id, result['worker_name'])
        return jsonify({'success': True, 'worker': result['worker_name']})
    return jsonify({'success': False, 'message': 'No qualified personnel scheduled.'})

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
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
