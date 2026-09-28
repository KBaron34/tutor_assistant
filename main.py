import argparse
import json
from pathlib import Path

from src.extract import extract
from src.classify import classify
from src.check_zone import check_zone

DATASET_PATH = Path(__file__).parent / "dataset.json"


def load_dataset() -> dict:
    """
    Загружает dataset.json.
    """
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def run_extract() -> None:
    """
    Прогоняет extract на всех записях.
    """
    data = load_dataset()
    for rec in data["records"]:
        print(f"{rec['id']}: {extract(rec['text'])}")


def run_classify() -> None:
    """
    Прогоняет classify на всех записях.
    """
    data = load_dataset()
    for rec in data["records"]:
        label, score = classify(rec["text"])
        print(f"{rec['id']}: {label} ({score})")


def run_check_zone() -> None:
    """
    Прогоняет check_zone на 15 наблюдениях.
    """
    data = load_dataset()
    for i, obs in enumerate(data["observations"], 1):
        result = check_zone(obs)
        print(f"{i}. {result}")


def run_all() -> None:
    """
    Прогоняет весь пайплайн.
    """
    print("=== Часть 1: extract ===")
    run_extract()
    print("\n=== Часть 2: classify ===")
    run_classify()
    print("\n=== Часть 3: check_zone ===")
    run_check_zone()


def main() -> None:
    parser = argparse.ArgumentParser(description="Пайплайн обработки записей о детях.")
    parser.add_argument(
        "command",
        choices=["extract", "classify", "check-zone", "run-all"],
        help="Что запустить",
    )
    args = parser.parse_args()

    commands = {
        "extract": run_extract,
        "classify": run_classify,
        "check-zone": run_check_zone,
        "run-all": run_all,
    }
    commands[args.command]()


if __name__ == "__main__":
    main()
