import os
import random

import pandas as pd
import spacy
from spellchecker import SpellChecker

# Load SpaCy language model
nlp = spacy.load("en_core_web_sm")

# Create a SpellChecker object
spell = SpellChecker()

def spell_check(text):
    # Parse the text using SpaCy
    correction = []
    tokens = [((match.start(),match.end()),match.groups()[0]) for match in re.finditer(r'([a-zA-Z\']+)',text)]
    
    lastSpanEnd = 0
    for (s,e), token in tokens:
      c = spell.correction(token)
      correction.append(text[lastSpanEnd:s])
      correction.append(c if c is not None else text[s:e])
      lastSpanEnd = e
    correction.append(text[lastSpanEnd:])
    
    return ''.join(correction)


class ConversationsRepo:
  ConversationsCount = 8628
  chat_id = None
  @staticmethod
  def _get(i: int|None = None):
    """gets a chat from the Sample data

    Args:
        i (int): The number of the conversation [1, 8628]
    """
    if i is None:
      i = random.randint(1,ConversationsRepo.ConversationsCount)
    if i < 1 or i > ConversationsRepo.ConversationsCount:
      raise ValueError(i)
    ConversationsRepo.chat_id = i
    
    script_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_directory, 'topical_chat.csv')
    
    df = pd.read_csv(file_path)
    chats = df.groupby('conversation_id')['message'].agg(list)
    chat = chats[i]
    chat = list(map(spell_check,chat))
    return chat
  @staticmethod
  def get(i: int|None = None):
    """gets a chat from the Sample data

    Args:
        i (int): The number of the conversation [1, 8628]
    """
    chat = list(map(spell_check,ConversationsRepo._get(i)))
    return chat