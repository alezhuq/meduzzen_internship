class UserNotFoundException(Exception):
    """Raised when user was not found in database"""
    pass


class UserAlreadyexistsException(Exception):
    """Raised when user creation failed due to unique constraint"""
    pass
