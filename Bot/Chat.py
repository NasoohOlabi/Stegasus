from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional

from .Message import Message
from .Person import Person


class Chat:
    messages: List[Message]
    correspondents: List[Person]

    def __init__(self, friend1: Person,friend2: Person,askGPT):
      self.correspondents = [friend1,friend2]
      self.askGPT = askGPT
      self.messages = []

    def setup(self):
      return f"{self.correspondents[0].get_description()} and {self.correspondents[1].get_description()}. and they have been friends for a long time"
    def chat_prompt(self):
      chat_str = '\n'.join([f"{message.person.first_name}: {message.text}" for message in self.messages])
      return f"Can you please continue this chat(keep chat going and interesting ask many questions)\n```{chat_str}```"
    def reply_message(self)-> Optional[Message]:
      reply = self.askGPT(self.chat_prompt())
      reply = ':'.join(reply.split(':')[1:])
      if len(reply.strip()) == 0:
        return None
      last_person = self.messages[-1].person
      replier = list(filter(lambda x : x.first_name != last_person.first_name,self.correspondents))[0]
      return Message(person=replier,text=reply)
    def chat_next(self):
      reply = self.reply_message()
      if reply is None:
        return False
      self.messages.append(reply)
      return True
    
    def start_conversation_with_post(self,post):
      return f"{self.setup()}. if you are {self.correspondents[0].first_name} and you want to tell {self.correspondents[1].first_name} about this post and your take on the topic `{post}` what would you send to {self.correspondents[1].him()} in chat (keep the chat going and ask many questions)?"
    def next(self):
      if len(self.messages) == 0:
        raise Exception("Can't continue a nonexisting conversation!")
        # self.messages.append(Message(person=self.correspondents[0],text=self.askGPT(self.start_conversation_with_post(demo_post))))
      else:
        return self.chat_next()

    def render(self):
      lineHalfLen = 21
      print(f"{'-'*lineHalfLen} Chat {'-'*lineHalfLen}")
      for c in self.messages:
        print(c)
      print('-'*(lineHalfLen*2+6))
      
    def stream(self):
      for message in self.messages:
        yield message
      while self.next():
        yield self.messages[-1] 