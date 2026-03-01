class ApiError(Exception):
    """API error with status and subStatus fields matching TIDAL API responses."""

    def __init__(self, status=None, subStatus=None, userMessage=None, **kwargs):
        self.status = status
        self.sub_status = subStatus
        self.user_message = userMessage
        message = userMessage or f"API Error {status}"
        super().__init__(message)

    def __repr__(self):
        return f"ApiError(status={self.status}, sub_status={self.sub_status}, message={self.user_message})"


class AuthError(ApiError):
    """Raised for authentication errors (401)."""
    pass


class RateLimitError(ApiError):
    """Raised for rate limit errors (429)."""
    def __init__(self, message=None, retry_after=None, **kwargs):
        super().__init__(status=429, userMessage=message, **kwargs)
        self.retry_after = retry_after
