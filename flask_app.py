from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from uuid import uuid4
from datetime import datetime, timedelta
from v1.graph import WorkFlow
from typing import Dict, List
import random

app = Flask(__name__)
# CORS(app,origins=['http://localhost:3000/',"*"])
CORS(app,origins="*")
app.config['CORS_HEADERS'] = 'Content-Type'



# In-memory storage for chats
# In production, you'd want to use a proper database
class ChatStorage:
    def __init__(self):
        self.chats: Dict[str, dict] = {}
        self.workflows: Dict[str, WorkFlow] = {}

    def create_chat(self, title: str) -> dict:
        chat_id = str(uuid4())
        chat = {
            'id': chat_id,
            'title': title,
            'messages': [],
            'created_at': datetime.now().isoformat()
        }
        self.chats[chat_id] = chat
        self.workflows[chat_id] = WorkFlow()  # Create a new workflow for each chat
        print('New Chat Created', chat_id)
        return chat

    def get_chat(self, chat_id: str) -> dict:
        return self.chats.get(chat_id)

    def get_all_chats(self) -> List[dict]:
        return list(self.chats.values())

    def add_message(self, chat_id: str, message: dict) -> None:
        if chat_id in self.chats:
            self.chats[chat_id]['messages'].append(message)
            print(self.chats[chat_id]['messages'])

    def clear_chat(self, chat_id: str) -> None:
        if chat_id in self.chats:
            self.chats[chat_id]['messages'] = []
            self.workflows[chat_id] = WorkFlow()  # Reset the workflow


# Initialize chat storage
chat_storage = ChatStorage()


@app.route('/chats', methods=['GET'])
def get_chats():
    """Get all chats"""
    return jsonify(chat_storage.get_all_chats())


@app.route('/chats', methods=['POST'])
def create_chat():
    """Create a new chat"""
    data = request.get_json()
    title = data.get('title', 'New Chat')
    chat = chat_storage.create_chat(title)
    return jsonify(chat)


@app.route('/chats/<chat_id>', methods=['GET'])
def get_chat(chat_id):
    """Get a specific chat"""
    chat = chat_storage.get_chat(chat_id)
    if chat is None:
        return jsonify({'error': 'Chat not found'}), 404
    print('Return Chat:', chat)
    return jsonify(chat)


@app.route('/chats/<chat_id>/messages', methods=['POST'])
def send_message(chat_id):
    """Send a message in a specific chat"""
    chat = chat_storage.get_chat(chat_id)
    if chat is None:
        return jsonify({'error': 'Chat not found'}), 404

    data = request.get_json()
    print(data)
    user_message = data.get('content')

    if not user_message:
        return jsonify({'error': 'Message content is required'}), 400

    # Handle special commands
    if user_message.startswith('/'):
        if user_message == '/clear':
            chat_storage.clear_chat(chat_id)
            return jsonify({
                'id': str(uuid4()),
                'role': 'assistant',
                'content': 'Chat history cleared.'
            })
        return jsonify({
            'id': str(uuid4()),
            'role': 'assistant',
            'content': 'Command not recognized.'
        })

    # Process message using the chat-specific workflow
    workflow = chat_storage.workflows[chat_id]
    # try:
    response = workflow.invoke(user_message)
    ai_message = {
        'id': str(uuid4()),
        'role': 'assistant',
        'content': response['messages'][-1].content
    }
    chat_storage.add_message(chat_id, data)
    chat_storage.add_message(chat_id, ai_message)
    return jsonify(ai_message)
    # TODO: Restore Exception Handling
    # except Exception as e:
    #     print("Inga tha error: ", e)
    #     return jsonify({
    #         'error': f'Error processing message: {str(e)}'
    #     }), 500


@app.route('/chats/<chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    """Delete a specific chat"""
    if chat_id in chat_storage.chats:
        del chat_storage.chats[chat_id]
        del chat_storage.workflows[chat_id]
        return jsonify({'message': 'Chat deleted successfully'})
    return jsonify({'error': 'Chat not found'}), 404


@app.route('/chats/<chat_id>/title', methods=['PATCH'])
def update_chat_title(chat_id):
    """Update chat title"""
    chat = chat_storage.get_chat(chat_id)
    if chat is None:
        return jsonify({'error': 'Chat not found'}), 404

    data = request.get_json()
    new_title = data.get('title')
    if not new_title:
        return jsonify({'error': 'Title is required'}), 400

    chat['title'] = new_title
    return jsonify(chat)


@app.route('/performance', methods=['GET'])
def get_performance():
    # Generate mock data for demonstration
    performance_data = {
        'overallProgress': random.randint(60, 95),
        'studyHours': random.randint(20, 40),
        'tasksCompleted': random.randint(10, 30),
        'averageGrade': round(random.uniform(70, 95), 2),
        'streak': random.randint(1, 14),
        'focusScore': random.randint(60, 100),
        'upcomingDeadlines': [
            {'task': 'Math Assignment', 'date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')},
            {'task': 'History Essay', 'date': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')},
            {'task': 'Science Project', 'date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')},
        ],
        'recentAchievements': [
            'Completed 7-day study streak',
            'Improved average grade by 5%',
            'Finished all tasks for the week',
        ],
        'subjectPerformance': [
            {'subject': 'Math', 'score': random.randint(70, 100)},
            {'subject': 'Science', 'score': random.randint(70, 100)},
            {'subject': 'History', 'score': random.randint(70, 100)},
            {'subject': 'English', 'score': random.randint(70, 100)},
            {'subject': 'Art', 'score': random.randint(70, 100)},
        ],
        'weeklyStudyHours': [
            {'day': 'Mon', 'hours': random.randint(1, 6)},
            {'day': 'Tue', 'hours': random.randint(1, 6)},
            {'day': 'Wed', 'hours': random.randint(1, 6)},
            {'day': 'Thu', 'hours': random.randint(1, 6)},
            {'day': 'Fri', 'hours': random.randint(1, 6)},
            {'day': 'Sat', 'hours': random.randint(1, 6)},
            {'day': 'Sun', 'hours': random.randint(1, 6)},
        ],
    }
    return jsonify(performance_data)


if __name__ == '__main__':
    app.run(debug=True)
