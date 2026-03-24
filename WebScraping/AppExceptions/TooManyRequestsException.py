class TooManyRequestsException(Exception):
    def __init__(self, message="Too Many Requests", url=None, retry_after=None):
        super().__init__(message)
        self.url = url
        self.retry_after = retry_after