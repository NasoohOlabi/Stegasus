import os
import re

# Get the path of the script
script_path = os.path.abspath(__file__)

ROOT_DIR = os.path.dirname(script_path)



#@title parseRules
def parseRules(name,ROOT_DIR=ROOT_DIR):
   with open(ROOT_DIR + f'/{name}.rules','r') as f:
      lines = f.readlines()
      cnt = -1
      results = []
      for line in lines:
         cnt+=1
         line = line[:-1].strip()
         if len(line) == 0:
            continue
         line = line.split('\t')
         if len(line) > 1:
            results.append((line[0],line[1]))
   return results

WORD_RULES = parseRules('variant') + parseRules('grammatical') + parseRules('misspelling')
SAFE_KEYBOARD_RULES = parseRules('keyboard.safer')
KEYBOARD_RULES = parseRules('keyboard')
WORD_RULES = list(map(lambda x: (re.compile(x[0]),x[1]), WORD_RULES))
KEYBOARD_RULES = list(map(lambda x: (re.compile(x[0]),x[1]), KEYBOARD_RULES))
SAFE_KEYBOARD_RULES = list(map(lambda x: (re.compile(x[0]),x[1]), SAFE_KEYBOARD_RULES))

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


__all__ = [
	'WORD_RULES'
	,'KEYBOARD_RULES'
	,'KEYBOARD_RULES'
	,'SAFE_KEYBOARD_RULES'
   ,'PARSED_TRIGRAMS'
]