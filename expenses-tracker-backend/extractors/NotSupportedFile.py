class NotSupportedFile(Exception):
    """Exception raised when a file type is not supported."""

    def __init__(self, filename: str | None, message: str | None = None):
        if filename and not message:
            message = f"File '{filename}' is not supported."
        super().__init__(message)