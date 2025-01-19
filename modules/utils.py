from typing import Any, Optional
from modules import config
import tls_client
import itertools
import logging


class Utils:
    proxy_pool = None

    @staticmethod
    def initialize_proxy_pool() -> None:
        if (
            Utils.proxy_pool is None
            and hasattr(config.Config, "proxies")
            and config.Config.use_proxy
        ):
            try:
                proxies = [
                    p.strip()
                    for p in open("data/proxies.txt", "r", encoding="U8")
                    .read()
                    .split("\n")
                    if p.strip()
                ]
                if proxies:
                    Utils.proxy_pool = itertools.cycle(proxies)
            except Exception as e:
                logging.error(f"Failed to initialize proxy pool: {e}")
                Utils.proxy_pool = None

    @staticmethod
    def get_next_proxy() -> Optional[str]:
        if not config.Config.use_proxy:
            return None

        Utils.initialize_proxy_pool()
        if Utils.proxy_pool is None:
            return None

        try:
            proxy = next(Utils.proxy_pool)
            if proxy and ":" in proxy:
                return f"{config.Config.proxy_type}://{proxy}"
        except Exception as e:
            logging.error(f"Error getting next proxy: {e}")

        return None

    @staticmethod
    def get_session() -> tls_client.Session:
        logger = logging.getLogger("Utils")

        proxy = Utils.get_next_proxy()
        if proxy:
            logger.info(f"Using proxy: {proxy}")
        else:
            logger.warning("No valid proxy available, continuing without proxy")

        session = tls_client.Session(
            timeout_seconds=5,
            client_identifier="firefox_135",
            ja3_string="771,4865-4867-4866-49195-49199-52393-52392-49196-49200-49171-49172-156-157-47-53,0-23-65281-10-11-35-16-5-34-18-51-43-13-45-28-27-65037,4588-29-23-24-25-256-257,0",
            h2_settings={
                "HEADER_TABLE_SIZE": 65536,
                "INITIAL_WINDOW_SIZE": 131072,
                "MAX_FRAME_SIZE": 16384,
            },
            h2_settings_order=[
                "HEADER_TABLE_SIZE",
                "INITIAL_WINDOW_SIZE",
                "MAX_FRAME_SIZE",
            ],
            supported_signature_algorithms=[
                "ECDSAWithP256AndSHA256",
                "PSSWithSHA256",
                "PKCS1WithSHA256",
                "ECDSAWithP384AndSHA384",
                "PSSWithSHA384",
                "PKCS1WithSHA384",
                "PSSWithSHA512",
                "PKCS1WithSHA512",
            ],
            supported_delegated_credentials_algorithms=[
                "ECDSAWithP256AndSHA256",
                "PSSWithSHA256",
                "PKCS1WithSHA256",
                "ECDSAWithP384AndSHA384",
                "PSSWithSHA384",
                "PKCS1WithSHA384",
                "PSSWithSHA512",
                "PKCS1WithSHA512",
            ],
            supported_versions=["GREASE", "1.3", "1.2"],
            key_share_curves=["GREASE", "X25519"],
            cert_compression_algo="brotli",
            pseudo_header_order=[":method", ":authority", ":scheme", ":path"],
            connection_flow=12517377,
            priority_frames=[
                {
                    "streamID": 3,
                    "priorityParam": {
                        "weight": 201,
                        "streamDep": 0,
                        "exclusive": False,
                    },
                },
                {
                    "streamID": 5,
                    "priorityParam": {
                        "weight": 101,
                        "streamDep": 0,
                        "exclusive": False,
                    },
                },
                {
                    "streamID": 7,
                    "priorityParam": {"weight": 1, "streamDep": 0, "exclusive": False},
                },
                {
                    "streamID": 9,
                    "priorityParam": {"weight": 1, "streamDep": 7, "exclusive": False},
                },
                {
                    "streamID": 11,
                    "priorityParam": {"weight": 1, "streamDep": 3, "exclusive": False},
                },
                {
                    "streamID": 13,
                    "priorityParam": {
                        "weight": 241,
                        "streamDep": 0,
                        "exclusive": False,
                    },
                },
            ],
            header_order=[
                ":method",
                ":path",
                ":authority",
                ":scheme",
                "user-agent",
                "accept",
                "accept-language",
                "accept-encoding",
                "origin",
                "sec-fetch-dest",
                "sec-fetch-mode",
                "sec-fetch-site",
                "priority",
                "te",
            ],
            random_tls_extension_order=True,
        )
        if proxy is not None:
            session.proxies = {"http": proxy, "https": proxy}
        return session

    @staticmethod
    def get_default_headers(token, referer: str = "@me") -> dict[str, Any]:
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
            "Accept": "*/*",
            "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Authorization": token,
            "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRmlyZWZveCIsImRldmljZSI6IiIsInN5c3RlbV9sb2NhbGUiOiJydS1SVSIsImhhc19jbGllbnRfbW9kcyI6ZmFsc2UsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChXaW5kb3dzIE5UIDEwLjA7IFdpbjY0OyB4NjQ7IHJ2OjEzNS4wKSBHZWNrby8yMDEwMDEwMSBGaXJlZm94LzEzNS4wIiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTM1LjAiLCJvc192ZXJzaW9uIjoiMTAiLCJyZWZlcnJlciI6IiIsInJlZmVycmluZ19kb21haW4iOiIiLCJyZWZlcnJlcl9jdXJyZW50IjoiIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6MzYwMzIwLCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ==",
            "X-Discord-Locale": "en-US",
            "X-Discord-Timezone": "Europe/Moscow",
            "X-Debug-Options": "bugReporterEnabled",
            "Connection": "keep-alive",
            "Referer": f"https://discord.com/channels/{referer}",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }
