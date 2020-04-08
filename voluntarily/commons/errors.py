class BatchMatchException(Exception):
    """
    Base class for all exceptions raised by BatchMatch
    """

class UserExists(BatchMatchException):
    """Thrown when user id already exist in the users index."""
    def __init__(self, message="user already exists", status=409, payload=None):
        self.message = message
        self.status = status
        self.payload = payload