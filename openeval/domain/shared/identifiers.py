from uuid import uuid4


def generate_id() -> str:
    """
    Generate a globally unique identifier.

    UUID4 is sufficient for OpenEval v1.
    """

    return str(uuid4())
