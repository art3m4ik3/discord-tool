from typing import List, Iterator, Dict, Any
from dataclasses import dataclass, field
from __future__ import annotations
from itertools import cycle
from modules import visual
import json
import os


@dataclass
class Config:
    """Configuration data structure."""

    tokens: List[str] = field(default_factory=list)
    proxies: Iterator[str] = field(default_factory=lambda: cycle([]))
    thread_count: int = 10
    proxy_type: str = "http"
    use_proxy: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for saving."""
        return {
            "use_proxy": self.use_proxy,
            "proxy_type": self.proxy_type,
            "thread_count": self.thread_count,
        }


class ConfigManager:
    """Manages configuration loading, saving and updates."""

    CONFIG_PATH = "data/config.json"

    def __init__(self) -> None:
        self.config: Config = Config()

    def configure(self) -> None:
        """Interactive configuration menu."""
        visual.Visual.clear()
        visual.Visual.logo()

        config_choices = [
            "Использовать прокси",
            "Изменить тип прокси",
            "Изменить количество потоков",
            "Завершить настройку",
        ]

        for num, choice in enumerate(config_choices, start=1):
            visual.Visual.info(f"[{num}] {choice}")

        choice = visual.Visual.choice("Выберите действие")

        if choice == "1":
            proxy_choice = visual.Visual.choice("Использовать прокси? (y/n)")
            self.config.use_proxy = proxy_choice.lower() == "y"
            self.save()
        elif choice == "2":
            proxy_types = ["http", "https", "socks4", "socks5"]
            visual.Visual.info("Доступные типы прокси:")
            for num, ptype in enumerate(proxy_types, start=1):
                visual.Visual.info(f"[{num}] {ptype}")
            type_choice = visual.Visual.choice("Выберите тип прокси")
            try:
                self.config.proxy_type = proxy_types[int(type_choice) - 1]
                self.save()
            except (ValueError, IndexError):
                visual.Visual.error("Неверный выбор")
        elif choice == "3":
            thread_count = visual.Visual.choice("Количество потоков")
            self.config.thread_count = int(thread_count)
            self.save()
        elif choice == "4":
            self.save()
            return

        self.configure()

    def load(self) -> None:
        """Load configuration from file."""
        try:
            with open(self.CONFIG_PATH, "r", encoding="utf-8") as f:
                config_data = json.load(f)
                self.config = Config(**config_data)
        except FileNotFoundError:
            self.config = Config()
            self.save()

    def save(self) -> None:
        """Save current configuration to file."""
        os.makedirs(os.path.dirname(self.CONFIG_PATH), exist_ok=True)
        with open(self.CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(self.config.to_dict(), f, indent=4)
