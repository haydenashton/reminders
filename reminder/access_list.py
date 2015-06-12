from pyramid.security import (
    Allow,
    Everyone
)

class RootFactory(object):
    """
    Set up what permissions groups have.
    """
    __acl__ = [
        (Allow, 'users', 'view'),
        (Allow, 'users', 'edit'),
        (Allow, 'admins', 'admin')
    ]

    def __init__(self, request):
        pass
