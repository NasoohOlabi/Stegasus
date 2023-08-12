import csv
import itertools
import os
import re
from math import inf, log2
from typing import Any, Generator, List, Literal, Optional, Tuple

import numpy as np
import torch
from icecream import ic
from scipy.special import softmax  # type: ignore
from transformers import AutoModelForSequenceClassification  # type: ignore
from transformers import AutoTokenizer  # type: ignore
from transformers import TFAutoModelForSequenceClassification  # type: ignore

from ..SemanticMasking import MaskGen
from .StringSpans import StringSpans

script_directory = os.path.dirname(os.path.abspath(__file__))


labels = ['❤', '😍', '📷', '🇺🇸', '☀', '💜', '😉', '💯', '😁', '🎄', '📸', '😜', '😂', '☹️', '😭', '😔', '😡', '💢', '😤', '😳', '🙃', '😩', '😠', '💕', '🙈', '🙄', '🔥', '😊', '😎', '✨', '💙', '😘']

augmentation_map = {'❤': ['💓', '💖', '💗', '💘', '💞', '💟'],
 '😍': ['😻', '🥰','🤩'],
 '📷': ['🎥', '📹', '🎞️', '📽️'],
 '☀': ['🌞', '🌅', '🌄', '🌤️', '🌻', '🌼'],
 '💜': ['❤️', '🤎', '🖤', '🤍'],
 '😉': ['😏', '😋', '😼', '😌', '😬'],
 '💯': ['👌','👍','👍🏻','👍🏼','👍🏽','👍🏾','👍🏿'],
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
  
  def __init__(self,text:str,span_size=5):
    self.text = text
    self.span_size = span_size
    self._slots: Optional[List[List[Tuple[int,str]]]] = None
    self._spaces: Optional[List[int]] = None
    self._bits: Optional[List[int]] = None
    
  def getSlots(self) -> List[List[Tuple[int,str]]]:
    if not self._slots is None:
      return self._slots
    self._slots = []
    pre_slots = []
    text = self.text
    Emojier.info(f"getSlots({text})")
    mask = MaskGen(text)
    ss = StringSpans(text)
    ticks = [(text[:v],(u,v)) for u,v in mask.NVA_words if (u,v) in ss.words]
    for pre_text, (u,v) in ticks:
      breakPoint = len(pre_text)
      pre_text = text[:breakPoint]
      Emojier.log('Slots>'+'-'*20 + 'tick' + '-'*20 + pre_text)
      emoji_options = gaussian_order(Emojier._predict(text[:breakPoint]))
      if len(emoji_options) < 2:
        Emojier.log('Slots>'+f'word={text[u:v]},range={(0,breakPoint)},not enough options={emoji_options}')
        continue
      
      pre_slots.append((breakPoint,emoji_options))
      
      Emojier.log('Slots>'+f"word={text[u:v]},range={(0,breakPoint)},{len(emoji_options)}=len({emoji_options})")
      
    Emojier.info(f"detected {len(pre_slots)} slots in: {text}")
    self._slots = []
    for idx, slot in enumerate(pre_slots):
      breakPoint, emoticons = slot
      if len(self._slots) == 0 or idx % self.span_size == 0:
        self._slots.append([])
      for emo in emoticons:
        self._slots[-1].append((breakPoint,emo))
    return self._slots
  
  def getSlot(self,space:int,offset:int) -> Tuple[int,str]:
    return self.getSlots()[space][offset]
  
  def getSpaces(self) -> List[int]:
    if self._spaces is None:
      self._spaces = [len(slot) for slot in self.getSlots()]
    return self._spaces
  def getSpace(self,i:int):
    return self.getSpaces()[i]
  def getBits(self) -> List[int]:
    if self._bits is None:
      self._bits = [int(log2(space)) for space in self.getSpaces()]
    return self._bits
  def getBit(self,i: int) -> int:
    return self.getBits()[i]
  
  def encode_encoder(self,bytes_str:str) -> Tuple[List[int],str]:
    """Encodes a bytes string using the given spaces and bits list.

    Args:
      bytes_str: The bytes string to encode.
      spaces: A list of integers representing the number of possible values for each
        bit in the encoded string.
      bits_list: A list of integers representing the number of bits in each byte
        of the encoded string.

    Returns:
      A tuple of (list of integers, string) representing the encoded bits and the
        remaining unencoded bits.

    Raises:
      ValueError: If `bytes_str` is not a valid bytes string.
    """

    if not all(c in ('0', '1') for c in bytes_str):
      raise ValueError("bytes_str isn't a bytes string : '{}'".format(bytes_str))

    bit_values = []
    remaining_bits = bytes_str
    for i in range(len(self.getBits())):
      bits = self.getBit(i)
      if len(remaining_bits) >= bits + 1 and int(remaining_bits[:bits + 1], 2) < self.getSpace(i) and \
          int(remaining_bits[:bits + 1], 2) >= 2**bits:
        bit_value = int(remaining_bits[:bits + 1], 2)
        bit_values.append(bit_value)
        remaining_bits = remaining_bits[bits + 1:]
      elif len(remaining_bits) >= bits and bits > 0:
        bit_value = int(remaining_bits[:bits], 2)
        bit_values.append(bit_value)
        remaining_bits = remaining_bits[bits:]
      else:
        bit_values.append(0)

    return bit_values, remaining_bits

  def decode_decoder(self,values: List[int]) -> str:
    """Decodes a list of integers using the given spaces and bits list.

    Args:
      values: The list of integers to decode.
      spaces: A list of integers representing the number of possible values for each
        bit in the encoded string.
      bits_list: A list of integers representing the number of bits in each byte
        of the encoded string.

    Returns:
      A string representing the decoded bytes.

    Raises:
      ValueError: If `values` is not a valid list of integers.
    """

    if not all(isinstance(v, int) for v in values):
      raise ValueError("values isn't a valid list of integers : '{}'".format(values))

    res = []
    for i in range(len(self.getBits())):
      space = self.getSpace(i)
      value_to_convert = values[i]
      if space == 0:
        continue
      bits = self.getBit(i)
      v = bin(value_to_convert).replace("0b", "")
      v = "0" * max(bits - len(v), 0) + v
      res.append(v)

    return "".join(res)

  @staticmethod
  def predict(text: str):
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
  
  def _encode(self,values:List[int]):
    spaces = self.getSpaces();
    if (len(values) > len(spaces)):
      raise ValueError("Can't encode")

    for i,value in enumerate(values):
      if value >= spaces[i] and spaces[i] != 0:
          raise ValueError("Won't fit");
        

    result = self.text;
    for i in range(len(values)-1,-1,-1):
      if values[i] != 0:
        breakPoint, emoji = self.getSlot(i, values[i])
        result = f'{result[0:breakPoint]} {emoji}{result[breakPoint:]}'
        
    return result
    
  def encode(self,bytes_str:str):
    values, rem = self.encode_encoder(bytes_str)
    Emojier.info(f"encode({self.text}, {bytes_str}),values={values},rem={rem}")
    return self._encode(values), rem
  
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
    logfile = './Emojier.log'
    with open(logfile,'a', encoding='utf-8') as f:
      f.write(str(string)+'\n') 
  @staticmethod
  def info(string:str):
    if Emojier.verbose:
      print(string)
    infoFile = './Emojier.info'
    with open(infoFile,'a', encoding='utf-8') as f:
      f.write(string+'\n') 
  @staticmethod
  def strip(text:str):
    for label in augmented_labels:
      text = text.replace(' '+label,'')
    for label in augmented_labels:
      text = text.replace(label,'')
    return text
  def first_unequal(self,a:str,b:str) -> int|float:
    for i, (x,y) in enumerate(zip(a,b)):
      if x != y:
        return i
    if len(a) == len(b):
      return inf
    else:
      return min(len(a),len(b)) 
  def _decode(self, encoded: str):
    slots = self.getSlots()
    values = [0 for _ in slots]
    old_first_unequal = self.first_unequal(encoded,self.text)
    for i,space_slots in enumerate(slots):
      maxValue = 0
      for j, (_,emoji) in enumerate(space_slots):
        values[i] = j
        tmp = self._encode(values)
        diff = self.first_unequal(encoded,tmp)
        if diff > old_first_unequal:
          old_first_unequal = diff
          maxValue = j
      values[i] = maxValue
    Emojier.info(f'decode values={values}')
    return self.decode_decoder(values)
        
  @staticmethod
  def decode(encoded_text:str, span_size=5):
    text = encoded_text
    text = Emojier.strip(text)
    clear_text = text
    emo = Emojier(text,span_size)
    return clear_text , emo._decode(encoded_text)
    
Emojier.model, Emojier.tokenizer = load_model()
