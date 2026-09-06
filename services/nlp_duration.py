import re

UNITS = {
    "second": "секунда",
    "minute": "минута",
    "hour": "час",
    "day": "день",
    "week": "неделя",
    "month": "месяц",
    "year": "год",
}

FORMS = {
    "час": ("час", "часа", "часов"),
    "день": ("день", "дня", "дней"),
    "месяц": ("месяц", "месяца", "месяцев"),
    "год": ("год", "года", "лет"),
    "секунда": ("секунда", "секунды", "секунд"),
    "минута": ("минута", "минуты", "минут"),
    "неделя": ("неделя", "недели", "недель"),
}

WEEK_MONTHS = {
    "week": ("неделю", "недели", "недель"),
    "month": ("месяц", "месяца", "месяцев"),
}


def _pluralize(number: int, forms: tuple[str, str, str]) -> str:
    if abs(number) % 10 == 1 and abs(number) % 100 != 11:
        return forms[0]
    if abs(number) % 10 in (2, 3, 4) and abs(number) % 100 not in (12, 13, 14):
        return forms[1]
    return forms[2]


def en_to_ru(duration: str) -> str:
    parts = duration.lower().replace(",", "").replace(" and ", " ").split()

    tokens = []
    i = 0
    while i < len(parts):
        word = parts[i]
        if re.fullmatch(r"-?\d+", word):
            number = int(word)
            unit = parts[i + 1].rstrip("s") if i + 1 < len(parts) else None
            if unit in UNITS:
                noun = UNITS[unit]
                form = WEEK_MONTHS[unit] if unit in WEEK_MONTHS else FORMS[noun]
                tokens.append(f"{number} {_pluralize(number, form)}")
                i += 2
                continue
        tokens.append(word)
        i += 1

    return ", ".join(tokens)
