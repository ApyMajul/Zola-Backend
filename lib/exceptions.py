"""
Provides Exceptions to be used by all apps.
"""
class LeviathanException(Exception):
    """
    Root Exception Class.

    Should no be used directly as it is too broad: use for inheritance.
    """
    ...


class LeviathanAuthException(LeviathanException):
    """
    Authentication-related exception.
    """
    ...


class LeviathanRegistrationException(LeviathanAuthException):
    """
    Registration-related exception.
    """
    ...

