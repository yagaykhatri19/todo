from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///TODO.db'
db = SQLAlchemy(app)

def current_time_without_seconds():
    now = datetime.now()
    return now.replace(microsecond=0)

class TODO(db.Model):
    sno = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(200), nullable = False)
    content = db.Column(db.String(500), nullable = True)
    date_created = db.Column(db.DateTime, default=current_time_without_seconds)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"
    
# ~Endpoints~
@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if (request.method=='POST'):
        action = request.form.get('action')
        # print(action)

        # if (action=='search_todo'):
        #     search_query = request.form['search']
        #     todo = TODO.query.filter(TODO.title.contains(search_query) | TODO.content.contains(search_query)).all()
        #     return render_template('index.html', allTodo=todo)
        
        # if (action=='add_todo'):
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
    if (request.method=='POST'):
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
    # print(search_query)
    todo = TODO.query.filter(TODO.title.contains(search_query) | TODO.content.contains(search_query)).all()
    return render_template('search.html', allTodo=todo)
# ~Endpoints~

if (__name__ == "__main__"):
    app.run(debug=True, port=8000)