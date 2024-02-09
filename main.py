import sqlite3
from flask import Flask, request

app = Flask(__name__)

@app.route('/api/users', methods=['POST'])
def create_user():

    data = request.get_json()

    db = sqlite3.connect('sqlite.db')
    cursor = db.cursor()
    cursor.execute('INSERT INTO users (user_id, user_name, balance) VALUES (?, ?, ?)', (data['user_id'], data['user_name'], data['balance']))
    db.commit()
    db.close()

    return data, 201

if __name__ == '__main__':
    app.run(debug=True, port=8000)
