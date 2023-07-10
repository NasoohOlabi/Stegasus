import os
import random

import pandas as pd


class ConversationsRepo:
  ConversationsCount = 8628
  @staticmethod
  def get(i: int|None = None):
    """gets a chat from the Sample data

    Args:
        i (int): The number of the conversation [1, 8628]
    """
    if i is None:
      i = random.randint(1,ConversationsRepo.ConversationsCount)
    if i < 1 or i > ConversationsRepo.ConversationsCount:
      raise ValueError(i)
    
    script_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_directory, 'topical_chat.csv')
    
    df = pd.read_csv(file_path)
    chats = df.groupby('conversation_id')['message'].agg(list)
    return chats[i]