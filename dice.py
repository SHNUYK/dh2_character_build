import secrets


def d10():
    return secrets.randbelow(10) + 1


def roll_plus():
    r = sorted([d10(), d10(), d10()], reverse=True)
    return 20 + r[0] + r[1]


def roll_minus():
    r = sorted([d10(), d10(), d10()])
    return 20 + r[0] + r[1]


def roll_normal():
    return 20 + d10() + d10()


def roll_wounds(base):
    return base + (secrets.randbelow(5) + 1)


def roll_blessing(base_fate, threshold):
    r = d10()
    bonus = 1 if r >= threshold else 0
    return base_fate + bonus, r
