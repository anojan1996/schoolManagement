from datetime import datetime
from flaskblog import db, login_manager
from flask_login import UserMixin

from flask_authorize import RestrictionsMixin, AllowancesMixin
from flask_authorize import PermissionsMixin

# mapping tables
UserTeam = db.Table(
    'user_group', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('team.id'))
)

UserRole = db.Table(
    'user_role', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)


class Team(db.Model, RestrictionsMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)


class Role(db.Model, AllowancesMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, auto_increment=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    roles = db.relationship('Role', secondary=UserRole)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


class students(db.Model):
    student_id = db.Column(db.Integer, primary_key=True, auto_increment=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    tamil = db.Column(db.Integer, nullable=False)
    mathematics = db.Column(db.Integer, nullable=False)
    science = db.Column(db.Integer, nullable=False)
    english = db.Column(db.Integer, nullable=False)
    id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.username}', " \
               f"'{self.tamil}', " \
               f"'{self.mathematics}', " \
               f"'{self.science}', " \
               f"'{self.english}')"


class attendances(db.Model):
    attendance_id = db.Column(db.Integer, primary_key=True, auto_increment=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    no_of_school_days = db.Column(db.Integer, nullable=False)
    no_of_days_attended = db.Column(db.Integer, nullable=False)
    id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.username}', " \
               f"'{self.no_of_school_days}', " \
               f"'{self.no_of_days_attended}')"


class leaves(db.Model):
    leave_id = db.Column(db.Integer, primary_key=True, auto_increment=True)
    teacher = db.Column(db.String(50), nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    no_of_days = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    reason = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Post('{self.teacher}', " \
               f"'{self.grade}', " \
               f"'{self.no_of_days}', " \
               f"'{self.date}', " \
               f"'{self.reason}')"


class notices(db.Model, PermissionsMixin):
    __permissions__ = dict(
        admin=['create', 'delete', 'update', 'view'],
        teacher=['create', 'delete', 'update', 'view'],
        student=['view']
    )

    notice_id = db.Column(db.Integer, primary_key=True, auto_increment=True)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', " \
               f"'{self.content}')"
