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

from .StringSpans import StringSpans

labels = ['❤', '😍', '📷', '🇺🇸', '☀', '💜', '😉', '💯', '😁', '🎄', '📸', '😜', '😂', '☹️', '😭', '😔', '😡', '💢', '😤', '😳', '🙃', '😩', '😠', '💕', '🙈', '🙄', '🔥', '😊', '😎', '✨', '💙', '😘']

augmentation_map = {'❤': ['💓', '💖', '💗', '💘', '💞', '💟'],
 '😍': ['😻', '🥰','🤩'],
 '📷': ['🎥', '📹', '🎞️', '📽️'],
 '☀': ['🌞', '🌅', '🌄', '🌤️', '🌻', '🌼'],
 '💜': ['❤️', '🤎', '🖤', '🤍'],
 '😉': ['😏', '😋', '😼', '😌', '😬'],
 '💯': ['👌'],
 '😁': ['😀', '😃', '😆', '😄', '😅', '😸'],
 '🎄': ['🎅', '🤶', '🎁', '🌟', '🌲'],
 '📸': [],
 '😜': ['😝', '😛'],
 '😂': ['🤣', '😹'],
 '☹️': ['🙁', '😞', '😖'],
 '😭': ['😢', '😥', '😪', '😓'],
 '😔': ['😟', '😕'],
 '😡': ['😣', '👿'],
 '💢': ['💥', '💨', '💣', '💫'],
 '😤': ['😒'],
 '😳': ['😮', '😯', '😲', '🙀', '😱'],
 '🙃': [],
 '😩': ['😫'],
 '😠': ['😾'],
 '💕': ['💔'],
 '🙈': ['🙉', '🙊', '🐵', '🐒', '🐾'],
 '🙄': ['😑', '🤨','😐'],
 '🔥': ['🌋', '🚒'],
 '😊': ['🙂'],
 '😎': ['🕶️', '🍻'],
 '✨': ['🔮', '🎉'],
 '💙': ['💚', '💛', '🧡'],
 '😘': ['😗', '😚', '😙']}

augmented_labels = list(augmentation_map.keys()) + [e for l in augmentation_map.values() for e in l]

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
  multiplicity = 3
  TopFPercent = 0.1
  verbose = False
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
  def _augment(emoticons:List[str]) -> List[str]:
    augmented = []
    for e in emoticons:
      augmented.append(e)
      for x in augmentation_map[e]:
        augmented.append(x)
    Emojier.log(f"_augment({emoticons}) = {augmented}")
    return augmented
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
    emoticons = [emo for emo, score in zip(emojis, sorted_scores) if emo != '🇺🇸' and score > Emojier.TopFPercent]
    return Emojier.addMultiplicities(
        Emojier._augment(
          emoticons
        )
      )
  @staticmethod
  def addMultiplicities(emoticons: List[str]):
    new_emoticons = []
    for emo in emoticons:
      for i in range(1,Emojier.multiplicity+1):
        new_emoticons.append(emo * i)
    return new_emoticons
  @staticmethod
  def encode(text:str,bytes_str:str):
    Emojier.info(f"encode({text}, {bytes_str})")
    mask = MaskGen(text)
    encoded_so_far = ''
    ss = StringSpans(text)
    ticks = [(text[:v],(u,v)) for u,v in mask.NVA_words if (u,v) in ss.words]
    original_length = len(text)
    curr_offset = lambda : (len(text) - original_length)
    new_ending = lambda x : curr_offset() + len(x)
    for pre_text, (u,v) in ticks:
      u, v = (u + curr_offset(), v+ curr_offset())
      breakPoint = new_ending(pre_text)
      pre_text = text[:breakPoint]
      Emojier.log('E>'+'-'*20 + 'tick' + '-'*20 + pre_text)
      emoji_options = gaussian_order(Emojier._predict(text[:breakPoint]))
      if len(emoji_options) < 2:
        Emojier.log('E>'+f'word={text[u:v]},range={(0,breakPoint)},not enough options={emoji_options}')
        continue
      if bytes_str[0] == "0":
        Emojier.log('E>'+f'word={text[u:v]},range={(0,breakPoint)},zero start={bytes_str[:5]}')
        encoded_so_far += bytes_str[0]
        bytes_str = bytes_str[1:]
        continue
      encoded_so_far += bytes_str[0]
      bytes_str = bytes_str[1:] # discard the one
      bits = floor(log2(len(emoji_options)))
      taken_bits = bytes_str[:bits]
      ind = int(taken_bits, 2)
      encoded_so_far += bytes_str[:bits]
      bytes_str = bytes_str[bits:]
      emoji = emoji_options[ind]
      Emojier.log('E>'+f"word={text[u:v]},range={(0,breakPoint)},len({emoji})={len(emoji)},{len(emoji_options)}=len({emoji_options})")
      Emojier.log('E>'+f'encoded_so_far={encoded_so_far}')
      if len(emoji) > 0:
        text = f'{text[0:breakPoint]} {emoji}{text[breakPoint:]}'
    Emojier.info(f"encoded {encoded_so_far} as: {text}")
    return text, bytes_str
  @staticmethod
  def int_to_binary_string(n: int, length: int) -> str:
    binary_str = bin(n)[2:]  # convert to binary string, remove '0b' prefix
    padded_str = binary_str.rjust(length, '0')  # pad with zeros to length
    return padded_str
  @staticmethod
  def cntPrefix(string:str, prefix:str):
    for i in range(4,0,-1):
    #   Emojier.log(f"string={string[:len(prefix*i)]},prefix*i={prefix*i},string.startswith(prefix * i)={string.startswith(prefix * i)}",end='|')
      if string.startswith(prefix * i):
        # Emojier.log('')
        return i
    # Emojier.log('')
    return 0
  @staticmethod
  def log(string:str):
    if Emojier.verbose:
      print(string)
    with open('Emojier.log','a', encoding='utf-8') as f:
      f.write(string+'\n') 
  @staticmethod
  def info(string:str):
    if Emojier.verbose:
      print(string)
    with open('Emojier.info','a', encoding='utf-8') as f:
      f.write(string+'\n') 
  @staticmethod
  def strip(text:str):
    for label in augmented_labels:
      text = text.replace(' '+label,'')
    for label in augmented_labels:
      text = text.replace(label,'')
    return text
  @staticmethod
  def decode(encoded_text:str):
    text = encoded_text
    text = Emojier.strip(text)
    clear_text = text
    mask = MaskGen(text)
    decoded_so_far = ''
    ss = StringSpans(text)
    ticks = [(text[:v],(u,v)) for u,v in mask.NVA_words if (u,v) in ss.words]
    original_length = len(text)
    curr_offset = lambda : (len(text) - original_length)
    new_ending = lambda x : curr_offset() + len(x)
    for pre_text, (u,v) in ticks:
      u, v = (u + curr_offset(), v+ curr_offset())
      breakPoint = new_ending(pre_text)
      pre_text = text[:breakPoint]
      Emojier.log('D>'+'-'*20 + 'tick' + '-'*20 + pre_text)
      emoji_options = gaussian_order(Emojier._predict(text[:breakPoint]))
      if len(emoji_options) < 2:
        Emojier.log('D>'+f'word={text[u:v]},range={(0,breakPoint)},not enough options={emoji_options}')
        continue
      
      emoji = None
      if any((encoded_text[breakPoint:].startswith(' '+label) for label in emoji_options)):
        emoticons = [label for label in emoji_options if encoded_text[breakPoint:].startswith(' '+label)]
        emoticons.sort(key= lambda x: len(x),reverse=True)
        emoji = emoticons[0]
              
      if emoji is None:
        Emojier.log('D>'+f'word={text[u:v]},range={(0,breakPoint)},zero start={text[breakPoint:breakPoint+5]}')
        decoded_so_far += "0"
        continue
      decoded_so_far += "1"
      bits = floor(log2(len(emoji_options)))
      idx = emoji_options.index(emoji)
      decoded_so_far += Emojier.int_to_binary_string(idx,bits)
      text = f'{text[0:breakPoint]} {emoji}{text[breakPoint:]}'
      Emojier.log('D>'+f"word={text[u:v]},range={(0,breakPoint)},len({emoji})={len(emoji)},{len(emoji_options)}=len({emoji_options})")
      Emojier.log('D>'+f'decoded_so_far={decoded_so_far}')
    return clear_text, decoded_so_far  
    
Emojier.model, Emojier.tokenizer = load_model()
