import re

import dateparser

# Паттерны поиска
DATE_PATTERN = re.compile(
    r"(\d{1,2}[./]\d{1,2}[./]\d{2,4}|\d{1,2}\s+[а-яА-Я]+\s+\d{4}(?:\s*г\.|года)?)"
)
CHILD_ID_PATTERN = re.compile(r"\bCH-\d+\b", re.IGNORECASE)
AUTHOR_PATTERN = re.compile(
    r"\b(?:[А-ЯЁ][а-яё]+\s+[А-ЯЁ]\.\s*[А-ЯЁ]\.|[А-ЯЁ]\.\s*[А-ЯЁ]\.\s+[А-ЯЁ][а-яё]+)"
)
SLEEP_HM_PATTERN = re.compile(
    r"(\d+)\s*ч(?:ас(?:а|ов)?)?\s*(\d+)?\s*мин", re.IGNORECASE
)
SLEEP_COLON_PATTERN = re.compile(r"(\d{1,2}):(\d{2})\s*(?:сна|спал|сон)", re.IGNORECASE)
SLEEP_HOURS_DECIMAL_PATTERN = re.compile(r"(\d+[,.]\d+)\s*час", re.IGNORECASE)
SLEEP_MINUTES_PATTERN = re.compile(r"(\d+)\s*минут", re.IGNORECASE)
ZONE_PATTERN = re.compile(r"\bзона\s*[:\-]\s*(\w+)\b", re.IGNORECASE)

MINUTES_PER_HOUR = 60


def parse_date(text: str) -> str | None:
    """
    Возвращает дату в формате ISO строки.

    :param text: строка текста

    :return: дата в формате ISO строки
    """
    lst_date = re.findall(DATE_PATTERN, text)

    if lst_date:
        dt = dateparser.parse(lst_date[0], settings={"DATE_ORDER": "DMY"})
        date = dt.date().isoformat()
    else:
        date = None

    return date


def parse_child_id(text: str) -> str | None:
    """
    Возвращает child_id.

    :param text: строка текста

    :return: child_id
    """
    lst_child_id = re.findall(CHILD_ID_PATTERN, text)

    if lst_child_id:
        child_id = lst_child_id[0].upper()
    else:
        child_id = None

    return child_id


def parse_author(text: str) -> str | None:
    """
    Возвращает автора записи.

    :param text: строка текста

    :return: автор записи
    """
    lst_author = re.findall(AUTHOR_PATTERN, text)

    if lst_author:
        author = lst_author[0]
        author = " ".join(author.split())
    else:
        author = None

    return author


def parse_sleep_hours(text: str) -> float | None:
    """
    Возвращает число часов сна.

    :param text: строка текста

    :return: число часов сна
    """
    # X ч. Y мин.
    m = SLEEP_HM_PATTERN.search(text)
    if m:
        hours = int(m.group(1))
        minutes = int(m.group(2)) if m.group(2) else 0
        return round(hours + minutes / MINUTES_PER_HOUR, 2)

    # X:YY сна/спал/сон
    m = SLEEP_COLON_PATTERN.search(text)
    if m:
        hours = int(m.group(1))
        minutes = int(m.group(2))
        return round(hours + minutes / MINUTES_PER_HOUR, 2)

    # X,Y часов
    m = SLEEP_HOURS_DECIMAL_PATTERN.search(text)
    if m:
        return round(float(m.group(1).replace(",", ".")), 2)

    # X минут
    m = SLEEP_MINUTES_PATTERN.search(text)
    if m:
        return round(int(m.group(1)) / MINUTES_PER_HOUR, 2)

    return None


def parse_zone(text: str) -> str | None:
    """
    Возвращает зону.

    :param text: строка текста

    :return: зона
    """
    lst_zone = re.findall(ZONE_PATTERN, text)

    if lst_zone:
        zone = lst_zone[0]
        zone = zone.strip().capitalize()
    else:
        zone = None

    return zone


def extract(text: str) -> dict:
    """
    Извлекает из строки и записывает в словарь дату в формате ISO строки,
    child_id, автора записи, число часов сна, зону.

    :param text: строка текста

    :return: словарь с данными
    """
    data_dict = {}

    data_dict["date"] = parse_date(text)
    data_dict["child_id"] = parse_child_id(text)
    data_dict["author"] = parse_author(text)
    data_dict["sleep_hours"] = parse_sleep_hours(text)
    data_dict["zone"] = parse_zone(text)

    return data_dict
