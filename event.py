from flask import Flask, render_template_string, request, redirect, url_for
import os
import sqlite3
import mysql.connector

app = Flask(__name__)

# Detect if running on Railway
ON_RAILWAY = 'MYSQLHOST' in os.environ

def get_db_connection():
    if ON_RAILWAY:
        # Use Railway MySQL in production
        return mysql.connector.connect(
            host=os.environ['MYSQLHOST'],
            user=os.environ['MYSQLUSER'],
            password=os.environ['MYSQLPASSWORD'],
            database=os.environ['MYSQLDATABASE'],
            port=int(os.environ.get('MYSQLPORT', 3306))
        )
    else:
        # Use SQLite locally (no XAMPP needed!)
        conn = sqlite3.connect('events.db')
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    if ON_RAILWAY:
        # MySQL table creation
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                event_date DATE NOT NULL,
                location VARCHAR(200) NOT NULL,
                description TEXT
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
    else:
        # SQLite table creation (local testing)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                event_date TEXT NOT NULL,
                location TEXT NOT NULL,
                description TEXT
            )
        """)
        # Add sample data if table is empty
        cursor.execute("SELECT COUNT(*) FROM events")
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.execute("""
                INSERT INTO events (name, event_date, location, description) VALUES
                ('Cloud Computing Workshop', '2026-04-10', 'Room 101', 'Learn about PaaS deployment'),
                ('Career Fair', '2026-04-15', 'Main Hall', 'Meet potential employers'),
                ('Hackathon Kickoff', '2026-04-20', 'Online', '24-hour coding competition')
            """)
            conn.commit()
        conn.close()
    print("✅ Database ready")

# HTML + CSS + JavaScript all in one template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>📅 Event Scheduler</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #333;
            margin-bottom: 20px;
            text-align: center;
        }
        .add-btn {
            display: inline-block;
            background: #28a745;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .add-btn:hover { background: #218838; }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background: #667eea;
            color: white;
        }
        tr:hover { background: #f5f5f5; }
        .edit-btn {
            background: #ffc107;
            color: #333;
            padding: 5px 10px;
            text-decoration: none;
            border-radius: 3px;
            margin-right: 5px;
        }
        .delete-btn {
            background: #dc3545;
            color: white;
            padding: 5px 10px;
            text-decoration: none;
            border-radius: 3px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input, textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        button {
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover { background: #5a67d8; }
        .back-link {
            display: inline-block;
            margin-top: 20px;
            color: #667eea;
            text-decoration: none;
        }
        .empty {
            text-align: center;
            padding: 40px;
            color: #999;
        }
    </style>
</head>
<body>
    <div class="container">
        {% if request.endpoint == 'index' %}
            <h1>📅 Event Scheduler</h1>
            <a href="/add" class="add-btn">+ Add New Event</a>
            
            <table>
                <thead>
                    <tr><th>Event Name</th><th>Date</th><th>Location</th><th>Actions</th></tr>
                </thead>
                <tbody>
                    {% for event in events %}
                    <tr>
                        <td>{{ event['name'] }}</td>
                        <td>{{ event['event_date'] }}</td>
                        <td>{{ event['location'] }}</td>
                        <td>
                            <a href="/edit/{{ event['id'] }}" class="edit-btn">Edit</a>
                            <a href="/delete/{{ event['id'] }}" class="delete-btn" onclick="return confirm('Delete this event?')">Delete</a>
                        </td>
                    </tr>
                    {% else %}
                    <tr><td colspan="4" class="empty">No events yet. Click "Add New Event" to create one!</td></tr>
                    {% endfor %}
                </tbody>
            </table>
            
        {% elif request.endpoint == 'add_event' %}
            <h1>➕ Add New Event</h1>
            <form method="POST">
                <div class="form-group">
                    <label>Event Name:</label>
                    <input type="text" name="name" required>
                </div>
                <div class="form-group">
                    <label>Date:</label>
                    <input type="date" name="event_date" required>
                </div>
                <div class="form-group">
                    <label>Location:</label>
                    <input type="text" name="location" required>
                </div>
                <div class="form-group">
                    <label>Description (optional):</label>
                    <textarea name="description" rows="3"></textarea>
                </div>
                <button type="submit">Save Event</button>
                <a href="/" class="back-link">← Back to Events</a>
            </form>
            
        {% elif request.endpoint == 'edit_event' %}
            <h1>✏️ Edit Event</h1>
            <form method="POST">
                <div class="form-group">
                    <label>Event Name:</label>
                    <input type="text" name="name" value="{{ event['name'] }}" required>
                </div>
                <div class="form-group">
                    <label>Date:</label>
                    <input type="date" name="event_date" value="{{ event['event_date'] }}" required>
                </div>
                <div class="form-group">
                    <label>Location:</label>
                    <input type="text" name="location" value="{{ event['location'] }}" required>
                </div>
                <div class="form-group">
                    <label>Description:</label>
                    <textarea name="description" rows="3">{{ event['description'] or '' }}</textarea>
                </div>
                <button type="submit">Update Event</button>
                <a href="/" class="back-link">← Back to Events</a>
            </form>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, event_date, location, description FROM events ORDER BY event_date")
    events = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template_string(HTML_TEMPLATE, events=events, request=request)

@app.route('/add', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        name = request.form['name']
        event_date = request.form['event_date']
        location = request.form['location']
        description = request.form.get('description', '')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        if ON_RAILWAY:
            cursor.execute(
                "INSERT INTO events (name, event_date, location, description) VALUES (%s, %s, %s, %s)",
                (name, event_date, location, description)
            )
        else:
            cursor.execute(
                "INSERT INTO events (name, event_date, location, description) VALUES (?, ?, ?, ?)",
                (name, event_date, location, description)
            )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index'))
    
    return render_template_string(HTML_TEMPLATE, request=request)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_event(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        name = request.form['name']
        event_date = request.form['event_date']
        location = request.form['location']
        description = request.form.get('description', '')
        
        if ON_RAILWAY:
            cursor.execute(
                "UPDATE events SET name=%s, event_date=%s, location=%s, description=%s WHERE id=%s",
                (name, event_date, location, description, id)
            )
        else:
            cursor.execute(
                "UPDATE events SET name=?, event_date=?, location=?, description=? WHERE id=?",
                (name, event_date, location, description, id)
            )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index'))
    
    if ON_RAILWAY:
        cursor.execute("SELECT id, name, event_date, location, description FROM events WHERE id=%s", (id,))
    else:
        cursor.execute("SELECT id, name, event_date, location, description FROM events WHERE id=?", (id,))
    event = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template_string(HTML_TEMPLATE, event=event, request=request)

@app.route('/delete/<int:id>')
def delete_event(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    if ON_RAILWAY:
        cursor.execute("DELETE FROM events WHERE id=%s", (id,))
    else:
        cursor.execute("DELETE FROM events WHERE id=?", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)