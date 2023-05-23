from werkzeug.security import generate_password_hash, check_password_hash
from .. import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(512), nullable=False)

    def __init__(self, username):
        self.username = username

    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True

    def get_id(self):
        return str(self.id)

    def get_roles(self):
        roles = []
        for role_assignment in self.role_assignments:
            if (role_assignment.role is not None
                    and role_assignment.role.active):
                roles.append(role_assignment.role.name)
        return ', '.join(roles)

    def set_role(self, role_name):
        self.remove_roles()
        RoleAssignment.create(role_name, self.id)
        db.session.commit()
        return True

    def remove_roles(self):
        for role_assignment in self.role_assignments:
            if role_assignment.role is not None:
                RoleAssignment.remove(role_assignment.role.name, self.id)
        db.session.commit()
        return True

    def remove(self):
        self.remove_roles()
        self.movies.clear()
        User.query.filter(User.id == self.id).delete()
        db.session.commit()
        return True

    def has_role(self, role):
        return any(role == role_assignment.role.name
                   and role_assignment.role.active
                   for role_assignment in self.role_assignments)

    def set_username(self, username):
        self.username = username

    def set_password(self, password):
        self.password = generate_password_hash(password, method='sha256')

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Role(db.Model):
    name = db.Column(db.VARCHAR(100), primary_key=True)
    active = db.Column(db.Boolean, default=True, nullable=False)

    def __init__(self, name, active=True):
        self.name = name
        self.active = active

    @staticmethod
    def create(name, active=True):
        rv = Role(name, active)
        db.session.add(rv)
        db.session.commit()
        return rv

    @staticmethod
    def get(role_name):
        role = Role.query.filter(Role.name == role_name).first()
        return role


class RoleAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.VARCHAR(100), db.ForeignKey('role.name'),
                          nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    role = db.relationship('Role',
                           backref=db.backref('role_assignments',
                                              lazy='joined'),
                           lazy='joined')
    user = db.relationship('User',
                           backref=db.backref('role_assignments',
                                              lazy='joined'),
                           lazy='joined')

    def __init__(self, role_name, user_id):
        self.role_name = role_name
        self.user_id = user_id

    @staticmethod
    def create(role_name, user_id):
        rv = RoleAssignment(role_name, user_id)
        db.session.add(rv)
        db.session.commit()
        return rv

    @staticmethod
    def get(id):
        rv = RoleAssignment.query.filter(RoleAssignment.id == id).first()
        return rv

    @staticmethod
    def remove(role_name, user_id):
        RoleAssignment.query.filter(
            RoleAssignment.role_name == role_name).filter(
                RoleAssignment.user_id == user_id).delete()
        db.session.commit()
        return True
