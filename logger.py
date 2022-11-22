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
        self.log_buffer = []

    def log(self, text: str) -> str:
        """
        Saves formatted string into log buffer.
        Args:
            text (str): any valid string, even f-type.

        """
        text = f"{datetime.datetime.now().strftime('%H:%M:%S')} {text}"
        return self.log_buffer.append(text)

    def reset(self) -> None:
        """
        Reset log buffer.
        """
        self.log_buffer.clear()
