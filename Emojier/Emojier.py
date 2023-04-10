# credit https://github.com/farkmarnum/emojify
import itertools
import json
import os
import random
import re
from math import ceil, floor, log2
from typing import Dict, Generator, List, Tuple

from Stegasus.util.StringSpans import StringSpans


def random_bit_stream(length=None):
    """Return a random string of zeros and ones of the given length (default: random integer between 0 and 100)."""
    if length is None:
        length = random.randint(0, 100)
    return ''.join(str(random.randint(0, 1)) for _ in range(length))
def int_to_binary_string(n: int, length: int):
    binary_str = bin(n)[2:]  # convert to binary string, remove '0b' prefix
    padded_str = binary_str.rjust(length, '0')  # pad with zeros to length
    return padded_str

# Get the path of the script
script_path = os.path.abspath(__file__)

ROOT_DIR = os.path.dirname(script_path)

emoticons_file = ROOT_DIR + '/emoji-data.json'

with open(emoticons_file, 'r') as f:
		emoji_data: Dict[str,Dict[str,List[str]]] = json.load(f)


regex = re.compile(r'[a-z0-9]+')
ALL_EMOJIS = set()
for k,v in emoji_data.items():
  if regex.match(k) is None:
    ALL_EMOJIS.add(k)
    # print('k',k)
  if isinstance(v,str) and regex.match(v) is None:
    ALL_EMOJIS.add(v)
    # print('v',v)
  elif isinstance(v,dict):
    for kk,vv in v.items():
      if regex.match(kk) is None:
        ALL_EMOJIS.add(kk)
        # print('kk',kk)
      if isinstance(vv,str) and regex.match(vv) is None:
        ALL_EMOJIS.add(v)
        # print('vv',vv)
EMOJIER_COMMON_WORDS = {
    'a',
    'an',
    'as',
    'is',
    'if',
    'of',
    'the',
    'it',
    'its',
    'or',
    'are',
    'this',
    'with',
    'so',
    'to',
    'at',
    'was',
    'and',
  }

class Emojier:
  @staticmethod
  def gaussian_order(lst):
    length = len(lst)
    max_odd_ind = length - 1 if length % 2 == 0 else length - 2
    max_even_ind = length - 1 if length % 2 != 0 else length - 2
    dist = itertools.chain(range(max_odd_ind,0,-2),range(0,max_even_ind + 1 , 2))
    return [lst[i] for i in dist]

  @staticmethod
  def encode(
        input_str: str,
        bytes_str: str,
        verbose=False,
        mask=True,
        maskStep: int =6,
        topX=False,
        X: float=0.15
    ) -> Tuple[str,str]:
    
    if verbose:
      print('encode:')
    input_str_spans = StringSpans(input_str)
    word_span_n_words = zip(input_str_spans.words, input_str_spans.get_words())
    result = input_str
    acc_offset = 0
    
    word_span_n_words_options: List[Tuple[int,str,List[str]]] = []
    for (_,we), word_raw in word_span_n_words:
      word = word_raw.lower()
      is_too_common = word in EMOJIER_COMMON_WORDS

      emoji_options = \
        Emojier.gaussian_order( ['']+
          [x[0] for x in
            sorted(
              emoji_data.get(word, {}).items(),
              key=lambda x:x[1],
              reverse=True
            )
          ]
        )
      if not is_too_common and len(emoji_options)>=2:
        word_span_n_words_options.append((we,word_raw, emoji_options))
    
    if mask:
      word_span_n_words_options = word_span_n_words_options[::maskStep]
    if topX:
      word_span_n_words_options.sort(key=lambda tup : len(tup[2]),reverse=True)
      taken_elements = ceil(len(word_span_n_words_options) * X) 
      word_span_n_words_options = word_span_n_words_options[:taken_elements]
      
    for we, word_raw, emoji_options in word_span_n_words_options:
      word = word_raw.lower()

      if verbose:
        print(f"word: {word} \nlen: {len(emoji_options)} \temoji_options[:10]: {emoji_options[:10]}")

      bits = floor(log2(len(emoji_options)))
      taken_bits = bytes_str[:bits]
      ind = int(taken_bits, 2)
      bytes_str = bytes_str[bits:]
      emojis = emoji_options[ind]
      if len(emojis) > 0:
        we = we + acc_offset
        acc_offset += len(emojis) + 1
        if verbose:
          print(f'>>>encoding {taken_bits} = {ind} as {emojis}\nwe={we}\tacc_offset={acc_offset}')
          print(f'result[:we]="{result[:we]}" result[we:]="{result[we:]}"')  
        result = f'{result[:we]} {emojis}{result[we:]}'  

    return result, bytes_str

  @staticmethod
  def eat_back(s:str) -> Generator[str,None,None]:
    for i in range(len(s),-1,-1):
      yield s[0:i]
  @staticmethod
  def decode(
            input_str: str,
            verbose=False,
            mask: bool =True,
            maskStep: int =6,
            topX: bool =False,
            X: float=0.15
      ) -> Tuple[str,str]:
    
    if verbose:
      print('decoding!')
    wordish = re.compile(r'^[a-z]*$')
    input_str_ss = StringSpans(input_str)
    words = [input_str[s:e] for s,e in input_str_ss.non_spaces]
    result = input_str
    bytes_str = ''
    
    emoticons_used = []
    word_span_n_words_options: List[Tuple[int,str,List[str]]] = []
    for i, word_raw in enumerate(words[:-1]):
      word = word_raw.lower()
      
      if wordish.match(word) is None:
        continue 

      is_too_common = word in EMOJIER_COMMON_WORDS

      emoji_options = \
        Emojier.gaussian_order( ['']+
          [x[0] for x in
            sorted(
              emoji_data.get(word, {}).items(),
              key=lambda x:x[1],
              reverse=True
            )
          ]
        )
      if not is_too_common and len(emoji_options) >= 2:
        word_span_n_words_options.append((i,word_raw,emoji_options))

    if mask:
      word_span_n_words_options = word_span_n_words_options[::maskStep]
    if topX:
      word_span_n_words_options.sort(key=lambda tup : len(tup[2]),reverse=True)
      taken_elements = ceil(len(word_span_n_words_options) * X) 
      word_span_n_words_options = word_span_n_words_options[:taken_elements]
        
    for i, word_raw, emoji_options in word_span_n_words_options:
      word = word_raw.lower()

      if verbose:
        print(f"word: {word} \nlen: {len(emoji_options)} \temoji_options[:10]: {emoji_options[:10]}")

      bits = floor(log2(len(emoji_options)))
      index = 0
      for w in Emojier.eat_back(words[i+1]):
        if w in emoji_options:
          index = emoji_options.index(w)
          emoticons_used.append((w,i+1))
          break
        
      data_extracted = int_to_binary_string(index,bits)
      if verbose:
        print(f'>>>decoding word:"{words[i]}" next word:"{words[i+1]}" length:"{len(emoji_options)}"')
        print(f'bits:"{bits}" data extracted:"{data_extracted}" index:"{index}"')
      bytes_str += data_extracted

    for emo,idx in reversed(emoticons_used):
      s,e = input_str_ss.non_spaces[idx]
      if emo:
        result = result[:s-1] + result[s:e].replace(emo,'') + result[e:]
  
    return result, bytes_str
