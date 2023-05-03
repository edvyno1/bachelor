import random

LOWER_CODE_BOUND = 10001000
UPPER_CODE_BOUND = 99998999

def generate_code() -> str:
    return str(random.randint(LOWER_CODE_BOUND, UPPER_CODE_BOUND))
