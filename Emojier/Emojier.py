import csv
import itertools
import re
import urllib.request
from math import floor, log2
from typing import Any, Generator, List

import numpy as np
import torch
from icecream import ic
from scipy.special import softmax  # type: ignore
from transformers import AutoModelForSequenceClassification  # type: ignore
from transformers import AutoTokenizer  # type: ignore
from transformers import TFAutoModelForSequenceClassification  # type: ignore

from SemanticMasking import MaskGen

labels = ['❤', '😍', '📷', '🇺🇸', '☀', '💜', '😉', '💯', '😁', '🎄', '📸', '😜', '😂', '☹️', '😭', '😔', '😡', '💢', '😤', '😳', '🙃', '😩', '😠', '💕', '🙈', '🙄', '🔥', '😊', '😎', '✨', '💙', '😘']
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
    dist = itertools.chain(range(max_odd_ind, 0, -2), range(0, max_even_ind + 1, 2))
    return [lst[i] for i in dist]
models_to_choose = [
    "amazon-sagemaker-community/xlm-roberta-en-ru-emoji-v2",
    "AlekseyDorkin/xlm-roberta-en-ru-emoji"
]
BASE_MODEL = models_to_choose[0]
def load_model():
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(BASE_MODEL)
    return model, tokenizer
class Emojier:
  BASE_MODEL = "amazon-sagemaker-community/xlm-roberta-en-ru-emoji-v2"
  model: Any = None
  tokenizer: Any = None
  multiplicityBits = 1
  TopFPercent = 0.2
  @staticmethod
  def setVerbose( v: bool):
    verbose = v
  @staticmethod
  def predict( text: str):
    inputs = Emojier.tokenizer(text, return_tensors="pt")
    outputs = Emojier.model(**inputs)
    logits = outputs.logits.detach().numpy()[0]
    predicted_class = logits.argmax()
    return predicted_class
    
  @staticmethod
  def preprocess(text:str):
      new_text = []
      for t in text.split(" "):
          t = '@user' if t.startswith('@') and len(t) > 1 else t
          t = 'http' if t.startswith('http') else t
          new_text.append(t)
      return " ".join(new_text)
    
  @staticmethod
  def _predict(text:str) -> List[str]:
    # Preprocess text (username and link placeholders)
    preprocessed = Emojier.preprocess(text)
    inputs = Emojier.tokenizer(preprocessed, return_tensors="pt")
    preds = Emojier.model(**inputs).logits
    scores = torch.nn.functional.softmax(preds, dim=-1).detach().numpy()
    sorted_scores = [float(value) for value in np.sort(scores.squeeze())[::-1]]
    ranking = np.argsort(scores)
    ranking = ranking.squeeze()[::-1]
    emojis = [Emojier.model.config.id2label[i] for i in ranking]
    return [emo for emo, score in zip(emojis, sorted_scores) if emo != '🇺🇸' and score > Emojier.TopFPercent]
  
  @staticmethod
  def encode(text:str,bytes_str:str,verbose=False):
    mask = MaskGen(text)
    encoded_so_far = ''
    ticks = [text[:v] for u,v in mask.NVA_words]
    original_length = len(text)
    new_ending = lambda x : (len(text) - original_length) + len(x)
    for pre_text in ticks:
      if verbose:
        print('-'*20 + 'tick' + '-'*20)
      breakPoint = new_ending(pre_text)
      pre_text = text[:breakPoint]
      emoji_options = gaussian_order(Emojier._predict(text[:breakPoint]))
      if len(emoji_options) < 2:
        if verbose:
          print(f'pre_text={pre_text},not enough options={emoji_options}')
        continue
      if bytes_str[0] == "0":
        if verbose:
          print(f'pre_text={pre_text},zero start={bytes_str[:5]}')
        encoded_so_far += bytes_str[0]
        bytes_str = bytes_str[1:]
        continue
      encoded_so_far += bytes_str[0]
      bytes_str = bytes_str[1:] # discard the one
      if verbose:
        print(f"word: {pre_text} \nlen: {len(emoji_options)} \temoji_options: {emoji_options}")
      bits = floor(log2(len(emoji_options)))
      taken_bits = bytes_str[:bits]
      ind = int(taken_bits, 2)
      encoded_so_far += bytes_str[:bits]
      bytes_str = bytes_str[bits:]
      emojis = emoji_options[ind]
      # Mutliplicity
      taken_bits = bytes_str[:Emojier.multiplicityBits]
      mult = int(taken_bits, 2)+1
      encoded_so_far += bytes_str[:Emojier.multiplicityBits]
      bytes_str = bytes_str[Emojier.multiplicityBits:]
      if verbose:
        print(f'encoded_so_far={encoded_so_far}')
      if len(emojis) > 0:
        text = f'{text[0:breakPoint]} {mult * emojis}{text[breakPoint:]}'
      if verbose:
        print(f'>>>encoding {taken_bits} = {ind} as {emojis}\nencoded text={text}')
    return text, bytes_str
  @staticmethod
  def int_to_binary_string(n: int, length: int) -> str:
    binary_str = bin(n)[2:]  # convert to binary string, remove '0b' prefix
    padded_str = binary_str.rjust(length, '0')  # pad with zeros to length
    return padded_str
  @staticmethod
  def cntPrefix(string:str, prefix:str):
    for i in range(4,0,-1):
      # if verbose:
      #   print(f"string={string[:len(prefix*i)]},prefix*i={prefix*i},string.startswith(prefix * i)={string.startswith(prefix * i)}",end='|')
      if string.startswith(prefix * i):
        # print('')
        return i
    # print('')
    return 0
  @staticmethod
  def strip(text:str):
    for label in labels:
      text = text.replace(' '+label,'')
    for label in labels:
      text = text.replace(label,'')
    return text
  @staticmethod
  def decode(text:str,verbose=False):
    if verbose:
      print("#"*20 + "decoding" + "#"*20)
    bytes_str:str = ''
    mask = MaskGen(text)
    # ticks = [text[:v] for u,v in mask.NVA_words if text[u:v] not in labels]
    ticks = [text[:v] for u,v in mask.NVA_words if not any((label in text[u:v] for label in labels))]
    original_length = len(text)
    new_ending = lambda x : (len(text) - original_length) + len(x)
    emoji_locations = []
    for pre_text in ticks:
      if verbose:
        print('-'*20 + 'tick' + '-'*20)
      breakPoint = new_ending(pre_text)
      pre_text = text[:breakPoint]
      if verbose:
        print(f'pre_text={pre_text}')
      emoji_options = gaussian_order(Emojier._predict(text[:breakPoint]))
      emoji = \
          [label for label in labels if text[breakPoint:].startswith(' '+label)][0] \
            if any((text[breakPoint:].startswith(' '+label) for label in labels)) \
              else None
      if emoji is not None:
        bytes_str += '1' # emoji exist
        bits = floor(log2(len(emoji_options)))
        idx = emoji_options.index(emoji)
        bytes_str += Emojier.int_to_binary_string(idx,bits)
        # Multiplicity
        # if verbose:
        #   print('counting multiplicity')
        multi = Emojier.cntPrefix(text[breakPoint+1:],emoji)
        bytes_str += Emojier.int_to_binary_string(multi-1,Emojier.multiplicityBits)
        emoji_locations.append((breakPoint, breakPoint + 1 + len(emoji)*multi))
        if verbose:
          print(f"word={pre_text},len(emoji_options)={len(emoji_options)},emoji_options={emoji_options},emoji={emoji},len(emoji)={len(emoji)},multi={multi}")
      else:
        if len(emoji_options) < 2:
          if verbose:
            print(f"nothing encoded emoji_options={emoji_options}")
        else:
          if verbose:
            print(f"no emoji = zero emoji_options={emoji_options}")
          bytes_str += '0'
      if verbose:
        print(f'bytes_str={bytes_str}')
    # remove emojies
    original = text
    for s,e in reversed(emoji_locations):
      original = original[:s] + original[e:]
    return original, bytes_str
  
Emojier.model, Emojier.tokenizer = load_model()
