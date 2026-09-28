import pytest

from src.check_zone import (
    ZONES,
    check_zone,
    check_zone_keywords,
    check_zone_llm,
)

OBSERVATIONS = [
    ("отказ от еды третий день подряд", "питание", True),
    ("ударил себя по голове при смене маршрута", "поведение", True),
    ("не отвечал на обращённую речь весь день", "коммуникация", True),
    ("закрывал уши в столовой из-за шума", "сенсорика", True),
    ("заснул только к полуночи, спал 5 часов", "сон", True),
    ("впервые сам застегнул куртку", "самообслуживание", True),
    ("не удерживает карандаш, роняет мелкие предметы", "моторика", True),
    ("плакал 20 минут без видимой причины", "эмоции", True),
    ("поездка в центр на автобусе заняла 40 минут", None, False),
    ("родители перенесли занятие на четверг", None, False),
    ("в кабинете меняли лампы, занятие прошло в другой комнате", None, False),
    ("оформлена справка для поликлиники", None, False),
    ("ел только жёлтую еду, остальное отодвигал", "питание", True),
    ("отказался идти на занятие, потому что шёл дождь", None, False),
    ("был весёлым на празднике, много бегал и шумел", "эмоции", True),
]


class TestZones:
    """
    Проверка списка зон.
    """

    def test_zones_count(self) -> None:
        assert len(ZONES) == 8

    def test_zones_content(self) -> None:
        expected = {
            "эмоции",
            "коммуникация",
            "поведение",
            "питание",
            "сенсорика",
            "сон",
            "моторика",
            "самообслуживание",
        }
        assert set(ZONES) == expected


class TestKeywords:
    """
    Тесты поиска зон по ключевым словам.
    """

    def test_observation_detected(self) -> None:
        in_zone, confidence, explanation = check_zone_keywords(
            "отказ от еды третий день подряд"
        )
        assert in_zone is True
        assert confidence > 0
        assert "питание" in explanation

    def test_no_zone(self) -> None:
        in_zone, confidence, explanation = check_zone_keywords(
            "поездка в центр на автобусе заняла 40 минут"
        )
        assert in_zone is False
        assert confidence == 0.0

    def test_confidence_range(self) -> None:
        """
        Confidence всегда [0, 1].
        """
        for text, _, _ in OBSERVATIONS:
            _, confidence, _ = check_zone_keywords(text)
            assert 0.0 <= confidence <= 1.0


class TestLLM:
    """
    Тесты определения зон с помощью LLM.
    """

    def test_llm_returns_tuple_or_none(self) -> None:
        """
        LLM либо возвращает кортеж, либо None (если ключа нет).
        """
        result = check_zone_llm("отказ от еды третий день подряд")
        assert result is None or (
            isinstance(result, tuple)
            and len(result) == 3
            and isinstance(result[0], bool)
            and isinstance(result[1], float)
            and isinstance(result[2], str)
        )


class TestCheckZone:
    """
    Общие тесты check_zone().
    """

    @pytest.mark.parametrize("text,expected_zone,expected_in_zone", OBSERVATIONS)
    def test_observation(
        self, text: str, expected_zone: str | None, expected_in_zone: bool
    ) -> None:
        in_zone, confidence, explanation = check_zone(text)

        assert in_zone is expected_in_zone
        assert 0.0 <= confidence <= 1.0
        assert isinstance(explanation, str)
        assert len(explanation) > 0

        if expected_zone is not None:
            assert expected_zone in explanation

    def test_empty_text(self) -> None:
        in_zone, confidence, explanation = check_zone("")
        assert in_zone is False
        assert confidence == 0.0
        assert isinstance(explanation, str)
