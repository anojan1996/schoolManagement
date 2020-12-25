from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:''@localhost/details'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'aucaean'

db = SQLAlchemy(app)


class students(db.Model):
    id = db.Column('id', db.Integer, nullable=False, primary_key=True)
    name = db.Column('name', db.String(255), nullable=False)
    city = db.Column('city', db.String(255), nullable=False)

    def __init__(self, id, name, city, addr, pin):
        self.id = int(id)
        self.name = name
        self.city = city
        print(id,name,city,addr,pin)


@app.route('/showall')
def show_all():
    return render_template('show_all.html', students=students.query.all())


@app.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        if not request.form['name'] or not request.form['city'] or not request.form['addr']:
            flash('Please enter all the fields', 'error')
        else:
            student = students(request.form['id'], request.form['name'],
                               request.form['city'],
                               request.form['addr'],
                               request.form['pin'])

            db.session.flush()
            db.session.add(student)
            db.session.commit()
            # students.query.all()
            flash('Record was successfully added')
            return redirect(url_for('show_all'))
    return render_template('new.html')


if __name__ == '__main__':
    id = 0
    db.create_all()
    app.run(debug=True)
