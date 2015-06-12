from pyramid.response import Response
from pyramid.view import view_config, view_defaults, forbidden_view_config
from pyramid.security import remember, forget
from pyramid.httpexceptions import HTTPFound

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    Reminder,
    User,
    Group
)


@view_config(route_name='home', renderer='home.mak', permission='edit')
def my_view(request):
    return {'project': 'reminder', 'logged_in': request.authenticated_userid}


@view_config(route_name='users', renderer='json', permission='admin')
def list_users(request):
    """
    Return a json list of Users. Only admins can view
    """
    try:
        users = DBSession.query(User).all()
    except DBAPIError, dbapie:
        print dbapie
        return Response("Error connecting to DB", content_type='text/plain', status_int=500)
    return users


@view_defaults(renderer='json')
class ReminderViews(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='reminders', request_method='POST', permission='edit')
    def create_reminder(self):
        reminder = Reminder(self.request.json_body)
        user = DBSession.query(User).filter(User.email == self.request.authenticated_userid).first()
        if user:
            user.reminders.append(reminder)
        return {}

    @view_config(route_name='reminders', request_method='PUT', permission='edit')
    def update_reminder(self):
        user = DBSession.query(User).filter(User.email == self.request.authenticated_userid).first()
        reminder = DBSession.query(Reminder).get(self.request.json_body['id'])
        if reminder and reminder.user_id == user.id:
            reminder.reminder_deleted = self.request.json_body['reminder_deleted']
            DBSession.add(reminder)
        return {}

    @view_config(route_name='reminders', request_method='GET', permission='view')
    def get_reminders(self):
        user = DBSession.query(User).filter(User.email == self.request.authenticated_userid).first()
        return DBSession.query(Reminder).filter((Reminder.user_id == user.id) &
                                                (Reminder.reminder_deleted == False) &
                                                (Reminder.reminder_sent == False)).all()


@view_config(route_name='login', renderer='login.mak')
@forbidden_view_config(renderer='login.mak')
def login(request):
    login_url = request.route_url('login')
    referrer = request.url
    if referrer == login_url:
        referrer = '/'
    came_from = request.params.get('came_from', referrer)
    message = ''
    email = ''
    password = ''
    if 'form.submitted' in request.params:
        email = request.params['email']
        password = request.params['password']

        user = DBSession.query(User).filter(User.email == email).first()

        if user and user.verify_password(password):
            headers = remember(request, email)
            return HTTPFound(location='/',
                             headers=headers)
        message = 'Failed login'

    return dict(
        message=message,
        url=request.application_url + '/login',
        came_from=came_from,
        email=email,
        password=password
    )


@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(location=request.route_url('login'),
                     headers=headers)


@view_config(route_name='signup', renderer='signup.mak')
def signup(request):
    message = ""
    email = ""
    if 'form.submitted' in request.params:
        email = request.params['email']
        password = request.params['password']
        confirmation = request.params['password_confirmation']

        if password and password == confirmation:
            user = User(email=email, password=password)
            group = DBSession.query(Group).filter(Group.name == 'users').first()
            user.groups.append(group)
            DBSession.add(user)

            headers = remember(request, email)
            return HTTPFound(location='/',
                             headers=headers)

        else:
            message = "Passwords did not match"

    return dict(
        message=message,
        url=request.application_url + '/signup',
        email=email
    )
