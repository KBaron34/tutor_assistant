import json
from pathlib import Path

import pytest

from src.classify import (
    MARKERS,
    PRIORITY_MARKERS,
    UNKNOWN,
    classify,
    count_markers,
)


@pytest.fixture(scope="module")
def records() -> dict[str, str]:
    """
    Загружает тексты записей из dataset.json.
    """
    dataset_path = Path(__file__).parent.parent / "dataset.json"
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {rec["id"]: rec["text"] for rec in data["records"]}


class TestCountMarkers:
    """
    Тесты вспомогательной функции count_markers.
    """

    def test_single_match(self) -> None:
        assert count_markers("У него был сон", ["сон"]) == 1

    def test_multiple_matches(self) -> None:
        assert count_markers("Сон и спал", ["сон", "спал"]) == 2

    def test_no_match(self) -> None:
        assert count_markers("Просто текст", ["сон", "спал"]) == 0

    def test_case_insensitive(self) -> None:
        assert count_markers("СОН", ["сон"]) == 1


class TestPriorityMarkers:
    """
    Приоритетные маркеры дают confidence 1.0.
    """

    def test_parent_note_mama(self) -> None:
        label, score = classify("Мама ребёнка CH-0342: ночью просыпался")
        assert label == "parent_note"
        assert score == 1.0

    def test_parent_note_papa(self) -> None:
        label, score = classify("Папа сообщил, что ребёнок спал плохо")
        assert label == "parent_note"
        assert score == 1.0

    def test_recommendation(self) -> None:
        label, score = classify("Рекомендация: ввести сенсорную паузу")
        assert label == "recommendation"
        assert score == 1.0

    def test_recommendation_over_lesson_report(self) -> None:
        """
        Приоритет recommendation побеждает lesson_report-маркеры.
        """
        text = "Рекомендация по ребёнку CH-0107. Специалист Петров И. И."
        label, score = classify(text)
        assert label == "recommendation"
        assert score == 1.0


class TestScoring:
    """
    Классификация без приоритетных маркеров — через скоры.
    """

    def test_observation(self) -> None:
        label, score = classify("Ребёнок был вялый, играл, отказался от еды")
        assert label == "observation"
        assert score > 0.5

    def test_lesson_report(self) -> None:
        label, score = classify("Отчёт о занятии №5, ребёнок спал плохо")
        assert label == "lesson_report"
        assert score > 0.5


class TestUnknown:
    """
    Граничные случаи — unknown.
    """

    def test_empty_text(self) -> None:
        label, score = classify("")
        assert label == UNKNOWN
        assert score == 0.0

    def test_no_markers(self) -> None:
        label, score = classify("Просто текст")
        assert label == UNKNOWN
        assert score == 0.0

    def test_ambiguous_equal_scores(self) -> None:
        """
        Margin = 0 < порога -> unknown.
        """
        label, _ = classify("Сон и отчёт")
        assert label == UNKNOWN


class TestDataset:
    """
    Тесты на реальных записях R1–R6.
    """

    def test_r1_observation(self, records: dict[str, str]) -> None:
        label, _ = classify(records["R1"])
        assert label == "observation"

    def test_r2_lesson_report(self, records: dict[str, str]) -> None:
        label, _ = classify(records["R2"])
        assert label == "lesson_report"

    def test_r3_parent_note(self, records: dict[str, str]) -> None:
        label, score = classify(records["R3"])
        assert label == "parent_note"
        assert score == 1.0

    def test_r4_observation(self, records: dict[str, str]) -> None:
        label, _ = classify(records["R4"])
        assert label == "observation"

    def test_r5_recommendation(self, records: dict[str, str]) -> None:
        label, score = classify(records["R5"])
        assert label == "recommendation"
        assert score == 1.0

    def test_r6_observation(self, records: dict[str, str]) -> None:
        label, _ = classify(records["R6"])
        assert label == "observation"
