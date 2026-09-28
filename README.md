# Digital Tutor Assistant

Модуль интеллектуальной обработки записей о детях: извлечение структурированных полей, классификация типа записи, отнесение наблюдений к зонам развития.

## Содержание

- [Архитектура](#архитектура)
- [Установка](#установка)
- [Запуск](#запуск)
- [Тесты](#тесты)
- [Структура проекта](#структура-проекта)

## Архитектура

Проект состоит из трёх модулей и CLI.

### Часть 1. `src/extract.py` — извлечение полей из текста

Функция `extract(text: str) -> dict` извлекает пять полей:

| Поле | Формат | Пример |
|---|---|---|
| `date` | ISO-строка | `"2025-03-05"` |
| `child_id` | `CH-XXXX` | `"CH-0421"` |
| `author` | `Фамилия И. О.` | `"Иванова А. С."` |
| `sleep_hours` | float (часы) | `6.5` |
| `zone` | строка или None | `"Моторика"` |

Отсутствующие поля возвращаются как `None`.

**Подход:** регулярные выражения и `dateparser`. Даты — через `dateparser` с `DATE_ORDER: "DMY"`. Остальные поля — регулярные выражения.

### Часть 2. `src/classify.py` — классификация типа записи

Функция `classify(text: str) -> tuple[str, float]` возвращает тип и уверенность.

Возможные типы: `observation`, `lesson_report`, `parent_note`, `recommendation`, `unknown`.

**Подход:** приоритетные маркеры + скоринг.

- Приоритетные маркеры (`мама`, `рекоменд`) дают детерминированный ответ с confidence 1.0.
- Остальные случаи — скоринг по маркерам с порогом `unknown` = 0.15.

### Часть 3. `src/check_zone.py` — отнесение к зонам развития

Функция `check_zone(note: str) -> tuple[bool, float, str]` определяет, относится ли наблюдение к одной из 8 зон:

эмоции, коммуникация, поведение, питание, сенсорика, сон, моторика, самообслуживание.

**Подход:** LLM (GigaChat) + fallback на keyword matching.

- Основной механизм — GigaChat с промптом, возвращающим JSON.
- Fallback — keyword matching, работает без API-ключа.

## Установка

### Основные зависимости

```bash
pip install -r requirements.txt
```

### Для Jupyter-ноутбука (опционально)

```bash
pip install jupyter pandas matplotlib
```

### Настройка GigaChat

Создайте `.env` в корне проекта:

```
GIGACHAT_CREDENTIALS=ваш_base64_ключ
GIGACHAT_SCOPE=GIGACHAT_API_PERS
GIGACHAT_MODEL=GigaChat-2
GIGACHAT_VERIFY_SSL_CERTS=false
```

Пример в `.env.example`. 

Без `.env` модуль `check_zone` работает через fallback на keywords.

## Запуск

### Пайплайн целиком

```bash
python main.py run-all
```

### Отдельные части

```bash
python main.py extract      # Часть 1: извлечение полей
python main.py classify     # Часть 2: классификация
python main.py check-zone   # Часть 3: проверка наблюдений
```

## Тесты

```bash
python -m pytest tests/ -v
```

Тесты для Части 3 используют GigaChat, если ключ задан в `.env`. Без ключа — работают через fallback на keywords.

## Структура проекта

```
tutor_assistant/
├── main.py                       # CLI
├── dataset.json                  # Тестовые данные
├── requirements.txt
├── .env.example                  # Шаблон для ключей
├── README.md
├── RESULTS.md                    # Результаты и обоснования
├── src/
│   ├── __init__.py
│   ├── extract.py                # Часть 1
│   ├── classify.py               # Часть 2
│   ├── check_zone.py             # Часть 3
│   └── utils.py                  # Общие функции
├── tests/
│   ├── __init__.py
│   ├── test_extract.py
│   ├── test_classify.py
│   └── test_check_zone.py
└── notebooks/
    └── threshold_analysis.ipynb  # Анализ порога для classify
```