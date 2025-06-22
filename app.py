from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

def init_db():
    if not os.path.exists('library.db'):
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        c.execute('CREATE TABLE books (id INTEGER PRIMARY KEY, title TEXT, author TEXT)')
        c.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)')
        conn.commit()
        conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            flash("Signup successful! Please login.")
            return redirect('/login')
        except sqlite3.IntegrityError:
            flash("Username already taken.")
            return redirect('/signup')
        finally:
            conn.close()
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect('/dashboard')
        else:
            flash("Invalid credentials")
            return redirect('/login')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('dashboard.html', username=session['username'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/add', methods=['GET', 'POST'])
def add_book():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        c.execute('INSERT INTO books (title, author) VALUES (?, ?)', (title, author))
        conn.commit()
        conn.close()
        return redirect('/books')
    return render_template('add_book.html')

@app.route('/books')
def view_books():
    if 'user_id' not in session:
        return redirect('/login')
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute('SELECT * FROM books')
    books = c.fetchall()
    conn.close()
    return render_template('view_books.html', books=books)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
