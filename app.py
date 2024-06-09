from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt

app = Flask(__name__)

# Primary database for TODO
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///TODO.db'

# Secondary database for User
app.config['SQLALCHEMY_BINDS'] = {
    'user_db': 'sqlite:///users.db'
}

db = SQLAlchemy(app)

app.secret_key = 'secret_key'

def current_time_without_seconds():
    now = datetime.now()
    return now.replace(microsecond=0)

# Model for TODO database
class TODO(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.String(500), nullable=True)
    date_created = db.Column(db.DateTime, default=current_time_without_seconds)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"

# Model for User database
class User(db.Model):
    __bind_key__ = 'user_db'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120), nullable=False)

    def __init__(self, email, password, name):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

    def __repr__(self):
        return f'<User {self.username}>'


# ~Endpoints~
@app.route('/', methods=['GET', 'POST'])
def main():
    if 'name' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_todo':
            title = request.form['_title']
            desc = request.form['desc']
            todo = TODO(title=title, content=desc)
            db.session.add(todo)
            db.session.commit()
            return redirect('/')
        
    allTodo = TODO.query.all()
    return render_template('index.html', allTodo=allTodo)

@app.route('/update/<int:sno>', methods=['GET', 'POST'])
def update(sno):
    if request.method == 'POST':
        title = request.form['_title']
        desc = request.form['desc']
        todo = TODO.query.filter_by(sno=sno).first()
        todo.title = title
        todo.content = desc
        db.session.add(todo)
        db.session.commit()
        return redirect('/')

    todo = TODO.query.filter_by(sno=sno).first()
    return render_template('update.html', allTodo=todo)

@app.route('/delete/<int:sno>')
def delete(sno):
    todo = TODO.query.filter_by(sno=sno).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect('/')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    search_query = request.form['search'].strip()
    if not search_query:
        # If the search query is empty, return a message or redirect
        return render_template('search.html', allTodo=[])
    todo = TODO.query.filter(TODO.title.contains(search_query) | TODO.content.contains(search_query)).all()
    return render_template('search.html', allTodo=todo)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        if name and email and password:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return render_template('register.html', error='Email is already registered.')
            user = User(name=name, email=email, password=password)
            db.session.add(user)
            db.session.commit()
            return redirect('/login')
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['name'] = user.name
            session['email'] = user.email
            session['password'] = user.password
            return redirect('/')
        else:
            return render_template('login.html', error='Invalid user.')
        
    return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('name', None)
    return redirect('login')
# ~Endpoints~

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8000)