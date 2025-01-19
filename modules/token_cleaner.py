from modules import config, visual, utils
from datetime import datetime
from typing import List
import threading
import json
import os


class TokenCleaner:
    def __init__(self) -> None:
        print(
            f"Loading tokens from: {os.path.abspath('data/tokens.txt')}"
        )  # Debug print
        self.tokens = self.split_tokens()
        self.cleaned_tokens = []
        self.failed_tokens = []
        self.valid_tokens_file = "output/valid/tokens.json"
        self.invalid_tokens_file = "output/invalid/tokens.json"
        self.lock = threading.Lock()

        self.clean_tokens()

    def split_tokens(self) -> list:
        visual.Visual.info(
            f"Разделение {len(config.Config.tokens)} токенов на {config.Config.thread_count} потоков"
        )
        avg_len = len(config.Config.tokens) // config.Config.thread_count
        remainder = len(config.Config.tokens) % config.Config.thread_count
        result = []
        start = 0

        for i in range(config.Config.thread_count):
            end = start + avg_len + (1 if i < remainder else 0)
            part = config.Config.tokens[start:end]
            if part and part[0]:
                result.append(part)
            start = end
        return result

    def save_results(self) -> None:
        with open(self.valid_tokens_file, "w") as f:
            json.dump(self.cleaned_tokens, f, indent=4)
        with open(self.invalid_tokens_file, "w") as f:
            json.dump(self.failed_tokens, f, indent=4)

    def log_success(self, message: str) -> None:
        with self.lock:  # Protect shared resources
            visual.Visual.success(message)

    def log_error(self, message: str) -> None:
        with self.lock:
            visual.Visual.error(message)

    def log_info(self, message: str) -> None:
        with self.lock:
            visual.Visual.info(message)

    def clean_token_thread(self, tokens: List[str]) -> None:
        session = utils.Utils.get_session()

        for token in tokens:
            visual.Visual.info(f"Очистка токена: {token[:10]}...")
            headers = utils.Utils.get_default_headers(token)
            try:
                # 1. Leave servers
                guilds_response = session.get(
                    "https://discord.com/api/v9/users/@me/guilds", headers=headers
                )
                if guilds_response.status_code != 200:
                    self.log_error(
                        f"Ошибка получения списка серверов: {guilds_response.status_code} {guilds_response.text}"
                    )
                    raise Exception(
                        "Failed to fetch guilds"
                    )  # Stop processing this token
                guilds = guilds_response.json()

                for guild in guilds:
                    if guild.get("owner"):
                        self.log_info(f"Пропуск сервера {guild['name']} (владелец)")
                        continue  # Don't leave owned servers

                    resp = session.delete(
                        f"https://discord.com/api/v9/users/@me/guilds/{guild['id']}",
                        headers=headers,
                    )
                    if resp.status_code == 204:
                        self.log_success(
                            f"Выход из сервера: {guild.get('name', guild['id'])}"
                        )
                    else:
                        self.log_error(
                            f"Ошибка выхода из сервера {guild.get('name', guild['id'])}: {resp.status_code} {resp.text}"
                        )

                # 2. Remove friends
                friends = session.get(
                    "https://discord.com/api/v9/users/@me/relationships",
                    headers=headers,
                ).json()
                for friend in friends:
                    resp = session.delete(
                        f"https://discord.com/api/v9/users/@me/relationships/{friend['id']}",
                        headers=headers,
                    )
                    if resp.status_code != 204:
                        visual.Visual.error(
                            f"Ошибка удаления друга: {resp.status_code}"
                        )

                # 3. Close DMs
                dms = session.get(
                    "https://discord.com/api/v9/users/@me/channels", headers=headers
                ).json()
                for dm in dms:
                    resp = session.delete(
                        f"https://discord.com/api/v9/channels/{dm['id']}",
                        headers=headers,
                    )
                    if (
                        resp.status_code != 200
                    ):  # 200 for DM close, 204 for leaving guilds/friends
                        visual.Visual.error(f"Ошибка закрытия ЛС: {resp.status_code}")

                self.cleaned_tokens.append(
                    {"token": token, "timestamp": datetime.now().isoformat()}
                )
                with self.lock:
                    self.cleaned_tokens.append(
                        {"token": token, "timestamp": datetime.now().isoformat()}
                    )
                self.log_success(f"Токен {token[:10]}... очищен.")

            except Exception as e:
                self.log_error(f"Ошибка при очистке токена {token[:10]}...: {e}")
                with self.lock:
                    self.failed_tokens.append(
                        {
                            "token": token,
                            "reason": str(e),
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

    def clean_tokens(self) -> None:
        self.log_info("Начало процесса очистки токенов")

        threads = []
        for i, token in enumerate(self.tokens):
            thread = threading.Thread(target=self.clean_token_thread, args=(token,))
            threads.append(thread)
            thread.start()
            self.log_info(f"Запущен поток {i} с {len(token)} токенами")

        for thread in threads:
            thread.join()

        self.save_results()
        self.log_info(
            f"Очистка завершена. Успешно: {len(self.cleaned_tokens)}, Неудачно: {len(self.failed_tokens)}"
        )
