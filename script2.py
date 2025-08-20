import argparse
import json
import logging
import urllib.parse
import webbrowser
from typing import List
import os
import sys


class Point:
    def __init__(self, point_id: int, latitude: float, longitude: float, title: str | None = None):
        """Инициализация точки."""
        self.id = point_id
        self.latitude = latitude
        self.longitude = longitude
        self.title = title


class YandexMapGenerator:
    def __init__(self, zoom: int = 5, lang: str = "ru_RU"):
        """Инициализация генератора карты."""
        self._zoom = zoom
        self._lang = lang
        self._points: List[Point] = []
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    def _parse_points(self, data: list) -> None:
        """Общая логика парсинга списка точек из JSON."""
        if not isinstance(data, list):
            raise ValueError("JSON должен быть списком точек")
        self._points = []
        for point in data:
            if not all(key in point for key in ["id", "latitude", "longitude"]):
                raise ValueError("Точка должна содержать id, latitude, longitude")
            self._points.append(Point(
                int(point["id"]),
                float(point["latitude"]),
                float(point["longitude"]),
                point.get("title")
            ))
        logging.info(f"Загружено {len(self._points)} точек")

    def load_points(self, json_input: str) -> None:
        """Загрузка точек из JSON (строки или файла)."""
        try:
            if os.path.isfile(json_input):
                logging.info(f"Определено: {json_input} — это файл")
                with open(json_input, "r", encoding="utf-8") as file:
                    data = json.load(file)
            else:
                logging.info("Определено: входные данные — это JSON-строка")
                data = json.loads(json_input)

            self._parse_points(data)

        except (json.JSONDecodeError, ValueError) as error:
            logging.error(f"Ошибка парсинга JSON: {error}")
            raise

    def generate_map_url(self) -> str:
        """Генерация URL для карты."""
        if not self._points:
            raise ValueError("Нет точек")
        points_str = [f"{p.longitude},{p.latitude},pmwtm{p.id}" for p in self._points]
        center = f"{self._points[0].longitude},{self._points[0].latitude}"
        params = {
            "ll": center,
            "z": self._zoom,
            "lang": self._lang,
            "pt": "~".join(points_str)
        }
        base_url = "https://maps.yandex.ru/"
        url = f"{base_url}?{urllib.parse.urlencode(params)}"
        logging.info(f"URL: {url}")
        return url

    def display_map(self) -> None:
        """Открытие карты в браузере."""
        url = self.generate_map_url()
        webbrowser.open(url)
        logging.info("Карта открыта.")


def main():
    parser = argparse.ArgumentParser(description="Метки на Яндекс.Картах")
    parser.add_argument("json_input", nargs="?", help="JSON-строка или путь к JSON-файлу")
    parser.add_argument("--stdin", action="store_true", help="Читать JSON из stdin")

    args = parser.parse_args()
    map_generator = YandexMapGenerator()

    if args.stdin:
        json_data = sys.stdin.read()
        map_generator.load_points(json_data)
    elif args.json_input:
        map_generator.load_points(args.json_input)
    else:
        parser.error("Укажите JSON-строку, путь к JSON-файлу или используйте --stdin")

    map_generator.display_map()


if __name__ == "__main__":
    main()
