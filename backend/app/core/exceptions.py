class NotFoundException(Exception):
    """Raised when smth was not found in database"""
    pass


class AlreadyExistsException(Exception):
    """Raised when creation of smth failed due to unique constraint"""
    pass
