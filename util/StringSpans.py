from typing import Callable, Generator, List, Tuple, Type

import regex as re


class StringSpans:
   string:str
   def __init__(self, string = None):
      if isinstance(string,str):
         self.string = string
         self._set_spans(string)
   
   @staticmethod
   def _get_words(text: str,verbose=False) -> Tuple[List[Tuple[int,int]],List[Tuple[int,int]],List[Tuple[int,int]],List[Tuple[int,int]]]:
      word_regex = re.compile(r'[a-zA-Z\'\-]+')
      space_regex = re.compile(r'\s')
      spans = []
      words = []
      spaces = []
      for match in re.finditer(word_regex, text):
         spans.append(match.span())
         words.append(match.span())
      for match in re.finditer(space_regex, text):
         spans.append(match.span())
         spaces.append(match.span())
      spans.sort()
      result = []
      last = 0
      for i in range(len(spans)):
         start, end = spans[i]
         if start != last:
               result.append((last,start))
         result.append((start,end))
         last = end
      if last != len(text):
         result.append((last,len(text)))     
      non_words = [
         (start,end) for start,end in result 
         if (start,end) not in words and space_regex.match(text[start:end]) is None
         ]
      non_spaces = [
         (start,end) for start,end in result 
         if (start,end) not in spaces
         ]
         
      return result, words, non_words, non_spaces
   
   def _set_spans(self, string:str):
      spans, words,non_words, non_spaces = StringSpans._get_words(string)
      self.words = words
      self.spans = spans
      self.non_words = non_words
      self.non_spaces = non_spaces

   def replace_word(self, word_index: int, replacement: str) -> str:
      # Check if the word_index is valid
      if not (0 <= word_index < len(self.words)):
         raise ValueError(f"Invalid word index: {word_index}")
      
      # Get the start and end indices of the word span at the given word_index
      start, end = self.words[word_index]
      
      # Replace the word span with the replacement string
      new_string = self.string[:start] + replacement + self.string[end:]
      
      return new_string
   def get_word(self, word_index: int) -> str:
      # Check if the word_index is valid
      if not (0 <= word_index < len(self.words)):
         raise ValueError(f"Invalid word index: {word_index}")
      
      # Get the start and end indices of the word span at the given word_index
      start, end = self.words[word_index]
      
      return self.string[start:end]
   def get(self,span) -> str:
      return self.string[span[0]:span[1]]
   def replace_word_StringSpans(self, word_index: int, replacement: str) -> Type['StringSpans']:
      ss = StringSpans()
      ss.string = self.replace_word(word_index, replacement)
      word_start, word_end = self.words[word_index]
      span_index = self.spans.index((word_start,word_end))
      new_len = len(replacement)
      word_len_diff = new_len - (word_end - word_start) 
      def f(span):
         start,end = span
         return (start,end) if end < word_start else (start+word_len_diff,end+word_len_diff)
      ss.words = [f(span) for span in self.words]
      ss.spans = [f(span) for span in self.spans]
      ss.non_words = [f(span) for span in self.non_words]
      ss.non_spaces = [f(span) for span in self.spans]
      ss.words[word_index] = (word_start,word_start+new_len)
      ss.spans[span_index] = (word_start,word_start+new_len)
      return ss
   def get_words(self) -> List[str]:
      return [self.string[start:end] for start,end in self.words]
   def index_span_text(self) -> Generator[tuple[int, int, int, str], None, None]:
      return ((i,start,end,self.string[start:end]) for i, (start,end) in enumerate(self.spans))
   def index_wordSpan_text(self) -> Generator[tuple[int, int, int, str], None, None]:
      return ((i,start,end,self.string[start:end]) for i, (start,end) in enumerate(self.words))
   def get_span_by_offset(self,offset) -> tuple[int, int]:
      span = next(((s,e) for s,e in self.spans if s<=offset<e),None)
      if span is None:
         raise ValueError(f'offset={offset} is not in any span')
      else:
         return span
   def get_word_by_offset(self,offset) -> tuple[int, int]:
      span = next(((s,e) for s,e in self.words if s<=offset<e),None)
      if span is None:
         raise ValueError(f'offset={offset} is not in any word')
      else:
         return span