from flask import Flask, render_template, request, redirect, session, jsonify
import psycopg2
import os
from urllib.parse import urlparse

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database setup
def get_db_connection():
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgres://u2am3popgd6aum:p80e050cc9f97f557acf043e66ec001968f4395e302c74994f5b4b25998b5e011@c5hilnj7pn10vb.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/dekltbc491e3fo')
    result = urlparse(DATABASE_URL)
    username = result.username
    password = result.password
    database = result.path[1:]
    hostname = result.hostname
    port = result.port
    
    return psycopg2.connect(
        database=database,
        user=username,
        password=password,
        host=hostname,
        port=port
    )

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS items (id SERIAL PRIMARY KEY, name TEXT, completed BOOLEAN)''')
    
    # Insert demo user
    demo_username = 'demouser'
    demo_password = 'ThisIsForWPClass'
    c.execute('INSERT INTO users (username, password) VALUES (%s, %s) ON CONFLICT (username) DO NOTHING', (demo_username, demo_password))
    
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/checklist')
def checklist():
    return render_template('checklist.html')

@app.route('/site_description')
def site_description():
    return render_template('site_description.html')

@app.route('/about_us')
def about_us():
    return render_template('about_us.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT password FROM users WHERE username = %s', (username,))
        user = c.fetchone()
        conn.close()
        
        if user and user[0] == password:
            session['username'] = username
            return redirect('/dashboard')
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/login')
    return render_template('dashboard.html', username=session['username'])

@app.route('/data')
def data():
    if 'username' not in session:
        return redirect('/login')
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM items')
    items = c.fetchall()
    conn.close()
    return jsonify(items)

@app.route('/add_item', methods=['POST'])
def add_item():
    if 'username' not in session:
        return redirect('/login')
    data = request.get_json()
    item_name = data.get('name')
    
    if not item_name:
        return jsonify({'success': False, 'message': 'Invalid item name'}), 400

    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO items (name, completed) VALUES (%s, %s)', (item_name, False))
    conn.commit()
    conn.close()

    return jsonify({'success': True})

@app.route('/toggle_item/<int:item_id>', methods=['POST'])
def toggle_item(item_id):
    if 'username' not in session:
        return redirect('/login')
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT completed FROM items WHERE id = %s', (item_id,))
    item = c.fetchone()
    if item:
        new_status = not item[0]
        c.execute('UPDATE items SET completed = %s WHERE id = %s', (new_status, item_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    conn.close()
    return jsonify({'success': False, 'message': 'Item not found'}), 404

@app.route('/delete_item/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    if 'username' not in session:
        return redirect('/login')
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM items WHERE id = %s', (item_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)
