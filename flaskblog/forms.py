from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, \
  IntegerField, TextAreaField
from wtforms import validators, ValidationError
from wtforms.fields.html5 import DateField
from wtforms_sqlalchemy.fields import QuerySelectField
from flaskblog.models import User, Subject

class RegistrationForm(FlaskForm):
  username = StringField('Username',
                         [validators.DataRequired("Pleaes enter your name")])
  role = StringField('Role',
                     [validators.DataRequired("Pleaes enter your Role")])
  email = StringField('Email',
                      [validators.DataRequired(
                          "Please enter your email address."),
                        validators.Email("Please enter your email address.")])
  password = PasswordField('Password', [
    validators.DataRequired("Pleaes enter your password")])
  confirm_password = PasswordField('Confirm Password',
                                   [validators.EqualTo("password")])

  submit = SubmitField('Sign Up')

  def validate_username(self, username):
    user = User.query.filter_by(username=username.data).first()
    if user:
      raise ValidationError(
          'That username is taken. Please choose a different one.')

  def validate_email(self, email):
    user = User.query.filter_by(email=email.data).first()
    if user:
      raise ValidationError(
          'That email is taken. Please choose a different one.')

  def validate_role(self, role):
    pass
    # user = Role.query.filter_by(name=role.data).first()
    # if not user:
    #     raise ValidationError('That role is not there. Please choose a different one.')


class LoginForm(FlaskForm):
  email = StringField('Email',
                      [validators.DataRequired(
                          "Please enter your email address."),
                        validators.Email("Please enter your email address.")]
                      )
  password = PasswordField('Password', [
    validators.DataRequired("Pleaes enter your password")])
  remember = BooleanField('Remember Me')
  submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
  username = StringField('Username',
                         [validators.DataRequired("Pleaes enter your name")])
  email = StringField('Email',
                      [validators.DataRequired(
                          "Please enter your email address."),
                        validators.Email("Please enter your email address.")]
                      )
  picture = FileField('Update Profile Picture',
                      validators=[FileAllowed(['jpg', 'png'])])
  submit = SubmitField('Update')



class Report(FlaskForm):

  studentName = StringField('Student Name', [
    validators.DataRequired("Please enter the student name")])
  term = IntegerField('Term')
  grade = IntegerField('Grade')
  english = StringField('English')
  science = StringField('Science')
  maths = StringField("Maths")
  tamil = StringField("Tamil")
  sinhala = StringField("Sinhala")

  submit = SubmitField('Submit')


class attendancesForm(FlaskForm):
  student_id = IntegerField('Student Id')
  student_name = StringField('Student Name',
                         [validators.DataRequired("Pleaes enter the username")])
  student_grade = IntegerField("Grade")
  student_term = IntegerField("Term")

  no_of_school_days = IntegerField('No Of School Days')
  no_of_days_attended = IntegerField('No Of Days Attended')
  submit = SubmitField('Submit')

  def validate_username(self, username):
    user = User.query.filter_by(username=username.data).first()
    if user:
      raise ValidationError(
          'That username is taken. Please choose a different one.')


class LeaveForm(FlaskForm):
  #teacher = StringField('Teacher Name')
  #grade = IntegerField('Grade')
  no_of_days = IntegerField('No Of Days')
  #date = DateField('Date', format='%y-%m-%d')
  reason = TextAreaField('Reason')
  submit = SubmitField('Submit')


class NoticeForm(FlaskForm):
  title = StringField('Title')
  content = TextAreaField('Content')
  submit = SubmitField('Submit')


class SubjectForm(FlaskForm):
  name = StringField('Subject Name')
  grade = IntegerField("Grade")
  submit = SubmitField('Submit')


class TermForm(FlaskForm):
  grade = IntegerField("Grade")
  term_no = IntegerField("Term")
  submit = SubmitField('Submit')
