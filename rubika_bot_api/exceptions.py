class APIRequestError(Exception):
    """Raised when an API request fails."""
    pass

class APIResponseError(Exception):
    """Raised when an API request returns an error response."""
    pass

class APIResponseWarning(Exception):
    """Raised when an API request returns a warning response."""
    pass

