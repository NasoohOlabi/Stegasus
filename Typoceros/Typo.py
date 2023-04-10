# Get the path of the script
from dataclasses import dataclass, field
from math import log2
from typing import Callable, Generator, List, Optional, Tuple

import regex as re

from .util import *


@dataclass
class Typo:
   """Class for Typo Engine."""

   text: str = field(repr=False)
   _length: int = field(init=False, repr=False)
   _slots: Optional[List[Tuple[Tuple[int, int], str, re.Pattern]]] = field(init=True, repr=False,default=None)
   _spaces: Optional[List[int]] = field(init=True, repr=False,default=None)
   verbose: bool = field(init=True,repr=False,default=False)

   def __post_init__(self):
      if self.text != normalize(self.text,self.verbose):
         raise ValueError("Text isn't spelled correctly")
   @staticmethod
   def isAcceptable(text:str,verbose:bool=False):
      return text == normalize(text,verbose)
   @staticmethod
   def FixText(text:str,verbose=False):
      return normalize(text,verbose)
   def apply(self, space: int, offset: int, text: str) -> str:
      if self.verbose:
         print(f"apply: space={space}, offset={offset}, text={text}")
      if offset == 0:
         return text
      match_tuple = self.slots[sum(self.spaces[0:space]) + offset - 1]
      applied = apply_match(text, match_tuple,self.verbose)
      if self.verbose:
         print(f"applied: {applied}")
      return applied
   @property
   def slots(self):
      if self._slots is None:
         self._slots = valid_rules_scan(self.text,self.verbose)
      return self._slots
   @property
   def length(self) -> int:
      return len(self.slots)
   @length.setter
   def length(self, length: int):
      pass
   @property
   def spaces(self) -> List[int]:
      if self._spaces is not None:
         return self._spaces
      
      sentence_ranges = chunker(self.text)
      
      # Initialize an empty list of buckets
      num_buckets = len(sentence_ranges)
      buckets: List[int] = [0 for _ in range(num_buckets)]
      
      # Iterate through each element range and put it in the corresponding bucket
      for i, (start, end) in enumerate(span for span,_,_ in self.slots):
         for j, (sent_start, sent_end) in enumerate(sentence_ranges):
            if sent_start <= start < sent_end and sent_start < end <= sent_end:
               buckets[j] += 1
               break
      return buckets
   @spaces.setter
   def spaces(self, value):
      pass
   @property
   def bits(self):
      return list(map(int, map(lambda x : log2(x + 1), self.spaces)))
   @bits.setter
   def bits(self, bits: int):
      pass
   def encode(self, values:List[int]):
      spaces = self.spaces
      if len(values) > len(spaces):
         raise ValueError("Can't encode")
      for i in range(len(values)):
         # spaces[i] = 0 means that the chunk has a birth defect
         # a typo not by us making the chunk unusable and in that case 
         # values[i] = 0 and the fact that it's an un-fixable typo will
         # tell the decoder to learn it
         if values[i] >= spaces[i] and spaces[i] != 0:
            raise ValueError("Won't fit")
      result = self.text
      for i in range(len(values) - 1, -1, -1):
         result = self.apply(i, values[i], result)
      return result
   @staticmethod
   def decode(text:str,verbose=False,test_self=None) -> Tuple[str,List[int]]:
      original = normalize(text,verbose)
      if test_self is not None:
         if original != test_self.text:
            print(f'original=\n{original}')
            print(f'test_self.text=\n{test_self.text}')
         assert original == test_self.text
      t = Typo(original)

      return original, t._decode(text,test_self)
   def _decode(self, text:str,test=None) -> List[int]:
      a_self = test if test is not None else self
      spaces = a_self.spaces
      cnt = len(diff(text,a_self.text))
      if a_self.verbose:
         print(f'cnt={cnt}')
         print(f'diff(text,a_self.text)={diff(text,a_self.text)}')
      values = [0 for s in spaces]
      for index, space in enumerate(spaces):
         isZero = True
         for i in range(space):
            values[index] = i
            dif = diff(text, a_self.encode(values))
            if len(dif) == cnt - 1:
               if a_self.verbose:
                  print(f'values={values}')
                  print(f'dif={dif}')
               cnt -= 1
               isZero = False
               break 
         if isZero:
            values[index] = 0     
            if a_self.verbose:
               print(f'chunk is empty values={values}')
      return  values
   def encode_encoder(self, bytes_str: str) -> Tuple[List[int], str]:
      if not set(bytes_str) <= set('01'):
         raise ValueError(f"bytes_str isn't a bytes string : '{bytes_str}'")
      values = self.bits
      bit_values = []
      remaining_bits = bytes_str
      for i, val in enumerate(values):
         if len(remaining_bits) >= val + 1 and int(remaining_bits[:val+1]) < self.spaces[i]:
            bit_value = int(remaining_bits[:val+1], 2)
            bit_values.append(bit_value)
            remaining_bits = remaining_bits[val+1:]
         elif len(remaining_bits) >= val and val > 0:
            bit_value = int(remaining_bits[:val], 2)
            bit_values.append(bit_value)
            remaining_bits = remaining_bits[val:]
         else:
            bit_values.append(0)
      return bit_values, remaining_bits
   def learn(self,text:str)->None:
      normalize(text,learn=True,verbose=self.verbose)