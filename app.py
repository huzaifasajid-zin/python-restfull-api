from flask import Flask, jsonify, request
import sqlite3
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "notes.db")
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/notes/all', methods=['GET'])
def get_all_notes():
    conn = get_db_connection()
    notes = conn.execute('SELECT * FROM notes').fetchall()
    conn.close()
    return jsonify([dict(note) for note in notes])


@app.route('/notes/search', methods=['GET'])
def search_notes():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400
    conn = get_db_connection()
    notes = conn.execute('SELECT * FROM notes WHERE title LIKE ? OR content LIKE ?', (f'%{query}%', f'%{query}%')).fetchall()
    conn.close()
    return jsonify([dict(note) for note in notes])

@app.route('/notes/count', methods=['GET'])
def count_notes():
    conn = get_db_connection()
    count = conn.execute('SELECT COUNT(*) FROM notes').fetchone()[0]
    conn.close()
    return jsonify({'count': count})



@app.route('/notes/<int:id>', methods=['GET'])
def get_note(id):
    conn = get_db_connection()
    note = conn.execute('SELECT * FROM notes WHERE id = ?', (id,)).fetchone()
    conn.close()
    if note is None:
        return jsonify({'error': 'Note not found'}), 404
    return jsonify(dict(note))

@app.route('/notes/add', methods=['POST'])
def create_note():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    if not title or not content:
        return jsonify({'error': 'Title and content are required'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO notes (title, content) VALUES (?, ?)', (title, content))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({'id': new_id, 'title': title, 'content': content}), 201

@app.route('/notes/update/<int:id>', methods=['PUT'])
def update_note(id):
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    if not title or not content:
        return jsonify({'error': 'Title and content are required'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE notes SET title = ?, content = ? WHERE id = ?', (title, content, id))
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'error': 'Note not found'}), 404
    conn.close()
    return jsonify({'id': id, 'title': title, 'content': content})


@app.route('/notes/patch/<int:id>', methods=['PATCH'])
def patch_note(id):
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    if not title and not content:
        return jsonify({'error': 'At least one of title or content is required'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    note = cursor.execute('SELECT * FROM notes WHERE id = ?', (id,)).fetchone()
    if note is None:
        conn.close()
        return jsonify({'error': 'Note not found'}), 404
    new_title = title if title else note['title']
    new_content = content if content else note['content']
    cursor.execute('UPDATE notes SET title = ?, content = ? WHERE id = ?', (new_title, new_content, id))
    conn.commit()
    conn.close()
    return jsonify({'id': id, 'title': new_title, 'content': new_content})

@app.route('/notes/delete/<int:id>', methods=['DELETE'])
def delete_note(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM notes WHERE id = ?', (id,))
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'error': 'Note not found'}), 404
    conn.close()
    return jsonify({'message': 'Note deleted successfully'})

@app.route('/notes/authenticate', methods=['POST'])
def authenticate():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if username == 'admin' and password == 'password':
        return jsonify({'message': 'Authentication successful'})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401
    
@app.route('/notes/secure', methods=['GET'])
def secure_endpoint():
    api_key = request.args.get('api_key')
    if api_key == 'my_secure_api_key':
        return jsonify({'message': 'Access granted to secure endpoint'})
    else:
        return jsonify({'error': 'Invalid API key'}), 403
    
if __name__ == '__main__':
    app.run(debug=True)