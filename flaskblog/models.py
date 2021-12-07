from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from flask_authorize import PermissionsMixin
from flask_authorize import RestrictionsMixin, AllowancesMixin
from flask_login import UserMixin

from flaskblog import db, login_manager,app

# mapping tables
UserGroup = db.Table(
    'user_group', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id'))
)

UserRole = db.Table(
    'user_role', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'))
)


# group
class Group(db.Model, RestrictionsMixin):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)


class Role(db.Model, AllowancesMixin):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Term(db.Model, PermissionsMixin):
    __tablename__ = 'terms'
    __permissions__ = dict(
        owner=['read', 'update', 'delete', 'revoke'],
        group=['read', 'update'],
        other=['read']
    )

    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.Integer, nullable=False)
    term = db.Column(db.Integer, nullable=False)
    marks = db.relationship('Mark', backref='term', lazy=True)
    attendances = db.relationship('Attendance', backref='term', lazy=True)
    # students = db.relationship('User', backref = 'term', lazy =True)


class Subject(db.Model):
    __tablename__ = 'subjects'
    __permissions__ = dict(
        owner=['read', 'update', 'delete', 'revoke'],
        group=['read', 'update'],
        other=['read']
    )
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.Integer)
    marks = db.relationship('Mark', backref='subject', lazy=True)


class Attendance(db.Model):
    __tablename__ = 'attendances'
    __permissions__ = dict(
        owner=['read', 'update', 'delete', 'revoke'],
        group=['read', 'update'],
        other=['read']
    )

    id = db.Column(db.Integer, primary_key=True, auto_increment=True)
    no_of_school_days = db.Column(db.Integer, nullable=False)
    no_of_days_attended = db.Column(db.Integer, nullable=False)
    term_id = db.Column(db.Integer, db.ForeignKey('terms.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    data_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Mark(db.Model):
    __tablename__ = 'marks'

    id = db.Column(db.Integer, primary_key=True)
    result = db.Column(db.Integer, nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'),
                           nullable=False)
    term_id = db.Column(db.Integer, db.ForeignKey('terms.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


"""
Editting by ----------------------------->>>"""


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, auto_increment=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='user.jpg')
    password = db.Column(db.String(60), nullable=False)
    roles = db.relationship('Role', secondary='user_role')
    groups = db.relationship('Group', secondary='user_group')
    notices = db.relationship('Notice', backref='author', lazy=True)
    leaves = db.relationship('Leave', backref='author', lazy=True)
    marks = db.relationship('Mark', backref='student', lazy=True)
    attendances = db.relationship('Attendance', backref='student', lazy=True)

    # term_id = db.Column(db.Integer, db.ForeignKey('terms.id'), nullable=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Notice(db.Model, PermissionsMixin):
    __tablename__ = 'notices'
    __permissions__ = dict(
        owner=['read', 'update', 'delete', 'revoke'],
        group=['read', 'update'],
        other=['read']
    )

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    data_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)

    # user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    def __repr__(self):
        return f"Notice ('{self.title}', " \
               f"'{self.content}')"


class Leave(db.Model, PermissionsMixin):
    __tablename__ = 'leaves'
    __permissions__ = dict(
        owner=['read', 'update', 'delete', 'revoke'],
        group=['read', 'update'],
        other=['read']
    )
    id = db.Column(db.Integer, primary_key=True)
    # teacher = db.Column(db.String(50), nullable=False)
    # grade = db.Column(db.Integer, nullable=False)
    #no_of_days = db.Column(db.Integer, nullable=False)
    # date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    data_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    reason = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Post('{self.teacher}', " \
               f"'{self.grade}', " \
               f"'{self.no_of_days}', " \
               f"'{self.date}', " \
               f"'{self.reason}')"


db.create_all()

student_role = Role(
    name='student',
    # restrictions=dict(
    #     notices=['read'],
    # )
)

teacher_role = Role(
    name='teacher',
    # restrictions=dict(
    #     notices=['read', 'create'],
    # )
)
admin_role = Role(name='admin',
                  # restrictions=dict(
                  #     notices=['read', 'create'],
                  # )
                  )

student_group = Group(
    name='student',
    restrictions=dict(
        notices=['update', 'delete'],
        leaves=['update', 'delete'],
        terms=['update', 'delete'],
        attendances=['update', 'delete'],
        subjects=['update', 'delete'],
    )
)

teacher_group = Group(
    name='teacher',
    restrictions=dict(
        notices=['delete'],
        leaves=['delete'],
        terms=[],
        attendances=[],
        subjects=[],
    )
)
admin_group = Group(name='admin', restrictions=dict(
    notices=[],
    leaves=[],
    terms=[],
    attendances=[],
    subjects=[],
))

"""
Not neeeded 
"""

db.create_all()
