import csv
import re
import urllib.request
from itertools import chain, islice
from math import floor, log2
from typing import Any, Generator, List

import numpy as np
import torch
from icecream import ic
from scipy.special import softmax
from transformers import (AutoModelForSequenceClassification, AutoTokenizer,
                          TFAutoModelForSequenceClassification)


def pre_texts(string:str)->Generator[str, Any, None]:
  spans = [x.span() for x in re.finditer(r'(\s)+', string)]
  for span in spans:
    yield string[0:span[0]]
  if spans[-1][1] != len(string):
    yield string

def gaussian_order(lst):
  length = len(lst)
  max_odd_ind = length - 1 if length % 2 == 0 else length - 2
  max_even_ind = length - 1 if length % 2 != 0 else length - 2
  dist = chain(range(max_odd_ind,0,-2),range(0,max_even_ind + 1 , 2))
  return [lst[i] for i in dist]

class Emojier:
  BASE_MODEL = "amazon-sagemaker-community/xlm-roberta-en-ru-emoji-v2"
  model: Any = None
  tokenizer: Any = None

  def setVerbose(self, v: bool):
    self.verbose = v

  def __init__(self, interval: int):
    if Emojier.model is None:
        Emojier.model = AutoModelForSequenceClassification.from_pretrained(Emojier.BASE_MODEL)
    if Emojier.tokenizer is None:
        Emojier.tokenizer = AutoTokenizer.from_pretrained(Emojier.BASE_MODEL)
    self.interval = interval
    self.verbose = False

  def predict(self, text: str):
    inputs = Emojier.tokenizer(text, return_tensors="pt")
    outputs = Emojier.model(**inputs)
    logits = outputs.logits.detach().numpy()[0]
    predicted_class = logits.argmax()
    return predicted_class
    
  def preprocess(self,text:str):
      new_text = []
      for t in text.split(" "):
          t = '@user' if t.startswith('@') and len(t) > 1 else t
          t = 'http' if t.startswith('http') else t
          new_text.append(t)
      return " ".join(new_text)
    
  def _predict(self,text:str) -> List[str]:
    # Preprocess text (username and link placeholders)
    preprocessed = self.preprocess(text)
    inputs = Emojier.tokenizer(preprocessed, return_tensors="pt")
    preds = Emojier.model(**inputs).logits
    scores = torch.nn.functional.softmax(preds, dim=-1).detach().numpy()
    # sorted_scores = [float(value) for value in np.sort(scores.squeeze())[::-1]]
    ranking = np.argsort(scores)
    ranking = ranking.squeeze()[::-1]
    emojis = [Emojier.model.config.id2label[i] for i in ranking]
    # return dict(zip(emojis, sorted_scores))
    return list(filter(lambda x : x != '🇺🇸',emojis))
  
  def encode(self,text:str,bytes_str:str):
    ticks = islice(pre_texts(text), 0, None, self.interval)
    original_length = len(text)
    new_ending = lambda x : (len(text) - original_length) + len(x)
    for pre_text in ticks:
      breakPoint = new_ending(pre_text)
      emoji_options = gaussian_order(self._predict(text[:breakPoint]))

      if bytes_str[0] == "0":
        bytes_str = bytes_str[1:]
        continue
      if self.verbose:
        print(f"word: {pre_text} \nlen: {len(emoji_options)} \temoji_options: {emoji_options}")

      bits = floor(log2(len(emoji_options)))
      taken_bits = bytes_str[:bits]
      ind = int(taken_bits, 2)
      bytes_str = bytes_str[bits:]
      emojis = emoji_options[ind]

      # Mutliplicity
      taken_bits = bytes_str[:2]
      mult = int(taken_bits, 2)+1
      bytes_str = bytes_str[2:]
      
      if len(emojis) > 0:
        text = f'{text[0:breakPoint]} {mult * emojis}{text[breakPoint:]}'
      if self.verbose:
        print(f'>>>encoding {taken_bits} = {ind} as {emojis}\nencoded text={text}')
    return text, bytes_str