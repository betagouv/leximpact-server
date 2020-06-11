# The LexCeption exception is raised when an error occurs within a
# simulation. It is used to dispatch the error message to the client,
# so messages should be clear for an external Web API user.


class LexCeption(Exception):
    pass
