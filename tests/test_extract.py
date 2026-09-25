import pytest

from src.extract import (
    extract,
    parse_author,
    parse_child_id,
    parse_date,
    parse_sleep_hours,
    parse_zone,
)


class TestParseDate:
    """
    Тесты извлечения даты.
    """

    def test_dotted_date(self) -> None:
        """
        Формат DD.MM.YYYY.
        """
        assert parse_date("05.03.2025 ...") == "2025-03-05"

    def test_dotted_short_year(self) -> None:
        """
        Формат DD.MM.YY.
        """
        assert parse_date("07.03.25 ...") == "2025-03-07"

    def test_russian_month(self) -> None:
        """
        Формат D месяца YYYY г.
        """
        assert parse_date("от 1 марта 2025 г. ...") == "2025-03-01"

    def test_slash_dmy(self) -> None:
        """
        Формат DD/MM/YY — трактуем как DMY.
        """
        assert parse_date("03/01/25 ...") == "2025-01-03"

    def test_no_date(self) -> None:
        """
        Нет даты -> None.
        """
        assert parse_date("Просто текст") is None


class TestParseChildId:
    """
    Тесты извлечения child_id.
    """

    def test_upper(self) -> None:
        assert parse_child_id("Ребёнок CH-0421, ...") == "CH-0421"

    def test_lower_normalized(self) -> None:
        """
        Нижний регистр в тексте -> верхний на выходе.
        """
        assert parse_child_id("ch-0421 ...") == "CH-0421"

    def test_no_id(self) -> None:
        assert parse_child_id("Нет идентификатора") is None


class TestParseAuthor:
    """
    Тесты извлечения автора.
    """

    def test_surname_first(self) -> None:
        """
        Формат Фамилия И. О.
        """
        assert parse_author("тьютор Иванова А. С.") == "Иванова А. С."

    def test_specialist(self) -> None:
        assert parse_author("Специалист Петров И. И.") == "Петров И. И."

    def test_no_author(self) -> None:
        """
        Роли без ФИО не считаются автором.
        """
        assert parse_author("Мама ребёнка CH-0342") is None


class TestParseSleepHours:
    """
    Тесты извлечения длительности сна.
    """

    def test_hours_minutes(self) -> None:
        """
        6 ч 30 мин -> 6.5.
        """
        assert parse_sleep_hours("Сон 6 ч 30 мин") == 6.5

    def test_decimal_hours(self) -> None:
        """
        6,5 часов -> 6.5.
        """
        assert parse_sleep_hours("Спал 6,5 часов") == 6.5

    def test_colon_with_marker(self) -> None:
        """
        5:45 сна -> 5.75 (5 часов 45 минут).
        """
        assert parse_sleep_hours("Итого 5:45 сна") == 5.75

    def test_minutes(self) -> None:
        """
        390 минут -> 6.5.
        """
        assert parse_sleep_hours("Сон ~390 минут") == 6.5

    def test_colon_without_marker_ignored(self) -> None:
        """
        6:30 без слова про сон -> None.
        """
        assert parse_sleep_hours("Встреча в 6:30") is None

    def test_no_sleep(self) -> None:
        assert parse_sleep_hours("Просто текст") is None


class TestParseZone:
    """
    Тесты извлечения зоны.
    """

    def test_explicit_zone(self) -> None:
        assert parse_zone("Зона: моторика") == "Моторика"

    def test_zone_dash(self) -> None:
        assert parse_zone("Зона - сенсорика") == "Сенсорика"

    def test_zone_only_explicit(self) -> None:
        """Не явная зона -> None."""
        assert parse_zone("Сенсорика") is None


class TestExtract:
    """
    Общие тесты extract().
    """

    def test_r1_full(self) -> None:
        text = (
            "05.03.2025. Ребёнок CH-0421, тьютор Иванова А. С. "
            "Сон 6 ч 30 мин, утром вялый."
        )
        assert extract(text) == {
            "date": "2025-03-05",
            "child_id": "CH-0421",
            "author": "Иванова А. С.",
            "sleep_hours": 6.5,
            "zone": None,
        }

    def test_r2_full(self) -> None:
        text = (
            "Отчёт о занятии №12 от 1 марта 2025 г. "
            "Специалист Петров И. И. Ребёнок CH-0107, зона: моторика. "
            "Накануне спал 6,5 часов."
        )
        assert extract(text) == {
            "date": "2025-03-01",
            "child_id": "CH-0107",
            "author": "Петров И. И.",
            "sleep_hours": 6.5,
            "zone": "Моторика",
        }

    def test_r6_empty(self) -> None:
        """
        Запись без необходимых полей полей -> все None.
        """
        text = "Ребёнок был в хорошем настроении, играл с конструктором."
        assert extract(text) == {
            "date": None,
            "child_id": None,
            "author": None,
            "sleep_hours": None,
            "zone": None,
        }
