import os
# Get the path of the script
from dataclasses import dataclass, field
from itertools import chain
from math import log2
from statistics import mode
from typing import Callable, Generator, List, Optional, Tuple

import Levenshtein
import regex as re
from icecream import ic
from language_tool_python import LanguageTool

from .StringSpans import StringSpans
from .UDict import add_word, check_word

# Initialize the LanguageTool tool
lang_tool = LanguageTool('en-US', config={ 'cacheSize': 1000, 'pipelineCaching': True })

# Get the path of the script
script_path = os.path.abspath(__file__)

ROOT_DIR = os.path.dirname(script_path)

def parseRules(name, ROOT_DIR=ROOT_DIR+'/rules') -> Generator[Tuple[str, str], None, None]:
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
KEYBOARD_CORRECTION_RULES = list(map(compile_first , parseRules('anti.keyboard')))
FAT_CORRECTION_RULES = list(map(compile_first , parseRules('fat.keyboard')))
WORD_RULES = list(map(compile_first ,  chain(parseRules('variant'), parseRules('grammatical'), parseRules('misspelling'))))
KEYBOARD_RULES = list(map(compile_first,  parseRules('keyboard')))


def count_uppercase_letters(s: str) -> int:
   count = 0
   for char in s:
      if ord(char) < 97 or ord(char) > 122:
         count += 1
   return count
def normal_word(word:str)->bool:
   return lang_tool.correct(word) == word or check_word(word)
def string_mutation_distance(str1: str, str2: str) -> int:
   """Returns the number of mutations required to transform str1 into str2"""
   return Levenshtein.distance(str1, str2)
def show_diff(a: str, b: str):
   l_a = StringSpans(a).get_words()
   l_b = StringSpans(b).get_words()
   for i in range(min(len(l_a), len(l_b))):
      if l_a[i] != l_b[i]:
         print(f'i:{i} a:"{l_a[i]}" b:"{l_b[i]}"')
def diff(a: str, b: str) -> List[Tuple[str,str]]:
   l_a = StringSpans(a).get_words()
   l_b = StringSpans(b).get_words()
   return [(l_a[i], l_b[i]) for i in range(min(len(l_a), len(l_b)))
      if l_a[i] != l_b[i]]
def apply_match(text:str, match_result: Tuple[Tuple[int,int],str,re.Pattern], verbose: bool = False) -> str:
   span, repl, regex = match_result
   if verbose:
      print(f"Before replace: {text}")
   replaced_text = regex.sub(repl, text[span[0]:span[1]])
   after_replace_text = text[:span[0]] + replaced_text + text[span[1]:]
   if verbose:
      print(f"After replace: {after_replace_text}")
   return after_replace_text
def keyboard_rules_scan(text: str)->List[Tuple[Tuple[int, int], str, re.Pattern]]:
   matches = []
   rules = KEYBOARD_RULES
   for regex, repl in rules:
     for x in regex.finditer(text,overlapped=True):
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
def expand_span_to_word(words:List[Tuple[int,int]],span:Tuple[int,int])->Tuple[Tuple[int,int],Tuple[int,int],int]:
   ss, se = span
   for i, (start,end) in enumerate(words):
      if start <= ss and se <= end:
         return (start,end),(ss-start,se-start),i
   for i, (start,end) in enumerate(words):
      if start > ss and se <= end:
         return (start,end),(start,se-start),i
      elif start <= ss and se > end:
         return (start,end),(ss-start,end-start),i
   
   raise ValueError(f'sth is wrong {words} {span}')
def valid_matches(text:str, slots:List[Tuple[Tuple[int, int], str, re.Pattern]], verbose=False):
   texas = StringSpans(text)
   mutations: List[str] = list(map(lambda x: '', slots))

   # Apply the match to the text and get the resulting strings
   for match_index, match_result in enumerate(slots):
      span, repl, regex = match_result
      ex_span,relative_span,ex_span_index = expand_span_to_word(texas.words,span)
      old_word = texas.get(ex_span)
      new_word = apply_match(old_word,(relative_span,repl,regex),verbose)
      new_word_corrections = corrections(new_word,verbose=verbose)
      if len(new_word_corrections) > 0:
         new_word_corrections_mode = mode(new_word_corrections)
      else:
         if verbose:
            print(f'new_word: {new_word} can\'t be fixed')
         new_word_corrections_mode = ''
      if normal_word(old_word) \
            and not normal_word(new_word) \
            and new_word[0].lower() == old_word[0].lower() \
            and new_word[-1].lower() == old_word[-1].lower() \
            and new_word_corrections_mode == old_word:
         mutations[match_index] = texas.replace_word(ex_span_index,new_word)
      else:
         if verbose:
            print(f'rule undetectable or modify looks! new word "{new_word}" != "{old_word}" original and will be corrected to {new_word_corrections_mode} from {new_word_corrections}')



   # Check for ambiguous and invalid matches
   ambiguous_invalid_matches = [i for i, new_string in enumerate(mutations)
         if not new_string or new_string in mutations[:i] or normalize(new_string,verbose=verbose) != text]

   # Create a list of valid matches
   valid_slots = [elem for i, elem in enumerate(slots) if i not in ambiguous_invalid_matches]
   
   # Print the list of matches and their mutations if verbose output is enabled
   if verbose:
      print('\n'+('%'*20)+'valid slots!'+('%'*20))
      for v in list(zip(slots, mutations)):
         print(v)

   return valid_slots
def valid_rules_scan(text:str,verbose=False):
   proposed_slots = rules_scan(text)
   if verbose:
      print('proposed_slots: ',proposed_slots)
   valid_slots = valid_matches(text,proposed_slots,verbose=verbose)
   if verbose:
      print('valid_slots: ')
      for s in valid_slots:
         print(s)
   return valid_slots
def chunker(text:str,span_size = 6) -> List[Tuple[int,int]]:
   words = StringSpans(text).words
   if len(words) < span_size:
      return [(0,len(text))]
   chunks = []
   last_start = 0
   for i in range(span_size-1,len(words),span_size):
      chunks.append((last_start,words[i][1]))
      if i+1<len(words):
         last_start = words[i+1][0] 

   # last word ends with last word
   chunks[-1] = (chunks[-1][0], words[-1][1])
   return chunks
def word_we_misspelled(word:str,spelling:str,verbose=False):
   uls = count_uppercase_letters(word)
   if string_mutation_distance(spelling,word) == 1 \
     and spelling[0].lower() == word[0].lower() \
     and spelling[-1].lower() == word[-1].lower() \
     and uls == 2 \
     and uls < len(word):

     for regex,repl in FAT_CORRECTION_RULES:
       if regex.sub(repl,word) != spelling:
         if verbose:
            print(f"FAT_CORRECTION_RULES ({regex}) ({repl}): {regex.sub(repl,word)} == {spelling}")
         return True
     return False
   else:
     return False # speller is wrong since input is ai generated and the only source for bad spelling is us and it's probably a name of sth
def spell_word(word:str,verbose=False) -> str:
   if normal_word(word):
      return word
   spellingOpt = lang_tool.check(word)[0].replacements[0]
   spelling = spellingOpt if spellingOpt is not None else word
   return spelling if word_we_misspelled(word,spelling,verbose) else word 
def correction_rules_subset(text:str):
   return [rule for rule in lang_tool.check(text) if rule.category in ['TYPOS','SPELLING','GRAMMAR','TYPOGRAPHY']]
def normalize(text:str,verbose=False,learn=False):
   chunks: List[Tuple[int,int]] = chunker(text) # size = chunks
   to_be_original = text
   offsets: List[int]= [x.offset for x in correction_rules_subset(text)] # size = offsets
   empty_chunks = [False for _ in chunks] # size = chunks
   text_sss = StringSpans(text)
   affected_words = [text[s:e] for s,e in text_sss.words if s in offsets] # size = offsets
   if verbose:
      print(f'text={text}')
      print(f'chunks={chunks}')
      print(f'offsets={offsets}')
   offsets_chunks = [
      [(o,affected_words[i],corrections(affected_words[i])) for i,o in enumerate(offsets) if chunk_start <= o < chunk_end]
      for chunk_start,chunk_end in chunks] # size = chunks
   if verbose:
      print(f'chunks_offsets={offsets_chunks}')
   for i, offsets_chunk in enumerate(offsets_chunks):
      if len(offsets_chunk) > 1:
         if verbose:
            print(f'len({offsets_chunk})={len(offsets_chunk)} > 1')
         empty_chunks[i] = True
         if learn:
            for o,w,cs in offsets_chunk:
               add_word(w)
      elif len(offsets_chunk) == 1 and len(offsets_chunk[0][2]) == 0:
         if verbose:
            print(f'no suggestions for {offsets_chunk[0][1]} added to dict')
         empty_chunks[i] = True
         if learn:
            add_word(offsets_chunk[0][1])
      elif len(offsets_chunk) == 1:
         cs = offsets_chunk[0][2]
         if verbose:
            print(f'typo={offsets_chunk[0][1]}\nsuggestion={mode(cs)}')
            print(f'votes={cs}')
         to_be_original = to_be_original.replace(offsets_chunk[0][1],mode(cs))
      else:
         empty_chunks[i] = True
   
   return to_be_original
def corrections (typo,verbose=False):
   suggestion = spell_word(typo)
   votes = [suggestion] if string_mutation_distance(suggestion,typo) == 1 and normal_word(suggestion) else []
   for regex,repl in FAT_CORRECTION_RULES:
      matches = ((x.span(), repl, regex) for x in regex.finditer(typo,overlapped=True))
      for match in matches:
         votes.append(apply_match(typo,match))
         
   for regex,repl in WORD_CORRECTION_RULES:
      if regex.match(typo) is not None:
         votes.append(regex.sub(repl,typo))

   for regex,repl in KEYBOARD_CORRECTION_RULES:
      matches = ((x.span(), repl, regex) for x in regex.finditer(typo,overlapped=True))
      for match in matches:
         votes.append(apply_match(typo,match))
         
   if verbose:
      print(f'unfiltered votes {votes}')
   votes = [v for v in votes if  normal_word(v)]
   if verbose:
      print(f'filtered votes {votes}')
   return votes