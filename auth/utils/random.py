import random
import string


def get_random_string(length: int = 20, allowed_characters: str | None = None):
    allowed_characters = allowed_characters or string.ascii_letters
    return "".join(random.choice(allowed_characters) for _ in range(length))
