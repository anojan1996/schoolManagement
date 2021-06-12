import os
import secrets
from itertools import groupby
from operator import attrgetter

from PIL import Image
from flask_login import login_user, logout_user, login_required
from sqlalchemy import desc

from flaskblog import app, db, bcrypt, authorize
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, \
  Report, attendancesForm, LeaveForm, SubjectForm, TermForm
from flaskblog.models import User, Attendance, Leave, admin_role, \
  teacher_role, student_role, admin_group, teacher_group, \
  student_group, Role, Group, Mark, Subject, Term, UserGroup

with app.app_context():
  if not Group.query.limit(1).all():
    # Adding groups if no groups exist
    db.session.add(admin_group)
    db.session.add(teacher_group)
    db.session.add(student_group)

    # adding roles if no roles exists
    db.session.add(admin_role)
    db.session.add(teacher_role)
    db.session.add(student_role)
    db.session.commit()


@app.route("/")
@app.route("/home")
def home():
  if current_user.is_authenticated:
    group_id = current_user.groups[0].id
    return render_template('enter.html', group_id =group_id)

  return render_template('home.html')


@app.route("/not_found")
def not_found():
  return render_template('not_found.html')


@app.route("/enter")
@login_required
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
    # We added role in form this is used for group and role
    role = Role.query.filter(Role.name == form.role.data).first()
    group = Group.query.filter(Group.name == form.role.data).first()

    hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
        'utf-8')
    user = User(username=form.username.data, email=form.email.data,
                password=hashed_password, roles=[role], groups=[group])
    print(user)
    db.session.add(user)
    db.session.commit()
    login_user(user)
    flash(f"Account Created Successfully! You are now logged in as {user.username}", category='success')
    return redirect(url_for('enter'))
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
      flash(f'Success! You are logged in as: {user.username}', category='success')
      return redirect(next_page) if next_page else redirect(url_for('enter'))
    else:
      flash('Login Unsuccessful. Please check email and password', 'danger')
  return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
  logout_user()
  flash("You have been logged out!", category='info')
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






@app.route("/view")
@login_required
def view():
  image_file = url_for('static',
                       filename='profile_pics/' + current_user.image_file)
  student = User.query.filter_by(username=current_user.username).first()
  return render_template('view.html', image_file=image_file, title='View',
                         student=student)


"""Notices routes in future we need to seperate this"""

from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import current_user, login_required

from flaskblog import app, db
from flaskblog.forms import NoticeForm
from flaskblog.models import Notice


@app.route("/notices", methods=['GET', 'POST'])
@login_required
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

@app.route('/leave', methods=['GET', 'POST'])
@login_required
def leave():
  form = LeaveForm()
  if form.validate_on_submit():
    leave = Leave(#teacher=form.teacher.data,
                   #grade=form.grade.data,
                   no_of_days=form.no_of_days.data,
                   #date=form.date.data,
                   reason=form.reason.data,
                   author=current_user)
    db.session.add(leave)
    db.session.commit()
    flash(f'Leave Form Sucessfully Submitted','success')
    return redirect(url_for('leave'))
  leaves = Leave.query.order_by(desc(Leave.data_posted)).all()
  return render_template('leaves.html', form=form, leaves=leaves)


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
      notice.content = form.content.data

      db.session.commit()
      flash(f'your Notice has been created', 'success')
      return redirect(url_for('notices'))
  if request.method == "GET":
    form.content.data = notice.content
    form.title.data = notice.title
  return render_template('notice.html', title=notice.title, notice=notice,
                         form=form)

@app.route("/leaves/<int:leave_id>", methods=['GET', 'POST'])
def leaves(leave_id):
  form = LeaveForm()
  leave = Leave.query.get_or_404(leave_id)
  if request.method == "POST":
    if not authorize.update('leaves'):
      abort(403)
    if form.validate_on_submit():
      print(f"{form.no_of_days.data} Form no_of_days data")
      leave.no_of_days = form.no_of_days.data
      leave.reason = form.reason.data

      db.session.commit()
      flash(f'your Leave has been created', 'success')
      return redirect(url_for('leave'))
  if request.method == "GET":
    form.reason.data = leave.reason
    form.no_of_days.data = leave.no_of_days
  return render_template('leave.html', no_of_days=leave.no_of_days, leave=leave,
                         form=form)



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

@app.route("/leaves/<int:leave_id>/delete", methods=['POST'])
@login_required
def delete_leave(leave_id):
  leave = Leave.query.get_or_404(leave_id)
  if not authorize.delete('leaves'):
    abort(403)
  db.session.delete(leave)
  db.session.commit()
  flash(f'Your leave has been deleted!', 'success')
  return redirect(url_for('leave'))


@app.route("/students", methods=['GET'])
@login_required
def students():
  studentsGroups = db.session.query(UserGroup).filter_by(group_id=3).all()
  students = []
  if studentsGroups:
    for record in studentsGroups:
      print(f"Record Id --> {record.user_id}")
      user = User.query.get(record.user_id)
      students.append(user)

  else:
    print("No Students in the database")

  print(students)
  return render_template('studentsData.html', students=students,
                         total=len(students))


@app.route("/students/<int:id>", methods=['GET', 'POST'])
def studentById(id):
  user_group = db.session.query(UserGroup).filter_by(user_id=id).first()
  if user_group.group_id == 3:
    student = User.query.get(id)
    form = UpdateAccountForm()
    if form.validate_on_submit():
      if form.picture.data:
        picture_file = save_picture(form.picture.data)
        student.image_file = picture_file
      student.username = form.username.data
      student.email = form.email.data
      db.session.commit()
      flash('Your account has been updated!', 'success')
      return redirect(url_for('students'))
    form.username.data = student.username
    form.email.data = student.email
    image_file = url_for('static',
                         filename='profile_pics/' + student.image_file)
    return render_template('account.html', title='Student Profile',
                           image_file=image_file, form=form)

  else:
    print("This user id is not  a student")


# TODO
@app.route("/students/<int:student_id>/reports", methods=["GET", "POST"])
def reportsByStudentId(student_id):
  if db.session.query(UserGroup).filter_by(
      user_id=student_id).first().group_id != 3:
    return redirect(url_for('not_found'))
  reports = []
  marks = Mark.query.filter_by(student_id=student_id).all()
  student = User.query.get(student_id)

  student_name = student.username
  subjects_query = Subject.query.filter_by(grade=1).all()
  form = Report()
  form.studentName.data = student_name
  if form.validate_on_submit():
    term = db.session.query(Term).filter_by(term=form.term.data,
                                            grade=form.grade.data).first()
    subjects = [form.english, form.science, form.maths, form.tamil,
                form.sinhala]
    subjects_query_dict = {}
    subjects_form_dict = {}
    for sub in subjects_query:
      subjects_query_dict[sub.name.lower()] = sub
    for sub in subjects:
      subjects_form_dict[sub.name.lower()] = sub

    for sub_name in subjects_form_dict.keys():
      mark = Mark(result=subjects_form_dict[sub_name].data, term_id=term.id,
                  subject_id=subjects_query_dict[sub_name].id,
                  student_id=student_id)
      db.session.add(mark)
    db.session.commit()
    flash(f'your Marks is added', 'success')
    return redirect(url_for('reportsByStudentId', student_id=student_id))

  for term_id, term_marks in groupby(marks, attrgetter('term_id')):
    report = {'student_name': student_name, 'student_id': student_id}

    term = Term.query.get(term_id)
    report['term'] = term.term
    report['grade'] = term.grade
    report['aggregate_term_id'] = term.id
    marks = {}
    for mark in term_marks:
      subject_id = mark.subject_id
      subject_name = Subject.query.get(subject_id).name
      mark = mark.result
      marks[subject_name] = mark
    report['term_marks'] = marks
    reports.append(report)
  # return jsonify({'reports': str(reports)})

  return render_template('studentReports.html', reports=reports, form=form)


@app.route("/students/<int:student_id>/reports/<int:term_id>",
           methods=["GET", "POST", "DELETE"])
def reportByTermIdAndStudentId(student_id, term_id):
  report = {}
  report['student_id'] = student_id
  student = User.query.get(student_id)
  report['student_name'] = student.username
  marks = Mark.query.filter_by(student_id=student_id,
                               term_id=term_id).all()
  marks_dict = {}
  for mark in marks:
    marks_dict[Subject.query.get(mark.subject_id).name] = mark.result
  term = Term.query.get(term_id)
  report['term'] = term.term
  report['grade'] = term.grade
  report['aggregate_term_id'] = term_id
  report['term_marks'] = marks_dict

  student_name = student.username
  subjects_query = Subject.query.filter_by(grade=1).all()
  form = Report()
  form.studentName.data = student_name
  form.grade.data = report['grade']
  form.term.data = report['term']
  subjects = [form.english, form.science, form.maths, form.tamil,
              form.sinhala]
  subjects_query_dict = {}
  subjects_form_dict = {}

  for sub in subjects_query:
    subjects_query_dict[sub.name.lower()] = sub
  for sub in subjects:
    subjects_form_dict[sub.name.lower()] = sub
    sub.data = marks_dict[sub.name.capitalize()]

  if request.method == "POST":
    if form.validate_on_submit():
      term = db.session.query(Term).filter_by(term=form.term.data,
                                              grade=form.grade.data).first()

      for sub_name in subjects_form_dict.keys():
        mark = Mark(result=subjects_form_dict[sub_name].data, term_id=term.id,
                    subject_id=subjects_query_dict[sub_name].id,
                    student_id=student_id)
        db.session.add(mark)
      db.session.commit()
      flash(f'your Marks is updated', 'success')
      return redirect(url_for('reportsByStudentId', student_id=student_id))

  return render_template('report.html', report=report, form=form)


@app.route("/reports", methods=['GET', 'POST'])
@login_required
def reports():
  form = Report()
  reports = []
  marks = Mark.query.order_by(Mark.term_id, Mark.student_id).all()
  for student_id, student_marks in groupby(marks, attrgetter('student_id')):
    student_name = User.query.get(student_id).username
    report = {'student_name': student_name, 'student_id': student_id}
    for term_id, term_marks in groupby(student_marks, attrgetter('term_id')):
      term = Term.query.get(term_id)
      report['term'] = term.term
      report['grade'] = term.grade
      report['aggregate_term_id'] = term.id
      marks = {}
      for mark in term_marks:
        subject_id = mark.subject_id
        subject_name = Subject.query.get(subject_id).name
        mark = mark.result
        marks[subject_name] = mark
      report['term_marks'] = marks
      reports.append(report)

  if request.method == "POST":
    subjects_query = Subject.query.filter_by(grade=1).all()
    student = User.query.filter_by(username=form.studentName.data).first()
    if not student:
      print(f"Hello {form.studentName.data.lower()}")
      print(student)
    student_id = student.id
    student_name = student.username
    if form.validate_on_submit():
      term = db.session.query(Term).filter_by(term=form.term.data,
                                              grade=form.grade.data).first()
      subjects = [form.english, form.science, form.maths, form.tamil,
                  form.sinhala]
      subjects_query_dict = {}
      subjects_form_dict = {}
      for sub in subjects_query:
        subjects_query_dict[sub.name.lower()] = sub
      for sub in subjects:
        subjects_form_dict[sub.name.lower()] = sub

      for sub_name in subjects_form_dict.keys():
        mark = Mark(result=subjects_form_dict[sub_name].data, term_id=term.id,
                    subject_id=subjects_query_dict[sub_name].id,
                    student_id=student_id)
        db.session.add(mark)
      db.session.commit()
      flash(f'your Marks is added', 'success')
      return redirect(url_for('reports'))
  return render_template('reports.html', reports=reports, form=form)


@app.route("/students/<int:student_id>/reports/<int:term_id>/delete",
           methods=["GET", "POST"])
def deleteReport(student_id, term_id):
  report = {}
  report['student_id'] = student_id
  student = User.query.get(student_id)
  report['student_name'] = student.username
  marks = Mark.query.filter_by(student_id=student_id,
                               term_id=term_id).all()
  marks_dict = {}
  for mark in marks:
    marks_dict[Subject.query.get(mark.subject_id).name] = mark.result
  term = Term.query.get(term_id)
  report['term'] = term.term
  report['grade'] = term.grade
  report['aggregate_term_id'] = term_id
  report['term_marks'] = marks_dict

  student_name = student.username
  subjects_query = Subject.query.filter_by(grade=1).all()
  form = Report()
  form.studentName.data = student_name
  subjects = [form.english, form.science, form.maths, form.tamil,
              form.sinhala]
  subjects_query_dict = {}
  subjects_form_dict = {}

  for sub in subjects_query:
    subjects_query_dict[sub.name.lower()] = sub
  for sub in subjects:
    subjects_form_dict[sub.name.lower()] = sub
    sub.data = marks_dict[sub.name.capitalize()]

  if request.method == "POST":
    for mark in marks:
      db.session.delete(mark)
    db.session.commit()
    return redirect(url_for('reportsByStudentId', student_id=student_id))

  return render_template('report.html', report=report)




@app.route('/subjects', methods=['GET', 'POST'])
@login_required
def subjects():
  form = SubjectForm()
  if request.method == "GET":
    subjects = Subject.query.all()
  if request.method == "POST":
    if form.validate_on_submit():
      subject = Subject(name=form.name.data, grade=form.grade.data)
      db.session.add(subject)
      db.session.commit()
      return redirect(url_for('subjects'))
  return render_template('subjects.html', form=form, subjects=subjects)


@app.route('/terms', methods=['GET', 'POST'])
@login_required
def terms():
  form = TermForm()
  if request.method == "GET":
    terms = Term.query.order_by(Term.grade).all()
    print(terms)

  if request.method == "POST":
    if form.validate_on_submit():
      term = Term(grade=form.grade.data, term=form.term_no.data)
      print(term)
      db.session.add(term)
      db.session.commit()
      return redirect(url_for('terms'))
  return render_template('terms.html', form=form, terms=terms)





#Attendances routes


@app.route('/attendances', methods=['GET', 'POST'])
@login_required
def attendances():
  student_attendances = Attendance.query.order_by(
    desc(Attendance.data_posted)).all()
  form = attendancesForm()
  if form.validate_on_submit():
    term = Term.query.filter_by(term=form.student_term.data,
                                grade=form.student_grade.data).first()
    print(term.term)
    student = User.query.filter_by(id=form.student_id.data).first()

    student_attendance = Attendance(student_id=student.id,
                                    no_of_school_days=form.no_of_school_days.data,
                                    no_of_days_attended=form.no_of_days_attended.data,
                                    term_id=term.id)
    db.session.add(student_attendance)
    db.session.commit()
    flash('Attendance Added Sucessfully')
    return redirect(url_for('attendances'))
  return render_template('attendances.html', attendances=student_attendances,
                         form=form)

@app.route('/students/<int:student_id>/attendances', methods= ['GET', 'POST'])
def attendancesByStudentId(student_id):
  student_attendances = Attendance.query.filter_by(student_id = student_id).order_by(
    desc(Attendance.data_posted)).all()
  form = attendancesForm()
  student = User.query.filter_by(id = student_id).first()
  form.student_id.data = student.id
  form.student_name.data =student.username
  if form.validate_on_submit():
    term = Term.query.filter_by(term=form.student_term.data,
                                grade=form.student_grade.data).first()
    print(term.term)
    student = User.query.filter_by(id=form.student_id.data).first()

    student_attendance = Attendance(student_id=student.id,
                                    no_of_school_days=form.no_of_school_days.data,
                                    no_of_days_attended=form.no_of_days_attended.data,
                                    term_id=term.id)
    db.session.add(student_attendance)
    db.session.commit()
    flash('Attendance Added Sucessfully')
    return redirect(url_for('attendances'))
  return render_template('attendances.html', attendances=student_attendances,
                         form=form)

