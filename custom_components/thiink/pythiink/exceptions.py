class ThiinkError(Exception):
    """Base exception for pythiink."""


class ThiinkConnectionError(ThiinkError):
    """Raised when the device cannot be reached."""
