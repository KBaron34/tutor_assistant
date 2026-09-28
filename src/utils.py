import re


def count_markers(text: str, markers: list[str]) -> int:
    """
    Считает, сколько маркеров из списка встретилось в тексте.

    :param text: текст
    :param markers: список маркеров

    :return: количество маркеров, которые встретились
    """
    text_lower = text.lower()
    return sum(1 for m in markers if m in text_lower)


def clean_llm_response(text: str) -> str:
    """
    Убирает markdown-обёртку из ответа LLM.

    :param text: текст

    :return: очищенный текст
    """
    content = re.sub(r"```(?:json)?", "", text)
    start = content.find("{")
    end = content.rfind("}")
    if start != -1 and end != -1:
        return content[start : end + 1]
    return content.strip()
