#@title imports
# !pin install contextualSpellCheck

import json
import math
import re

import nltk
from nltk.tokenize import word_tokenize

from .common import *  # pylint: disable=import-error

nltk.download('punkt')

from dataclasses import dataclass, field
from typing import List, Tuple

import contextualSpellCheck
import spacy

SPELL_CHECKER = spacy.load('en_core_web_sm')
contextualSpellCheck.add_to_pipe(SPELL_CHECKER)
import os

# Get the path of the script
script_path = os.path.abspath(__file__)

# Construct the path to the file relative to the package
ROOT_DIR = os.path.dirname(script_path)


class util:
   
   @staticmethod
   def get_words(t: str) -> List[str]:
      return word_tokenize(t.strip())

   @staticmethod
   def show_diff(a: str, b: str):
      l_a = util.get_words(a)
      l_b = util.get_words(b)
      for i in range(min(len(l_a), len(l_b))):
         if l_a[i] != l_b[i]:
            print(f'i:{i} a:"{l_a[i]}" b:"{l_b[i]}"')
   
   @staticmethod
   def diff(a: str, b: str):
      l_a = util.get_words(a)
      l_b = util.get_words(b)
      acc = []
      for i in range(min(len(l_a), len(l_b))):
         if l_a[i] != l_b[i]:
            acc.append((l_a[i], l_b[i]))
      return acc
   
   @staticmethod
   def apply_match(text:str, match_result: Tuple[Tuple[int,int],str,re.Pattern], verbose: bool = False) -> str:
      span, repl, regex = match_result
      if verbose:
         print(f"Before replace: {text}")
      replaced_text = regex.sub(repl, text[span[0]:span[1]])
      if verbose:
         print(f"After replace: {replaced_text}")
      return text[:span[0]] + replaced_text + text[span[1]:]


   @staticmethod
   def keyboard_rules_scan(text: str, safe=False):
      matches = []
      rules = SAFE_KEYBOARD_RULES if safe else KEYBOARD_RULES
      for regex, repl in rules:
         for x in regex.finditer(text):
            matches.append((x.span(), repl, regex))
      matches.sort()
      return matches


   @staticmethod
   def word_rules_scan(text: str):
      text_words = util.get_words(text)
      matches = []
      for i, word in enumerate(text_words):
         for regex, repl in WORD_RULES:
            x = regex.match(word)
            if x is not None:
               start, end = x.span()
               start += sum(map(len, text_words[0:i]))
               end += sum(map(len, text_words[0:i]))
               matches.append(((start, end), repl, regex))
      matches.sort()
      return matches

   @staticmethod
   def rules_scan(text: str):
      result = util.word_rules_scan(text) + util.keyboard_rules_scan(text)
      result.sort()
      return result

   @staticmethod
   def Trigram(text:str):
      l = list(text)
      result = []
      for i in range(len(l)-2):
         result.append(''.join(l[i:i+3]))
      return result

   @staticmethod
   def MatchValidator(text:str,freq=PARSED_TRIGRAMS, verbose=False):
      uText = text.upper()
      uText_words = util.get_words(uText.lower())
      valid_regex = re.compile('[A-Z][A-Z][A-Z]')
      def helper(match_result):
         span,repl,regex = match_result
         newString = uText[span[0]-1] + regex.sub(repl,uText[span[0]:span[1]]) + (uText[span[1]] if span[1] < len(uText) else '')
         tri = filter(lambda x : valid_regex.match(x) is not   None ,util.Trigram(newString))
         for t in tri:
            if freq[t] < 10000:
               if verbose:
                  print(f"MatchValidator: trigram {t} appears less than 10000 times in corpus")
               return False
         newString = util.apply_match(text,  match_result,verbose).lower()
         words = util.get_words(newString)
         if len(words) != len(uText_words):
            if verbose:
               print(f"MatchValidator: length of words in transformed string ({len(words)}) does not match original string ({len(uText_words)})")
            return False
         
         for ow,nw in zip(uText_words,words):
            if ow[0] != nw[0] or ow[-1] != nw[-1]:
               if verbose:
                  print(f"MatchValidator: first and/or last character of word in transformed string ({nw}) does not match original string ({ow})")
               return False
         return True
      return helper

   @staticmethod
   def valid_rules_scan(text:str,verbose=False):
      pred = util.MatchValidator(text,verbose)
      return list(filter(pred,util.rules_scan(text)))
   @staticmethod
   def spellcheck(text:str,verbose=False):
      doc = SPELL_CHECKER(text)
      if verbose:
         print(f"util.spellcheck('{text}') = '{json.dumps(doc)}'")
      return doc._.outcome_spellCheck


@dataclass
class Typo:
   """Class for Typo Engine."""

   text: str = field(repr=False)
   _length: int = field(init=False, repr=False)
   _slots: List[Tuple[Tuple[int, int], str, re.Pattern]]|None = field(init=True, repr=False,default=None)
   verbose: bool = False

   def spell_check(self):
      return util.spellcheck(self.text)

   def __post_init__(self):
      if self.text != util.spellcheck(self.text):
         raise ValueError("Text isn't spelled correctly")

   def apply(self, space: int, offset: int, text: str) -> str:
      if self.verbose:
         print(f"apply: space={space}, offset={offset}, text={text}")
      if offset == 0:
         return text
      match_tuple = self.slots[sum(self.spaces[0:space]) + offset - 1]
      applied = util.apply_match(text, match_tuple,self.verbose)
      if self.verbose:
         print(f"applied: {applied}")
      return applied
   
   @property
   def slots(self):
      if self._slots is None:
         self._slots = util.valid_rules_scan(self.text,self.verbose)
      return self._slots

   @property
   def length(self) -> int:
      return len(self.slots)

   @length.setter
   def length(self, length: int):
      pass

   @property
   def spaces(self) -> List[int]:
      index_length = self.length
      s1 = index_length
      answer = []
      while s1 > 0 and index_length > 0:
         s1 = 2 ** math.floor(math.log2(index_length))
         index_length -= s1
         answer.append(s1)
      return answer

   @spaces.setter
   def spaces(self, value):
      pass

   @property
   def bits(self):
      return list(map(int, map(math.log2, self.spaces)))

   @bits.setter
   def bits(self, bits: int):
      pass

   def encode(self, values):
      spaces = self.spaces
      if len(values) > len(spaces):
         raise ValueError("Can't encode")
      for i in range(len(values)):
         if values[i] >= spaces[i]:
            raise ValueError("Won't fit")
      result = self.text
      for i in range(len(values) - 1, -1, -1):
         result = self.apply(i, values[i], result)
      return result

   def decode(self, text):
      spaces = self.spaces
      differences = len(util.diff(text, self.text))
      if differences > len(spaces):
         raise ValueError("Can't encode")
      values = list(map(lambda x: 0, spaces))
      for i in range(len(spaces)):
         for j in range(spaces[i] + 1):
            if len(util.diff(text, self.apply(i, j, self.text))) < differences:
               values[i] = j
               break
      return values

   def encode_encoder(self, bytes_str: str) -> Tuple[List[int], str]:
      if not set(bytes_str) <= set('01'):
         raise ValueError(f"bytes_str isn't a bytes string : '{bytes_str}'")
      values = self.bits
      bit_values = []
      remaining_bits = bytes_str
      for val in values:
         if len(remaining_bits) >= val and len(remaining_bits[:val]) > 0:
            bit_value = int(remaining_bits[:val], 2)
            bit_values.append(bit_value)
            remaining_bits = remaining_bits[val:]
         else:
            bit_values.append(0)
      return bit_values, remaining_bits
