import nltk
import spacy
from typing import List, Tuple, Optional
from dataclasses import dataclass, field
from torch import Tensor
from typing import List, Tuple

def create_mask(a: List[Tuple[int, int]], b: List[Tuple[int, int]]) -> List[bool]:
    """
    Creates a mask over `a` such that the `a[i]` range is contained in any `b[j]` range.
    Only keeps the last `True` if a consecutive `True` occurs.
    """
    mask = []
    j = 0
    for i in range(len(a)):
        while j < len(b) and b[j][1] < a[i][0]:
            j += 1
        mask.append(j < len(b) and b[j][0] <= a[i][0] and b[j][1] >= a[i][1])
        
    for i in range(1, len(mask)):
        if mask[i] and mask[i-1]:
            mask[i-1] = False
    return mask

@dataclass
class SemanticPositions:
    string : str = field(init=True,repr=True)
    NVA_words : List[Tuple[int,int]] = field(init=True,repr=True)
    tokens : Optional[Tensor] = field(init=True,repr=True)
    mask : Optional[List[bool]] = field(init=True,repr=True)

def MaskGen(text:str,tokenizer=None):
  """Extract the start and end positions of verbs, nouns, and adjectives in the given text."""
  # Load the spaCy English model
  nlp = spacy.load('en_core_web_sm')
  
  # Parse the text with spaCy
  doc = nlp(text)
  
  # Create a dictionary to store the start and end positions of each POS tag
  # pos_dict = {
  #   'VERB': [],
  #   'NOUN': [],
  #   'ADJ': []
  # }
  pos_list: List[Tuple[int,int]] = []
  
  # Loop through each token in the parsed text
  for token in doc:
    if token.pos_ in ['VERB','NOUN','ADJ']:
      # If the token's POS tag is a verb, noun, or adjective, add its start and end positions to the dictionary
      # pos_dict[token.pos_]
      pos_list.append((token.idx, token.idx + len(token)))

  pos_list.sort()

  if tokenizer is not None:
    # tokenize the input string
    tokens = tokenizer.tokenize(text)

    start_index = 0
    token_mask = [False for _ in tokens]
    token_spans = []
    last_span = 0
    for token in tokens:
        token_start_index = text.find(token, start_index)
        token_end_index = token_start_index + len(token)
        span = (token_start_index, token_end_index)
        token_spans.append(span)
        start_index = token_end_index
    
    m = create_mask(token_spans,pos_list)
    return SemanticPositions(string=text,
                             NVA_words=pos_list,
                             tokens=tokens,
                             mask=m)

  return SemanticPositions(string=text,
                             NVA_words=pos_list,
                             tokens=None,
                             mask=None)




