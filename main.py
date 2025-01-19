from modules import config, visual, token_checker, server_joiner, token_cleaner
from itertools import cycle
import sys
import os

__VERSION__ = "1.0.0"


class DiscordTool:
    def __init__(self) -> None:
        self.config_manager = config.ConfigManager()

        # Create config if not exist
        if not os.path.exists("data/config.json"):
            visual.Visual.info("Файл конфигурации не найден, создание нового...")
            self.config_manager.configure()
        else:
            self.config_manager.load()

        visual.Visual.clear()
        visual.Visual.logo()
        visual.Visual.info("Инициализация...")

        folders = ["data", "output", "output/valid", "output/invalid"]

        # Create dirs if not exist
        for folder_num, folder in enumerate(folders, start=1):
            os.makedirs(folder, exist_ok=True)
            visual.Visual.debug(
                f"[{folder_num}/{len(folders)}] Папка {folder} создана."
            )

        # Load tokens
        self.load_tokens()

        # Load proxies if enabled
        if self.config_manager.config.use_proxy:  # Access config through the manager
            self.load_proxies()

        visual.Visual.clear()
        visual.Visual.logo()

        # Load menu
        self.main_menu()

    def load_tokens(self):
        try:
            visual.Visual.debug("Загрузка токенов")
            with open("data/tokens.txt", "r", encoding="U8") as f:
                config.Config.tokens = [
                    line.strip() for line in f if line.strip()
                ]  # remove empty lines

            if not config.Config.tokens:
                raise FileNotFoundError
        except FileNotFoundError:
            visual.Visual.error(
                "Для работы необходимо создать файл в data/tokens.txt и указать нужные токены."
            )
            with open("data/tokens.txt", "w", encoding="U8") as f:
                pass
            raise

    def load_proxies(self):
        try:
            visual.Visual.debug("Загрузка прокси")
            with open("data/proxies.txt", "r", encoding="U8") as f:
                proxies = [line.strip() for line in f if line.strip()]
                if proxies:  # Check if proxies list is not empty
                    config.Config.proxies = cycle(proxies)
                else:
                    visual.Visual.error(
                        "Файл proxies.txt пуст. Прокси не будут использоваться."
                    )
                    self.config_manager.config.use_proxy = False  # Disable proxy usage
                    self.config_manager.save()  # Save updated config

        except FileNotFoundError:
            visual.Visual.error(
                "Для работы с прокси необходимо создать файл в data/proxies.txt и указать нужные прокси."
            )
            with open("data/proxies.txt", "w", encoding="U8") as f:
                pass
            raise

    def main_menu(self) -> None:
        menu_choices = [
            ("Проверка токенов", token_checker.TokenChecker),
            ("Присоединиться к серверу", server_joiner.ServerJoiner),
            ("Очистить токены", token_cleaner.TokenCleaner),
            ("Настройки", self.config_manager.configure),
            ("Выход", sys.exit),
        ]

        for num, (choice, _) in enumerate(menu_choices, start=1):
            visual.Visual.info(f"[{num}] {choice}")

        menu_choice = visual.Visual.choice("Выберите действие")

        try:
            visual.Visual.clear()
            visual.Visual.logo()

            choice_index = int(menu_choice) - 1
            if 0 <= choice_index < len(menu_choices):
                menu_choices[choice_index][1]()
            else:
                visual.Visual.error("Неверный выбор")
        except ValueError:
            visual.Visual.error("Введите число")

        self.main_menu()


if __name__ == "__main__":
    try:
        DiscordTool()
    except KeyboardInterrupt:
        sys.exit()
    except:
        input("Enter чтобы выйти...")
