"""
Logger class
"""
import datetime

class Logger():
    """
    Log informations about taken actions
    """
    def __init__(self) -> None:
        """
        Initialize Logger
        """
        self.logs_buffer = []

    def log(self, text: str) -> str:
        """
        Saves formatted string into log buffer.
        Args:
            text (str): any valid string, even f-type.

        """
        text = f"{datetime.datetime.now().strftime('%H:%M:%S')} {text}"
        return self.logs_buffer.append(text)

    def reset(self) -> None:
        """
        Reset log buffer.
        """
        self.logs_buffer.clear()
