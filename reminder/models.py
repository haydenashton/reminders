import datetime

from passlib.apps import custom_app_context as pwd_context

from sqlalchemy import (
    Column,
    ForeignKey,
    Index,
    Integer,
    Text,
    DateTime,
    Boolean,
    Table,
    func,
    event
)

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    backref
)

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


# Linking table to model many to many relationship between users and groups
user_groups = Table('user_groups', Base.metadata,
                    Column('user_id', Integer, ForeignKey('users.id')),
                    Column('group_id', Integer, ForeignKey('groups.id'))
)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(Text, unique=True)
    password = Column(Text)

    groups = relationship('Group', secondary=user_groups, backref='User')

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)

    def group_names(self):
        return [group.name for group in self.groups]

    def in_group(self, group):
        return group in self.group_names()

    def __json__(self, args):
        return {"id": self.id, "email": self.email, "password": self.password, "groups": self.groups}

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Group(Base):
    """
    Represents the groups that a user belongs to
    """
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    users = relationship('User', secondary=user_groups, backref='Group')

    def __json__(self, args):
        return {"name": self.name}


class Reminder(Base):
    __tablename__ = 'reminders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(Text)
    description = Column(Text)
    reminder_time = Column(DateTime)
    created = Column(DateTime, default=func.now())
    reminder_sent = Column(Boolean, default=False)
    reminder_deleted = Column(Boolean, default=False)

    user = relationship("User", backref=backref('reminders', order_by=id))

    def __init__(self, args):
        reminder_time = datetime.datetime.strptime(args['reminder_time'], "%d/%m/%YT%H:%M")
        super(Reminder, self).__init__(title=args['title'],
                                       description=args['description'],
                                       reminder_time=reminder_time)

    def __json__(self, request):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "reminder_time": self.reminder_time.strftime("%d/%m/%YT%H:%M"),
            "created": self.created.isoformat(),
            "reminder_sent": self.reminder_sent,
            "reminder_deleted": self.reminder_deleted
        }

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


def password_listener(target, value, oldvalue, initiator):
    """
    Hash the password when the value is set.
    """
    return pwd_context.encrypt(value)


# Listen for the password field being set
event.listen(User.password, 'set', password_listener, retval=True)


def user_groups(user_email, request):
    """
    Return the group names user belongs to if user is found
    """
    user = DBSession.query(User).filter(User.email == user_email).first()
    return user.group_names() if user else []



# Indexes
Index('email_index', User.email, unique=True)
Index('date_time_index', Reminder.reminder_time)
