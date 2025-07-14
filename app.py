from flask import Flask, request, jsonify, send_from_directory
from pymongo import MongoClient
from datetime import datetime
import os

app = Flask(__name__, static_url_path='', static_folder='static')
client = MongoClient('mongodb+srv://kartikmanche:1234@cluster0.nlfoddw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['webhookDB']
collection = db['events']

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    event_type = request.headers.get('X-GitHub-Event')

    if event_type == 'push':
        record = {
            'type': 'push',
            'author': data['pusher']['name'],
            'to_branch': data['ref'].split('/')[-1],
            'timestamp': datetime.utcnow()
        }
    elif event_type == 'pull_request':
        pr = data['pull_request']
        record = {
            'type': 'pull_request',
            'author': pr['user']['login'],
            'from_branch': pr['head']['ref'],
            'to_branch': pr['base']['ref'],
            'timestamp': datetime.utcnow()
        }
    elif event_type == 'merge':
        record = {
            'type': 'merge',
            'author': data['sender']['login'],
            'from_branch': 'dev',
            'to_branch': 'master',
            'timestamp': datetime.utcnow()
        }
    else:
        return jsonify({'message': 'Unhandled event type'}), 400

    collection.insert_one(record)
    return jsonify({'message': 'Event recorded'}), 200

@app.route('/events', methods=['GET'])
def get_events():
    return jsonify(list(collection.find({}, {'_id': 0})))

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

if __name__ == '__main__':
    app.run(debug=True)
