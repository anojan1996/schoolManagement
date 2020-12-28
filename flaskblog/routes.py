import os
import secrets
from sqlalchemy import desc

from PIL import Image
from flask_login import login_user, logout_user, login_required

from flaskblog import app, db, bcrypt, authorize
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, \
  studentsForm, attendancesForm, leavesForm
from flaskblog.models import User, students, attendances, leaves, admin_role, \
  teacher_role, student_role, admin_group, teacher_group, \
  student_group, Role, Group

with app.app_context():
  db.session.add(teacher_group)
  db.session.add(student_group)
  db.session.add(admin_group)
  db.session.add(admin_role)
  db.session.add(teacher_role)
  db.session.add(student_role)

  db.session.commit()


@app.route("/")
@app.route("/home")
def home():
  return render_template('home.html')


@app.route("/enter")
def enter():
  return render_template('enter.html')


@app.route("/about")
def about():
  return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
  if current_user.is_authenticated:
    return redirect(url_for('home'))
  form = RegistrationForm()
  if form.validate_on_submit():
    role = Role.query.filter(Role.name == form.role.data).first()
    group = Group.query.filter(Group.name == form.role.data).first()

    hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
        'utf-8')
    user = User(username=form.username.data, email=form.email.data,
                password=hashed_password, roles=[role], groups=[group])

    db.session.add(user)
    db.session.commit()
    flash('Your account has been created! You are now able to log in',
          'success')
    return redirect(url_for('login'))
  return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
    return redirect(url_for('enter'))
  form = LoginForm()
  if form.validate_on_submit():
    user = User.query.filter_by(email=form.email.data).first()
    if user and bcrypt.check_password_hash(user.password, form.password.data):
      login_user(user, remember=form.remember.data)
      next_page = request.args.get('next')
      return redirect(next_page) if next_page else redirect(url_for('enter'))
    else:
      flash('Login Unsuccessful. Please check email and password', 'danger')
  return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
  logout_user()
  return redirect(url_for('home'))


def save_picture(form_picture):
  random_hex = secrets.token_hex(8)
  _, f_ext = os.path.splitext(form_picture.filename)
  picture_fn = random_hex + f_ext
  picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

  output_size = (125, 125)
  i = Image.open(form_picture)
  i.thumbnail(output_size)
  i.save(picture_path)

  return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
  form = UpdateAccountForm()
  if form.validate_on_submit():
    if form.picture.data:
      picture_file = save_picture(form.picture.data)
      current_user.image_file = picture_file
    current_user.username = form.username.data
    current_user.email = form.email.data
    db.session.commit()
    flash('Your account has been updated!', 'success')
    return redirect(url_for('account'))
  elif request.method == 'GET':
    form.username.data = current_user.username
    form.email.data = current_user.email
  image_file = url_for('static',
                       filename='profile_pics/' + current_user.image_file)
  return render_template('account.html', title='Account',
                         image_file=image_file, form=form)


@app.route('/showall')
def show_all():
  return render_template('show_all.html')


@app.route('/new', methods=['GET', 'POST'])
def new():
  form = studentsForm()
  if form.validate_on_submit():
    student = students(username=form.username.data,
                       tamil=form.tamil.data,
                       mathematics=form.mathematics.data,
                       science=form.science.data,
                       english=form.english.data)
    db.session.add(student)
    db.session.commit()
    flash('Marks Added Sucessfully')
    return redirect(url_for('show_all'))
  return render_template('new.html', form=form)


@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
  form = attendancesForm()
  if form.validate_on_submit():
    attendance = attendances(username=form.username.data,
                             no_of_school_days=form.no_of_school_days.data,
                             no_of_days_attended=form.no_of_school_days.data)
    db.session.add(attendance)
    db.session.commit()
    flash('Attendance Added Sucessfully')
    return redirect(url_for('show_all'))
  return render_template('attendance.html', form=form)


@app.route('/leave', methods=['GET', 'POST'])
def leave():
  form = leavesForm()
  if form.validate_on_submit():
    leave = leaves(teacher=form.teacher.data,
                   grade=form.grade.data,
                   no_of_days=form.no_of_days.data,
                   date=form.date.data,
                   reason=form.reason.data)
    db.session.add(leave)
    db.session.commit()
    flash('Leave Form Sucessfully Submitted')
    return redirect(url_for('show_all'))
  return render_template('leave.html', form=form)


@app.route("/view")
@login_required
def view():
  image_file = url_for('static',
                       filename='profile_pics/' + current_user.image_file)
  student = students.query.filter_by(username=current_user.username).first()
  return render_template('view.html', image_file=image_file, title='View',
                         student=student)


"""Notices routes in future we need to seperate this"""

from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import current_user, login_required

from flaskblog import app, db
from flaskblog.forms import NoticeForm
from flaskblog.models import Notice


@app.route("/notice", methods=['GET', 'POST'])
def notices():
  form = NoticeForm()
  if form.validate_on_submit():
    notice = Notice(title=form.title.data, content=form.content.data,
                    author=current_user)
    db.session.add(notice)
    db.session.commit()
    flash(f'your Notice has been created', 'success')
    return redirect(url_for('notices'))
  notices = Notice.query.order_by(desc(Notice.data_posted)).all()
  return render_template('notices.html', notices=notices, form=form)


@app.route("/notice/new", methods=['GET', 'POST'])
@login_required
def new_notice():
  form = NoticeForm()
  if form.validate_on_submit():
    notice = Notice(title=form.title.data, content=form.content.data,
                    author=current_user)
    db.session.add(notice)
    db.session.commit()
    flash(f'your Notice has been created', 'success')
    return redirect(url_for('notice'))
  return render_template('new_notice.html', title='new notice', legend='Notice',
                         form=form)


@app.route("/notice/<int:notice_id>", methods=['GET', 'POST'])
def notice(notice_id):
  form = NoticeForm()
  notice = Notice.query.get_or_404(notice_id)
  if request.method == "POST":
    if not authorize.update('notices'):
      abort(403)
    if form.validate_on_submit():
      print(f"{form.title.data} Form title data")
      notice.title = form.title.data
      notice.content =form.content.data

      db.session.commit()
      flash(f'your Notice has been created', 'success')
      return redirect(url_for('notices'))
  if request.method =="GET":
    form.content.data = notice.content
    form.title.data = notice.title
  return render_template('notice.html', title=notice.title, notice=notice,
                         form=form)


@app.route("/notice/<int:notice_id>/update", methods=['GET', 'POST'])
@login_required
def update_notice(notice_id):
  notice = Notice.query.get_or_404(notice_id)
  if not authorize.update('notices'):
    abort(403)
  form = NoticeForm()
  if form.validate_on_submit():
    notice.title = form.title.data
    notice.content = form.content.data
    db.session.commit()
    flash('Your notice has been updated!', 'success')
    return redirect(url_for('notices', notice_id=notice.id))
  if request.method == 'GET':
    form.title.data = notice.title
    form.content.data = notice.content
  print(str(form))
  return render_template('notice.html', title='Update Notice',
                         form=form, legend='Update Notice', notice=notice)


@app.route("/notice/<int:notice_id>/delete", methods=['POST'])
@login_required
def delete_notice(notice_id):
  notice = Notice.query.get_or_404(notice_id)
  if not authorize.delete('notices'):
    abort(403)
  db.session.delete(notice)
  db.session.commit()
  flash(f'Your notice has been deleted!', 'success')
  return redirect(url_for('notices'))
