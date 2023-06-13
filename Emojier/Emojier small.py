import csv
import re
import urllib.request
from itertools import chain
from math import floor, log2
from typing import Any, Generator, List

import numpy as np
from scipy.special import softmax
from transformers import (AutoModelForSequenceClassification, AutoTokenizer,
                          TFAutoModelForSequenceClassification)


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
  dist = chain(range(max_odd_ind,0,-2),range(0,max_even_ind + 1 , 2))
  return [lst[i] for i in dist]
class Emojier:
  
  def setVerbose(self,v:bool):
    self.verbose = v
  
  def __init__(self):

    task='emoji'
    MODEL = f"cardiffnlp/twitter-roberta-base-{task}"

    self.tokenizer = AutoTokenizer.from_pretrained(MODEL)

    # download label mapping
    self.labels=[]
    mapping_link = f"https://raw.githubusercontent.com/cardiffnlp/tweeteval/main/datasets/{task}/mapping.txt"
    with urllib.request.urlopen(mapping_link) as f:
        html = f.read().decode('utf-8').split("\n")
        csvreader = csv.reader(html, delimiter='\t')
    self.labels = [row[1] for row in csvreader if len(row) > 1]

    # PT
    self.model = AutoModelForSequenceClassification.from_pretrained(MODEL)
    self.model.save_pretrained(MODEL)
    
    self.verbose = False
    
  def preprocess(self,text:str):
      new_text = []
      for t in text.split(" "):
          t = '@user' if t.startswith('@') and len(t) > 1 else t
          t = 'http' if t.startswith('http') else t
          new_text.append(t)
      return " ".join(new_text)
  def _predict(self,text:str) -> List[str]:# Preprocess text (username and link placeholders)

    text = self.preprocess(text)
    encoded_input = self.tokenizer(text, return_tensors='pt')
    output = self.model(**encoded_input)
    scores = output[0][0].detach().numpy()
    scores = softmax(scores)

    ranking = np.argsort(scores)
    ranking = ranking[::-1]
    result = ['']
    for i in range(scores.shape[0]):
        l = self.labels[ranking[i]]
        # s = scores[ranking[i]]
        # print(f"{i+1}) {l} {np.round(float(s), 4)}")
        result.append(l)
    return result
  
  def encode(self,text:str,bytes_str:str):
    ticks = pre_texts(text)
    ticks_emoticons = map(lambda x: (x,self._predict(x)),ticks)
    original_length = len(text)
    new_ending = lambda x : (len(text) - original_length) + len(x)
    for pre_text, emoji_options in ticks_emoticons:
      if self.verbose:
        print(f"word: {pre_text} \nlen: {len(emoji_options)} \temoji_options[:10]: {emoji_options[:10]}")

      bits = floor(log2(len(emoji_options)))
      taken_bits = bytes_str[:bits]
      ind = int(taken_bits, 2)
      bytes_str = bytes_str[bits:]
      emojis = emoji_options[ind]
      
      if len(emojis) > 0:
        breakPoint = new_ending(pre_text)
        text = f'{text[0:breakPoint]} {emojis}{text[breakPoint:]}'
      if self.verbose:
        print(f'>>>encoding {taken_bits} = {ind} as {emojis}\nencoded text={text}')
      
  # https://huggingface.co/cardiffnlp/bertweet-base-emoji
      
#       from transformers import AutoModelForSequenceClassification
# from transformers import TFAutoModelForSequenceClassification
# from transformers import AutoTokenizer
# import numpy as np
# from scipy.special import softmax
# import csv
# import urllib.request

# # Preprocess text (username and link placeholders)
# def preprocess(text):
#     new_text = []
#     for t in text.split(" "):
#         t = '@user' if t.startswith('@') and len(t) > 1 else t
#         t = 'http' if t.startswith('http') else t
#         new_text.append(t)
#     return " ".join(new_text)

# # Tasks:
# # emoji, emotion, hate, irony, offensive, sentiment
# # stance/abortion, stance/atheism, stance/climate, stance/feminist, stance/hillary

# task='emoji'
# MODEL = f"cardiffnlp/twitter-roberta-base-{task}"

# tokenizer = AutoTokenizer.from_pretrained(MODEL)

# # download label mapping
# labels=[]
# mapping_link = f"https://raw.githubusercontent.com/cardiffnlp/tweeteval/main/datasets/{task}/mapping.txt"
# with urllib.request.urlopen(mapping_link) as f:
#     html = f.read().decode('utf-8').split("\n")
#     csvreader = csv.reader(html, delimiter='\t')
# labels = [row[1] for row in csvreader if len(row) > 1]

# # PT
# model = AutoModelForSequenceClassification.from_pretrained(MODEL)
# model.save_pretrained(MODEL)

# text = "Looking forward to Christmas"
# text = preprocess(text)
# encoded_input = tokenizer(text, return_tensors='pt')
# output = model(**encoded_input)
# scores = output[0][0].detach().numpy()
# scores = softmax(scores)

# # # TF
# # model = TFAutoModelForSequenceClassification.from_pretrained(MODEL)
# # model.save_pretrained(MODEL)

# # text = "Looking forward to Christmas"
# # text = preprocess(text)
# # encoded_input = tokenizer(text, return_tensors='tf')
# # output = model(encoded_input)
# # scores = output[0][0].numpy()
# # scores = softmax(scores)

# ranking = np.argsort(scores)
# ranking = ranking[::-1]
# for i in range(scores.shape[0]):
#     l = labels[ranking[i]]
#     s = scores[ranking[i]]
#     print(f"{i+1}) {l} {np.round(float(s), 4)}")

# text = "that's sick"
# text = preprocess(text)
# encoded_input = tokenizer(text, return_tensors='pt')
# output = model(**encoded_input)
# scores = output[0][0].detach().numpy()
# scores = softmax(scores)

# # # TF
# # model = TFAutoModelForSequenceClassification.from_pretrained(MODEL)
# # model.save_pretrained(MODEL)

# # text = "Looking forward to Christmas"
# # text = preprocess(text)
# # encoded_input = tokenizer(text, return_tensors='tf')
# # output = model(encoded_input)
# # scores = output[0][0].numpy()
# # scores = softmax(scores)

# ranking = np.argsort(scores)
# ranking = ranking[::-1]
# for i in range(scores.shape[0]):
#     l = labels[ranking[i]]
#     s = scores[ranking[i]]
#     print(f"{i+1}) {l} {np.round(float(s), 4)}")