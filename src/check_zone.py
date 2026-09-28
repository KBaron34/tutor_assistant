import json
import os

from dotenv import load_dotenv

from gigachat import GigaChat

try:
    from .utils import count_markers, clean_llm_response
except ImportError:
    from utils import count_markers, clean_llm_response

load_dotenv()


ZONES = [
    "эмоции",
    "коммуникация",
    "поведение",
    "питание",
    "сенсорика",
    "сон",
    "моторика",
    "самообслуживание",
]

KEYWORD_MARKERS = {
    "эмоции": [
        "плакал",
        "слёз",
        "расстро",
        "весёл",
        "радост",
        "злил",
        "испуг",
        "тревог",
    ],
    "коммуникация": ["отвечал", "речь", "обращён", "говорил", "молчал", "общени"],
    "поведение": ["ударил", "агресс", "кричал", "бросил", "истерик"],
    "питание": [
        "поел",
        "съел",
        "еда",
        "еду",
        "завтрак",
        "обед",
        "ужин",
        "аппетит",
        "отказ от еды",
    ],
    "сенсорика": ["уши", "шум", "свет", "тактиль", "запах", "сенсор", "перегруз"],
    "сон": ["сон", "спал", "заснул", "проснулся", "полуноч", "ночь"],
    "моторика": [
        "удержива",
        "карандаш",
        "роняет",
        "мелк",
        "движени",
        "координаци",
        "моторик",
    ],
    "самообслуживание": [
        "сам",
        "застегнул",
        "оделся",
        "умылся",
        "куртк",
        "обувь",
        "одежд",
    ],
}


NO_ZONE_MESSAGE = "не относится к отслеживаемым зонам"

PROMPT = """Ты классифицируешь наблюдения за детьми по 8 зонам развития.

Зоны:
- эмоции: плач, радость, злость, страх, тревога
- коммуникация: речь, ответы, обращённая речь, общение
- поведение: агрессия, удары, крик, отказ, истерика
- питание: еда, аппетит, отказ от еды, избирательность в еде
- сенсорика: реакция на шум, свет, запахи, тактильные ощущения
- сон: засыпание, длительность сна, качество сна
- моторика: мелкая и крупная моторика, координация, движение
- самообслуживание: одевание, гигиена, самостоятельность

Правила:
- Не придумывай связи, которых нет в тексте.
- Если текст не относится ни к одной зоне — in_zone: false.
- Наблюдение о ребёнке, НЕ о среде. "Меняли лампы", "перенесли занятие", "дождь" — False.
- explanation СТРОГО по шаблону:
  - если in_zone: true -> "<текст> относится к зоне '<зона>'"
  - если in_zone: false -> "<текст> не относится к отслеживаемым зонам"
- Никаких "так как", "поскольку", "однако", дополнительных предложений.
- Ответ — только JSON. Без markdown. Без пояснений.

Текст наблюдения: "{text}"


Примеры ответа:
{{"in_zone": true, "confidence": 0.95, "zone": "сенсорика", "explanation": "Закрывал уши в столовой из-за шума относится к зоне 'сенсорика'"}}

Если не относится:
{{"in_zone": false, "confidence": 0.0, "zone": null, "explanation": "Поездка в центр на автобусе заняла 40 минут не относится к отслеживаемым зонам"}}
"""


def check_zone_llm(text: str) -> tuple[bool, float, str] | None:
    """
    Определяет зону через GigaChat.

    :param text: текст

    :returns:
        (in_zone, confidence, explanation) или None, если LLM недоступна
        или вернула невалидный ответ.
    """
    credentials = os.getenv("GIGACHAT_CREDENTIALS")
    if not credentials:
        return None

    try:
        with GigaChat(credentials=credentials, verify_ssl_certs=False) as client:
            response = client.chat(PROMPT.format(text=text))
            content = response.choices[0].message.content
            content = clean_llm_response(content)
            data = json.loads(content)
            return (
                bool(data["in_zone"]),
                float(data["confidence"]),
                str(data["explanation"]),
            )
    except Exception:
        return None


def check_zone_keywords(text: str) -> tuple[bool, float, str]:
    """
    Определяет зону по ключевым словам.

    Считает совпавшие маркеры по каждой зоне. Выбирает зону
    с максимальным числом совпадений. Если ни один маркер
    не найден — возвращает False.

    :param text: текст

    :returns:
        (True, confidence, explanation) — если зона определена,
        (False, 0.0, explanation) — если не относится ни к одной.
    """
    scores = {
        zone: count_markers(text, markers) for zone, markers in KEYWORD_MARKERS.items()
    }
    total = sum(scores.values())

    if total == 0:
        return False, 0.0, f"{text} {NO_ZONE_MESSAGE}"

    top_zone, top_count = max(scores.items(), key=lambda x: x[1])
    confidence = round(top_count / total, 2)

    return True, confidence, f"{text} относится к зоне '{top_zone}'"


def check_zone(text: str) -> tuple[bool, float, str]:
    """
    Определяет, относится ли наблюдение к одной из отслеживаемых зон.

    Использует LLM (GigaChat). Если ключ не задан или LLM вернула ошибку —
    переключается на поиск по ключевым словам.

    :param text: текст

    :returns:
        (in_zone, confidence, explanation):
            - in_zone: True, если относится к зоне, иначе False;
            - confidence: уверенность 0.0–1.0;
            - explanation: текстовое объяснение.
    """
    result = check_zone_llm(text)
    if result:
        return result
    return check_zone_keywords(text)
