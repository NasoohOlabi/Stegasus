#@title imports
# !pin install contextualSpellCheck

import itertools
import json
import math
import os
import re
# Get the path of the script
from dataclasses import dataclass, field
from typing import Callable, Generator, List, Optional, Tuple

import Levenshtein
import nltk
from language_tool_python import LanguageTool
from nltk.tokenize import word_tokenize
from spellchecker import SpellChecker

# nltk.download('punkt')
# nltk.download('perluniprops')



# Initialize the LanguageTool tool
lang_tool = LanguageTool('en-US')
spell_tool = SpellChecker()

# Get the path of the script
script_path = os.path.abspath(__file__)

ROOT_DIR = os.path.dirname(script_path)



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
   
WORD_CORRECTION_RULES = list(map(compile_first , itertools.chain(parseRules('anti.variant'), parseRules('anti.misspelling'))))
FAT_CORRECTION_RULES = list(map(compile_first , parseRules('fat.keyboard')))
KEYBOARD_CORRECTION_RULES = list(map(compile_first , parseRules('anti.keyboard')))
WORD_RULES = list(map(compile_first ,  itertools.chain(parseRules('variant'), parseRules('grammatical'), parseRules('misspelling'))))
KEYBOARD_RULES = list(map(compile_first,  parseRules('keyboard')))


def parse_trigrams(ROOT_DIR=ROOT_DIR):
   d = dict()
   with open(ROOT_DIR + '/statistical-attack/english-trigrams.txt', 'r') as f:
      lines = f.readlines()
      for line in lines:
         sp = line.split(' ')
         if len(sp) > 1:
            d[sp[0]] = int(sp[1][:-1])
   return d

PARSED_TRIGRAMS = parse_trigrams()


class util:
   
   @staticmethod
   def get_words(text: str,verbose=False) -> Tuple[List[str],Callable[[List[str],bool],str]]:
      words = word_tokenize(text)
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
         print(f"detokenize '{text}' -> '{words}' + '{non_words}' -> '{text}'")
         return ''.join(tokens)
      
      return  words ,detokenize
   
   @staticmethod
   def show_diff(a: str, b: str):
      l_a,_ = util.get_words(a)
      l_b,_ = util.get_words(b)
      for i in range(min(len(l_a), len(l_b))):
         if l_a[i] != l_b[i]:
            print(f'i:{i} a:"{l_a[i]}" b:"{l_b[i]}"')
   
   @staticmethod
   def diff(a: str, b: str):
      l_a,_ = util.get_words(a)
      l_b,_ = util.get_words(b)
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
   def keyboard_rules_scan(text: str)->List[Tuple[Tuple[int, int], str, re.Pattern]]:
      matches = []
      rules = KEYBOARD_RULES
      for regex, repl in rules:
         for x in regex.finditer(text):
            matches.append((x.span(), repl, regex))
      matches.sort()
      return matches

   @staticmethod
   def word_rules_scan(text: str)->List[Tuple[Tuple[int, int], str, re.Pattern]]:
      matches = []
      for regex, repl in WORD_RULES:
         x = regex.match(text)
         if x is not None:
            start, end = x.span()
            matches.append(((start, end), repl, regex))
      matches.sort()
      return matches

   @staticmethod
   def rules_scan(text: str)-> List[Tuple[Tuple[int, int], str, re.Pattern]]:
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
   def valid_matches(text:str, slots:List[Tuple[Tuple[int, int], str, re.Pattern]], freq=PARSED_TRIGRAMS, verbose=False):
      text_words, _ = util.get_words(text)
      mutations: List[str] = list(map(lambda x: '', slots))

      # Apply the match to the text and get the resulting strings
      for match_index, match_result in enumerate(slots):
         new_string = util.apply_match_and_validate(text, match_result, mutations, match_index, text_words, verbose)
         norm = util.normalize(new_string,verbose)
         if norm != new_string:
            mutations[match_index] = new_string
         else:
            print(f'rule undetectable "{norm}" != "{text}"')

      # Print the list of matches and their mutations if verbose output is enabled
      if verbose:
         print(list(zip(slots, mutations)))

      # Check for ambiguous and invalid matches
      ambiguous_invalid_matches = util.find_ambiguous_or_invalid_matches(mutations)

      # Create a list of valid matches
      valid_slots = [elem for i, elem in enumerate(slots) if i not in ambiguous_invalid_matches]

      return valid_slots

   @staticmethod
   def apply_match_and_validate(text: str, match_result: Tuple[Tuple[int, int], str, re.Pattern], mutations: List[str], match_index: int, text_words: List[str], verbose: bool) -> str:
      span, repl, regex = match_result
      new_string = util.apply_match(text, match_result, verbose)
      print(f"MatchValidator: validating match {text}->{new_string}")

      # Check if the resulting string has the same number of words as the original text
      words, _ = util.get_words(new_string)
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

   @staticmethod
   def find_ambiguous_or_invalid_matches(mutations: List[str]) -> List[int]:
      ambiguous_invalid_matches = []
      for i, new_string in enumerate(mutations):
         if len(new_string) == 0:
               # If the mutation is an empty string, it is ambiguous or invalid
               ambiguous_invalid_matches.append(i)
         else:
               for j in range(i):
                  if mutations[j] == mutations[i]:
                     # If the mutation is the same as a previous one, it is ambiguous
                     ambiguous_invalid_matches.append(i)
                     break

      return ambiguous_invalid_matches



   @staticmethod
   def valid_rules_scan(text:str,verbose=False):
      proposed_slots = util.rules_scan(text)
      print('proposed_slots: ',proposed_slots)
      try:
         valid_slots = util.valid_matches(text,proposed_slots,verbose=verbose)
         print('valid_slots: ',valid_slots)
         return valid_slots
      except ValueError:
         return []
      
   @staticmethod
   def chunker(text:str,span_size = 6):
      # Iterate over the spans in the sentence
      words,_ = util.get_words(text)
      chunks = []
      cur_word = 0
      last_sep = 0
      i = 0
      while i < len(text):
         if text[i:i+len(words[cur_word])] == words[cur_word]:
            if cur_word % span_size == 0 and cur_word != 0:
               chunks.append((last_sep,i))
               last_sep = i
            i = i + len(words[cur_word]) - 1
            cur_word+=1
         
         i += 1
      if last_sep < len(text):
         chunks.append((last_sep, len(text)))
      return chunks

   @staticmethod
   def word_we_misspelled(word,spelling):
      if util.string_mutation_distance(spelling,word) == 1 \
         and spelling[0].lower() == word[0].lower() \
         and spelling[-1].lower() == word[-1].lower():

         for regex,repl in FAT_CORRECTION_RULES:
            if regex.sub(repl,word) == spelling:
               return spelling
         return word
      else:
         return word # speller is wrong since input is ai generated and the only source for bad spelling is us and it's probably a name of sth
   @staticmethod
   def spell_word(word:str) -> str:
      spellingOpt = spell_tool.correction(word)
      spelling = spellingOpt if spellingOpt is not None else word
      return spelling if util.word_we_misspelled(word,spelling) else word 

   @staticmethod
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

      temp = lang_tool.correct(text)
      if verbose and text != temp:
         print(f'lang_tool.correct "{text}" -> "{temp}"')
      text = temp 

      words, get_sentence  = util.get_words(text)
      spelled_words = [util.spell_word(w) for w in words]

      spelled_text = get_sentence(spelled_words,verbose)

      if verbose:
         print(f"util.normalize('{original_text}') => '{spelled_text}'")
      return spelled_text
   
   @staticmethod
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
      if self.text != util.normalize(self.text,self.verbose):
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
      if self._spaces is not None:
         return self._spaces
      
      sentence_ranges = util.chunker(self.text)
      
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
      return list(map(int, map(lambda x : math.log2(x + 1), self.spaces)))

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






# # Test case 1: Correct simple grammar error
# # Define the input sentence
# s1 = "Your the best"

# # Use LanguageTool to correct grammar errors
# s2 = tool.correct(s1)

# # Check that the output is correct
# print('s1,s2')
# util.show_diff(s2, "You're the best")

# # Test case 2: Handle correct input sentence
# # Define the input sentence
# s3 = "You're the best"

# # Use LanguageTool to correct grammar errors
# print('s3,s4')
# s4 = tool.correct(s3)

# # Check that the output is correct
# util.show_diff(s4, "You're the best")

# # Example 1: Correct a complex sentence
# # Define the input sentence
# s5 = "The dog chased it's tail, but its too short."

# # Use LanguageTool to correct grammar errors
# s6 = tool.correct(s5)

# # Print the corrected sentence
# print('s5,s6')
# util.show_diff(s5,s6)
# print(s6)
# # Expected output: "The dog chased its tail, but it's too short."

# # Example 2: Handle correct input sentence
# # Define the input sentence
# s7 = "The quick brown fox jumped over the lazy dog."

# # Use LanguageTool to correct grammar errors
# s8 = tool.correct(s7)
# print('s7,s8')
# util.show_diff(s7,s8)

# # Print the corrected sentence
# print(s8)
# Expected output: "The quick brown fox jumped over the lazy dog."



t = Typo('Hi, How are you?',verbose=True)

t.slots