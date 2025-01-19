from modules import config, visual, utils
from datetime import datetime
from typing import List
import threading
import json


class ServerJoiner:
    def __init__(self) -> None:
        self.invite_code = visual.Visual.choice(
            "Введите код приглашения (например, zalupa)"
        )
        self.invite_code = self.invite_code.split("/")[-1]  # Extract invite code
        self.tokens = config.Config.tokens
        self.joined_tokens = []
        self.failed_tokens = []

        self.join_server()

    def save_results(self) -> None:
        with open("output/joined_servers.json", "w") as f:
            json.dump(self.joined_tokens, f, indent=4)
        with open("output/failed_servers.json", "w") as f:
            json.dump(self.failed_tokens, f, indent=4)

    def join_server_thread(self, tokens: List[str]) -> None:
        session = utils.Utils.get_session()

        for token in tokens:
            headers = utils.Utils.get_default_headers(token)
            try:
                join_response = session.post(
                    f"https://discord.com/api/v9/invites/{self.invite_code}",
                    headers=headers,
                )

                if join_response.status_code == 200:
                    visual.Visual.success(
                        f"Токен {token[:10]}... успешно присоединился к серверу"
                    )
                    self.joined_tokens.append(
                        {"token": token, "timestamp": datetime.now().isoformat()}
                    )
                elif join_response.status_code == 429:
                    visual.Visual.error(f"Ratelimit для токена {token[:10]}...")
                    self.failed_tokens.append(
                        {
                            "token": token,
                            "reason": "ratelimit",
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                else:
                    visual.Visual.error(
                        f"Токен {token[:10]}... не смог присоединиться к серверу. Код: {join_response.status_code}, Ответ: {join_response.text}"
                    )
                    self.failed_tokens.append(
                        {
                            "token": token,
                            "reason": join_response.text,
                            "timestamp": datetime.now().isoformat(),
                            "status_code": join_response.status_code,
                        }
                    )
            except Exception as e:
                visual.Visual.error(
                    f"Ошибка при присоединении токена {token[:10]}...: {e}"
                )
                self.failed_tokens.append(
                    {
                        "token": token,
                        "reason": str(e),
                        "timestamp": datetime.now().isoformat(),
                    }
                )

    def join_server(self) -> None:
        threads = []
        chunk_size = len(self.tokens) // config.Config.thread_count
        for i in range(config.Config.thread_count):
            start = i * chunk_size
            end = start + chunk_size
            thread = threading.Thread(
                target=self.join_server_thread, args=(self.tokens[start:end],)
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        self.save_results()
        visual.Visual.info(
            f"Присоединение завершено. Успешно: {len(self.joined_tokens)}, Неудачно: {len(self.failed_tokens)}"
        )
