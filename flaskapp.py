import sqlite3
from flask import Flask, render_template, g, request, redirect, url_for, session, flash

app = Flask(__name__)
app.config['DATABASE'] = '/home/ubuntu/flaskapp/users.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'your_secret_key'


def connect_to_database():
    return sqlite3.connect(app.config['DATABASE'])


def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = connect_to_database()
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


def execute_query(query, args=()):
    cur = get_db().execute(query, args)
    rows = cur.fetchall()
    cur.close()
    return rows


def commit():
    get_db().commit()


@app.route('/')
def mainpage():
    return render_template('mainpage.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/submit', methods=['POST'])
def submit():
    username = request.form['username']
    password = request.form['password']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']

    CREATE_TABLE = '''
        CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        first_name TEXT,
        last_name TEXT,
        email TEXT
         )
    '''
    INSERT_INTO_TABLE = '''
        INSERT INTO users (username, password, first_name, last_name, email)
        VALUES (?, ?, ?, ?, ?)
    '''
    CHECK_USER = ''' SELECT * FROM users WHERE username=?'''
    execute_query(CREATE_TABLE)

    nfile = request.files['textfile']
    wc = "0"  # default val
    if nfile:
        wc = cntWords(nfile)

    user_exists = execute_query(CHECK_USER, (username,))
    commit()

    if user_exists:
        return redirect(url_for('display_details', username=username, password=password, wc=wc))

    execute_query(INSERT_INTO_TABLE, (username, password, first_name, last_name, email))
    commit()

    return redirect(url_for('display_details', username=username, password=password, wc=wc))


@app.route('/display_details')
def display_details():
    username = request.args.get('username')
    password = request.args.get('password')
    wc = request.args.get('wc')

    FETCH_DETAILS = '''
        SELECT * FROM users WHERE username=? AND password=?
    '''
    user_info = execute_query(FETCH_DETAILS, (username, password))
    commit()

    return render_template('display_details.html', user_info=user_info, wc=wc)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        CHECK_USER = '''SELECT * FROM users WHERE username=? AND password=?'''
        user_info = execute_query(CHECK_USER, (username, password))

        if user_info:
            # Store the user's information in the session
            session['user_info'] = user_info[0]

            # Redirect to the user details page
            return redirect(url_for('display_details', username=username, password=password, wc=0))
        else:
            flash('Invalid username or password. Please try again.', 'error')

    return render_template('login.html')


def cntWords(nfile):
    string = nfile.read()
    words = string.split()
    return str(len(words))


if __name__ == '__main__':
    app.run(debug=True)

