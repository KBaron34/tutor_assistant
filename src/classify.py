PRIORITY_MARKERS = {
    "parent_note": ["мама", "папа", "родит"],
    "recommendation": ["рекоменд", "ввести"],
}

MARKERS = {
    "lesson_report": ["отчёт", "отчет", "№"],
    "observation": [
        "сон",
        "спал",
        "настроен",
        "вялый",
        "играл",
        "отказал",
        "перегруз",
        "просып",
        "ел",
    ],
}

UNKNOWN = "unknown"
THRESHOLD = 0.15


def count_markers(text: str, markers: list[str]) -> int:
    """
    Считает, сколько маркеров из списка встретилось в тексте.

    :param text: текст
    :param markers: список маркеров

    :return: количество маркеров, которые встретились
    """
    text_lower = text.lower()
    return sum(1 for m in markers if m in text_lower)


def classify(text: str) -> tuple[str, float]:
    """
    Классифицирует тип записи:
        1. Если найден приоритетный маркер (parent_note, recommendation) -
           возвращаем тип с confidence 1.0.
        2. Иначе считаем скоры по остальным типам, нормируем.
        3. Если разрыв между топ-1 и топ-2 меньше порога — unknown.
        4. Иначе — топ-1.

    :param text: текст

    :return: кортеж (тип, уверенность):
                — тип из списка;
                - уверенность в диапазоне 0.0 – 1.0.
    """
    # Приоритетные маркеры
    for label, markers in PRIORITY_MARKERS.items():
        if count_markers(text, markers) > 0:
            return label, 1.0

    # Рассчет скоров
    scores = {label: count_markers(text, markers) for label, markers in MARKERS.items()}
    total = sum(scores.values())

    if total == 0:
        return UNKNOWN, 0.0

    # Нормировка
    norm_scores = {label: s / total for label, s in scores.items()}
    sorted_scores = sorted(norm_scores.items(), key=lambda x: x[1], reverse=True)

    top1_label, top1_score = sorted_scores[0]
    top2_score = sorted_scores[1][1] if len(sorted_scores) > 1 else 0.0

    # Порог
    if top1_score - top2_score < THRESHOLD:
        return UNKNOWN, top1_score

    return top1_label, top1_score
