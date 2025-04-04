from time import time


def create_id() -> int:
    """
    Creates a unique identifier, which is a hash of the current time.

    Returns:
        int: A unique identifier.
    """
    return hash(time())
