from dataclasses import dataclass, field
from typing import Dict, Optional, Literal,List

from .Person import Person

@dataclass
class Message:
    person: Person
    text: str
    def __str__(self):
      return f"{self.person.first_name}: `{self.text}`"
    def __repr__(self):
      return f"{self.person.first_name}: `{self.text}`"


