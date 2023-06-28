from flask import Flask, render_template, request, redirect, Markup
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class ToDo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(1000), nullable=False)
    desc = db.Column(db.String(10000), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        todo = ToDo(title=title, desc=desc)
        db.session.add(todo)
        db.session.commit()

    query = request.args.get('q')
    print("Received query:", query)
    if query:
        Todos = ToDo.query.filter(ToDo.title.contains(query) | ToDo.desc.contains(query)).all()
        print("Search results:", Todos)
    else:
        Todos = ToDo.query.all()

    return render_template('index.html', Todos=Todos, query=query)

#this function updates a todo and reloads the data to show the updated data
@app.route('/update/<int:sno>', methods=['GET', 'POST'])
def update(sno):
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        todo = ToDo.query.filter_by(sno=sno).first()
        todo.title = title
        todo.desc = desc
        db.session.add(todo)
        db.session.commit()
        return redirect("/")
    todo = ToDo.query.filter_by(sno=sno).first()

    return render_template('update.html', todo=todo)

#this is the delete function which will delete the todo and reload the page to show the modified data
@app.route('/delete/<int:sno>')
def delete(sno):
    todo = ToDo.query.filter_by(sno=sno).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect("/")

#this part highlights the search text in the list
@app.template_filter('highlight')
def highlight_search_text(text, query):
    if query and query.strip():
        highlighted_text = re.sub(re.escape(query), r'<mark>\g<0></mark>', text, flags=re.IGNORECASE)
        return Markup(highlighted_text)
    return text

if __name__ == "__main__":
    app.run(debug=True)
