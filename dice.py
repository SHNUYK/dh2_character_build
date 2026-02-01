import secrets


def roll_plus():
    rolls = [secrets.randbelow(10) + 1 for _ in range(3)]
    rolls.sort(reverse=True)
    return 20 + rolls[0] + rolls[1]


def roll_minus():
    rolls = [secrets.randbelow(10) + 1 for _ in range(3)]
    rolls.sort()
    return 20 + rolls[0] + rolls[1]


def roll_normal():
    return 20 + (secrets.randbelow(10) + 1) + (secrets.randbelow(10) + 1)
