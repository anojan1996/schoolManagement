from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = 'random string'


@app.route("/about")
def about():
    return render_template('1.html')


@app.route('/Admin')
def admin():
    return render_template('index.html')

@app.route('/Teacher')
def teacher():
    return render_template('teacher.html')

@app.route('/Student')
def student():
    return render_template('student1.html')


@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or \
                request.form['password'] != 'admin':
            error = 'Invalid username or password. Please try again!'
        else:
            return redirect(url_for('admin'))

        if request.method == 'POST':
            if request.form['username'] != 'teacher' or \
                    request.form['password'] != 'teacher':
                error = 'Invalid username or password. Please try again!'
            else:
                return redirect(url_for('teacher'))

            if request.method == 'POST':
                if request.form['username'] != 'student' or \
                        request.form['password'] != 'student':
                    error = 'Invalid username or password. Please try again!'
                else:
                    return redirect(url_for('student'))

    return render_template('login3.html', error = error)


if __name__ == "__main__":
    app.run(debug=True)