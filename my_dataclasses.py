from dataclasses import dataclass
from typing import List


@dataclass
class Code:  # Класс который просто содержит букву и соответствующей ей код
    letter: str
    code: str


@dataclass
class ReturnData:  # Класс который содержит закодированный текст + набор кодов
    encoded_text: str
    codes: List[Code]
