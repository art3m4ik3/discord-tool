from __future__ import annotations
from pystyle import Colorate, Colors, Center
from typing import Tuple, ClassVar
from datetime import datetime
from main import __VERSION__
from modules import config
import random
import os

# ASCII art logo
text_logo = """
▓█████▄  ██▓  ██████  ▄████▄   ▒█████   ██▀███  ▓█████▄    ▄▄▄█████▓ ▒█████   ▒█████   ██▓
▒██▀ ██▌▓██▒▒██    ▒ ▒██▀ ▀█  ▒██▒  ██▒▓██ ▒ ██▒▒██▀ ██▌   ▓  ██▒ ▓▒▒██▒  ██▒▒██▒  ██▒▓██▒
░██   █▌▒██▒░ ▓██▄   ▒▓█    ▄ ▒██░  ██▒▓██ ░▄█ ▒░██   █▌   ▒ ▓██░ ▒░▒██░  ██▒▒██░  ██▒▒██░
░▓█▄   ▌░██░  ▒   ██▒▒▓▓▄ ▄██▒▒██   ██░▒██▀▀█▄  ░▓█▄   ▌   ░ ▓██▓ ░ ▒██   ██░▒██   ██░▒██░
░▒████▓ ░██░▒██████▒▒▒ ▓███▀ ░░ ████▓▒░░██▓ ▒██▒░▒████▓      ▒██▒ ░ ░ ████▓▒░░ ████▓▒░░██████▒
 ▒▒▓  ▒ ░▓  ▒ ▒▓▒ ▒ ░░ ░▒ ▒  ░░ ▒░▒░▒░ ░ ▒▓ ░▒▓░ ▒▒▓  ▒      ▒ ░░   ░ ▒░▒░▒░ ░ ▒░▒░▒░ ░ ▒░▓  ░
 ░ ▒  ▒  ▒ ░░ ░▒  ░ ░  ░  ▒     ░ ▒ ▒░   ░▒ ░ ▒░ ░ ▒  ▒        ░      ░ ▒ ▒░   ░ ▒ ▒░ ░ ░ ▒  ░
 ░ ░  ░  ▒ ░░  ░  ░  ░        ░ ░ ░ ▒    ░░   ░  ░ ░  ░      ░      ░ ░ ░ ▒  ░ ░ ░ ▒    ░ ░
   ░     ░        ░  ░ ░          ░ ░     ░        ░                    ░ ░      ░ ░      ░  ░
 ░                   ░                           ░
"""


class Visual:
    """Handles all visual output formatting and styling."""

    _selected_color: ClassVar[str] = random.choice(Colors().dynamic_colors)

    @staticmethod
    def logo(print_info: bool = True) -> Tuple[str, str]:
        """
        Generates and optionally prints the application logo.

        Args:
            print_info: Whether to print the logo immediately

        Returns:
            Tuple containing the formatted logo and info strings
        """
        logo = Visual.color_theme(Center.XCenter(text_logo))
        info = Visual.color_theme(
            Center.GroupAlign(f"v{__VERSION__}, Автор: art3m4ik3", Center.right)
        )

        if print_info:
            print(logo)
            print(info)
            print()

        return logo, info

    @staticmethod
    def color_theme(text: str) -> str:
        """Applies the selected color theme to text."""
        return Colorate.Horizontal(Visual._selected_color, text)

    @staticmethod
    def build_string(level: str, text: str, color: int) -> str:
        """
        Builds a formatted log string with timestamp and color.

        Args:
            level: Log level (Info/Error/Success/Debug)
            text: Message text
            color: Color code from Colors().static_colors
        """
        timestamp = Visual.color_theme(f"[{datetime.now().strftime('%H:%M:%S')}]")
        colored_text = Colorate.Color(
            Colors().static_colors[color], f"[{level}] {text}"
        )
        return f"{timestamp} {colored_text}"

    # Message type methods
    @staticmethod
    def info(text: str) -> None:
        """Prints an info message."""
        text = Visual.build_string("Инфо", text, 12)
        print(text)

    @staticmethod
    def error(text: str) -> None:
        """Prints an error message."""
        text = Visual.build_string("Ошибка", text, 14)
        print(text)

    @staticmethod
    def success(text: str) -> None:
        """Prints a success message."""
        text = Visual.build_string("Успех", text, 15)
        print(text)

    @staticmethod
    def debug(text: str) -> None:
        """Prints a debug message."""
        text = Visual.build_string("Отладка", text, 16)
        print(text)

    @staticmethod
    def choice(text: str) -> str:
        """
        Prompts user for input with formatted prompt.

        Args:
            text: Prompt text

        Returns:
            User input string
        """
        timestamp = Visual.color_theme(f"[{datetime.now().strftime('%H:%M:%S')}]")
        return input(f"{timestamp} {text} /> ")

    @staticmethod
    def clear() -> None:
        """Clears the terminal screen."""
        os.system("cls" if os.name == "nt" else "clear")
