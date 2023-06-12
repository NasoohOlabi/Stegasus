#@title Person
from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional


@dataclass
class Person:
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    city: Optional[str] = None
    email: Optional[str] = None
    favorites: Dict[str, str] = field(default_factory=dict)
    interests: List[str] = field(default_factory=list)

    def get_description(self):
        description = f"{self.first_name}{' '+self.last_name if self.last_name is not None else ''} is a "

        if self.age:
            description += f"{self.age} years old " 

        if self.gender:
            description += f"{self.gender} "

        if self.city:
            description += f"who lives in {self.city} "
        filler = ["and","Who's"]
        favorites_str = ''
        if len(self.favorites) > 0:
          description += filler.pop()
          if self.favorites:
              favorites_list = [f"{key} is {value}" for key, value in self.favorites.items()]
              favorites_str = " and ".join(favorites_list)
              favorites_str = f" favorite {favorites_str} "
          description += favorites_str
        interests_str=''
        if len(self.interests) > 0:
          description += filler.pop()
          if self.interests:
              interests_list = [f"{value}" for value in self.interests]
              interests_str = ", ".join(interests_list)
              interests_str = f" interests are {interests_str}."
          description += interests_str

        return description


    def add_favorite(self, category: str, favorite: str):
        self.favorites[category] = favorite
        return self

    def add_interest(self, interest: str):
        self.interests.append(interest)
        return self
    def him(self):
      if self.gender == 'boy' or self.gender == 'male':
        return 'him'
      else:
        return 'her'
            
