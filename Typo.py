
import os
import re
# Get the path of the script
from dataclasses import dataclass, field
from itertools import chain
from math import log2
from typing import Callable, Generator, List, Optional, Tuple

import Levenshtein
from language_tool_python import LanguageTool
from spellchecker import SpellChecker

# Initialize the LanguageTool tool
lang_tool = LanguageTool('en-US')
spell_tool = SpellChecker()

# Get the path of the script
# script_path = '.'
script_path = os.path.abspath(__file__)

ROOT_DIR = os.path.dirname(script_path)
# ROOT_DIR = '.'


#@title parseRules
def parseRules(name, ROOT_DIR=ROOT_DIR) -> Generator[Tuple[str, str], None, None]:
   with open(ROOT_DIR + f'/{name}.tsv', 'r') as f:
      for line in f:
            line = line.strip()
            if len(line) == 0:
               continue
            line = line.split('\t')
            if len(line) > 1:
               yield (line[0], line[1])

def compile_first(x:Tuple[str,str])->Tuple[re.Pattern[str],str]:
   try:
      return (re.compile(x[0]),x[1])
   except:
      print(x)
      raise ValueError(f'compilable {x}')
   
WORD_CORRECTION_RULES = list(map(compile_first , chain(parseRules('anti.variant'), parseRules('anti.misspelling'))))
FAT_CORRECTION_RULES = list(map(compile_first , parseRules('fat.keyboard')))
KEYBOARD_CORRECTION_RULES = list(map(compile_first , parseRules('anti.keyboard')))
WORD_RULES = list(map(compile_first ,  chain(parseRules('variant'), parseRules('grammatical'), parseRules('misspelling'))))
KEYBOARD_RULES = list(map(compile_first,  parseRules('keyboard')))


def get_words(text: str,verbose=False) -> Tuple[List[str],Callable[[List[str],bool],str]]:
   # words = word_tokenize(text)
   words = list(spell_tool.split_words(text))
   spans = []
   first_word_hit = text.find(words[0])
   spans.append((0,first_word_hit))
   last_hit_end = first_word_hit + len(words[0])
   for w in words[1:]:
      hit_end = text.find(w,last_hit_end) 
      spans.append((last_hit_end,hit_end))
      last_hit_end = hit_end + len(w)
   spans.append((last_hit_end,len(text)))
   non_words = list(map(lambda x: text[x[0]:x[1]], spans))

   def detokenize(words:List[str],verbose=verbose) -> str:
      ## combine words with non_words into a single string
      tokens = [non_words[0]]
      for i in range(len(words)):
         tokens.append(words[i])
         tokens.append(non_words[i+1])
      if verbose:
         print(f"detokenize \n'{text}' \n-> \n'{words}' + \n'{non_words}' \n-> \n'{text}'")
      return ''.join(tokens)
   
   return  words ,detokenize
def show_diff(a: str, b: str):
   l_a,_ = get_words(a)
   l_b,_ = get_words(b)
   for i in range(min(len(l_a), len(l_b))):
      if l_a[i] != l_b[i]:
         print(f'i:{i} a:"{l_a[i]}" b:"{l_b[i]}"')
def diff(a: str, b: str):
   l_a,_ = get_words(a)
   l_b,_ = get_words(b)
   acc = []
   for i in range(min(len(l_a), len(l_b))):
      if l_a[i] != l_b[i]:
         acc.append((l_a[i], l_b[i]))
   return acc
def apply_match(text:str, match_result: Tuple[Tuple[int,int],str,re.Pattern], verbose: bool = False) -> str:
   span, repl, regex = match_result
   if verbose:
      print(f"Before replace: {text}")
   replaced_text = regex.sub(repl, text[span[0]:span[1]])
   if verbose:
      print(f"After replace: {replaced_text}")
   return text[:span[0]] + replaced_text + text[span[1]:]
def keyboard_rules_scan(text: str)->List[Tuple[Tuple[int, int], str, re.Pattern]]:
   matches = []
   rules = KEYBOARD_RULES
   for regex, repl in rules:
      for x in regex.finditer(text):
         matches.append((x.span(), repl, regex))
   return matches
def word_rules_scan(text: str)->List[Tuple[Tuple[int, int], str, re.Pattern]]:
   matches = []
   for regex, repl in WORD_RULES:
      x = regex.match(text)
      if x is not None:
         start, end = x.span()
         matches.append(((start, end), repl, regex))
   return matches
def rules_scan(text: str)-> List[Tuple[Tuple[int, int], str, re.Pattern]]:
   result = word_rules_scan(text) + keyboard_rules_scan(text)
   result.sort()
   return result
def valid_matches(text:str, slots:List[Tuple[Tuple[int, int], str, re.Pattern]], verbose=False):
   text_words, _ = get_words(text)
   mutations: List[str] = list(map(lambda x: '', slots))

   # Apply the match to the text and get the resulting strings
   for match_index, match_result in enumerate(slots):
      new_string = apply_match_and_validate(text, match_result, mutations, match_index, text_words, verbose)
      norm = normalize(new_string,verbose)
      if norm != new_string:
         mutations[match_index] = new_string
      else:
         print(f'rule undetectable "{norm}" != "{text}"')

   # Print the list of matches and their mutations if verbose output is enabled
   if verbose:
      print(list(zip(slots, mutations)))

   # Check for ambiguous and invalid matches
   ambiguous_invalid_matches = find_ambiguous_or_invalid_matches(mutations)

   # Create a list of valid matches
   valid_slots = [elem for i, elem in enumerate(slots) if i not in ambiguous_invalid_matches]

   return valid_slots
def apply_match_and_validate(text: str, match_result: Tuple[Tuple[int, int], str, re.Pattern], mutations: List[str], match_index: int, text_words: List[str], verbose: bool) -> str:
   new_string = apply_match(text, match_result, verbose)
   if verbose:
      print(f"MatchValidator: validating match {text} -> {new_string}")

   # Check if the resulting string has the same number of words as the original text
   words, _ = get_words(new_string)
   if len(words) != len(text_words):
      if verbose:
            print(f"MatchValidator: length of words in transformed string ({len(words)}) does not match original string ({len(text_words)})")
      # Set the mutation to an empty string if it is not valid
      mutations[match_index] = ''
   else:
      # Check if the first and last character of each modified word is the same as the original word
      for ow, nw in zip(text_words, words):
            ow = ow.lower()
            nw = nw.lower()
            if ow[0] != nw[0] or ow[-1] != nw[-1]:
               if verbose:
                  print(f"MatchValidator: first and/or last character of word in transformed string ({nw}) does not match original string ({ow})")
               # Set the mutation to an empty string if it is not valid
               mutations[match_index] = ''
               break

   return new_string
def find_ambiguous_or_invalid_matches(mutations: List[str]) -> List[int]:
    return [i for i, new_string in enumerate(mutations, start=1)
            if not new_string or new_string in mutations[:i-1]]
def valid_rules_scan(text:str,verbose=False):
   proposed_slots = rules_scan(text)
   if verbose:
      print('proposed_slots: ',proposed_slots)
   valid_slots = valid_matches(text,proposed_slots,verbose=verbose)
   if verbose:
      print('valid_slots: ',valid_slots)
   return valid_slots
def chunker(text:str,span_size = 6):
   words,_ = get_words(text)
   chunks = []
   cur_word = 0
   last_sep = 0
   i = 0
   while i < len(text) and cur_word < len(words):
      if text[i:i + len(words[cur_word])] == words[cur_word]:
            if cur_word % span_size == 0 and cur_word != 0:
               chunks.append((last_sep,i))
               last_sep = i
            i = i + len(words[cur_word]) - 1
            cur_word+=1
         
      i += 1
   if last_sep < len(text):
      chunks.append((last_sep, len(text)))
   return chunks
def word_we_misspelled(word:str,spelling:str,verbose=False):
   if string_mutation_distance(spelling,word) == 1 \
      and spelling[0].lower() == word[0].lower() \
      and spelling[-1].lower() == word[-1].lower():

      for regex,repl in FAT_CORRECTION_RULES:
         if regex.sub(repl,word) != spelling:
            if verbose:
               print(f"FAT_CORRECTION_RULES ({regex}) ({repl}): {regex.sub(repl,word)} == {spelling}")
            return True
      return False
   else:
      return False # speller is wrong since input is ai generated and the only source for bad spelling is us and it's probably a name of sth
def spell_word(word:str,verbose=False) -> str:
   spellingOpt = spell_tool.correction(word)
   spelling = spellingOpt if spellingOpt is not None else word
   return spelling if word_we_misspelled(word,spelling,verbose) else word 
def normalize(original_text:str,verbose=False):
   text = original_text
   temp = text
   for regex,repl in WORD_CORRECTION_RULES:
      temp =  regex.sub(repl, text)
      if verbose and text != temp:
         print(f'WORD_CORRECTION_RULES rule:{(regex,repl)} "{text}" -> "{temp}"')
      text = temp 

   for regex,repl in KEYBOARD_CORRECTION_RULES:
      temp =  regex.sub(repl, text)
      if verbose and text != temp:
         print(f'KEYBOARD_CORRECTION_RULES rule:{(regex,repl)} "{text}" -> "{temp}"')
      text = temp 

   dot_split_sentences = text.split('.')
   temp = '.'.join([lang_tool.correct(sentence) for sentence in dot_split_sentences])
   if verbose and text != temp:
      print(f'lang_tool.correct \n"{text}" \n-> \n"{temp}"')
   text = temp 

   words, get_sentence  = get_words(text)
   spelled_words = [spell_word(w,verbose) for w in words]
   if verbose:
      for i in range(len(words)):
         if words[i] != spelled_words[i]:
            print(f"normalize speller: '{words[i]}' -> '{spelled_words[i]}'")

   spelled_text = get_sentence(spelled_words,verbose)

   if verbose:
      print(f"normalize('{original_text}') => '{spelled_text}'")
      print(('='*10)+'diff'+('='*10))
      show_diff(original_text,spelled_text)
      print('='*20)
   return spelled_text
def string_mutation_distance(str1: str, str2: str) -> int:
   """Returns the number of mutations required to transform str1 into str2"""
   return Levenshtein.distance(str1, str2)


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
         if values[i] >= spaces[i]:
            raise ValueError("Won't fit")
      result = self.text
      for i in range(len(values) - 1, -1, -1):
         result = self.apply(i, values[i], result)
      return result


   def decode(self,text:str):
      spaces = self.spaces
      differences = len(diff(text, self.text))
      if differences > len(spaces):
         raise ValueError("Can't encode")
      values = list(map(lambda x: 0, spaces))
      for i in range(len(spaces)):
         for j in range(spaces[i] + 1):
            if len(diff(text, self.apply(i, j, self.text))) < differences:
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


def testTypoCarrier(text,verbose=False):
   t = Typo(text,verbose=verbose)

   spaces = t.spaces

   print(f"t.spaces = {spaces}")
   print(f"t.bits = {t.bits}")
   print(f"max={max(spaces)}")
   print(f"len={len(spaces)}")
   
   g = (list(map(lambda x: i % x ,spaces)) for i in range(max(spaces))) 

   for v in g:
      print(f'{v}',end='')
      x =t.decode(t.encode(v))
      if not x == v:
         print(f'\nt.decode(t.encode(v)):{x}')
         print(f't.text:{v}')
      else:
         print(" passed!")
   return t