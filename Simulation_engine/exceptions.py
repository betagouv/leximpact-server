
class LexCeption(Exception):
    '''
    The LexCeption exception is raised when an error occurs within a
    simulation. It is used to dispatch the error message to the client,
    so messages should be clear for an external Web API user.
    '''
    pass


class ConfigurationException(Exception):
    '''
    Raised when the user ".env" file comes with errors
    whether an environment variable is missing
    or the application couldn't use its configured value.
    '''
    pass
