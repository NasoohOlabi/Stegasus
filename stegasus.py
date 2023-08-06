#@title random_bit_stream
import random


def random_bit_stream(length=None):
    """Return a random string of zeros and ones of the given length (default: random integer between 0 and 100)."""
    if length is None:
        length = random.randint(0, 100)
    return ''.join(str(random.randint(0, 1)) for _ in range(length))
def int_to_binary_string(n: int, length: int):
    binary_str = bin(n)[2:]  # convert to binary string, remove '0b' prefix
    padded_str = binary_str.rjust(length, '0')  # pad with zeros to length
    return padded_str
  
from FrustratinglySimpleBert import MaskedStego

print ('\nSetting up Masked Stego\n')

masked_stego = MaskedStego()

print ('\nSetting up Masked Stego Completed\n')

from TypocerosJar import JavaJarWrapper

print ('\nSetting up Typoceros\n')
Typo = JavaJarWrapper()

print ('\nSetting up Typoceros Completed\n')


#@title Pipe
from typing import Any, Callable, Dict, List

from Emojier import Emojier


def pipe(callbacks: List[Callable], config: Dict[str, Any]={}, index=0):
    def process_callbacks(state, callbacks: List[Callable], config: Dict[str, Any]={}, index=0):
        # Get the current callback
        callback = callbacks[index]

        # Get the next callback (if exists)
        next_callback = None
        if index < len(callbacks) - 1:
            next_callback = lambda s, c, cf=config: process_callbacks(s, callbacks, cf, index + 1)

        # Call the callback with the current state, next callback, and config
        state = callback(state, next_callback, config)

        # Return the final state
        return state

    def _pipe(state):
        return process_callbacks(state, callbacks, config, index)

    return _pipe

def bert_callback(state, next_callback, config):
    if state is None:
        raise ValueError('State is None')

    pipe_verbose = config['pipe_verbose']
    encode = config['encode']
    decode = config['decode']
    message_pipe, bytes_pipe = state

    if encode:
      stega_bert = masked_stego(message_pipe[-1],bytes_pipe[-1], 3, 0.01)
      message_pipe.append(stega_bert.encoded_text)
      bytes_pipe.append(stega_bert.remaining_bytes)

    if next_callback is not None:
        state = next_callback(state, next_callback, config)

    if decode:
      encoded_text = message_pipe.pop()
      remaining_bytes = bytes_pipe.pop()
      encoded_bytes = masked_stego.decode(encoded_text,3,0.01)
      if encode and decode:
        assert encoded_bytes + remaining_bytes == bytes_pipe[-1]
      else:
        message_pipe.append(encoded_text)
        bytes_pipe.append(encoded_bytes + remaining_bytes)

    return state

def emojer_callback(state, next_callback, config):
    if state is None:
        raise ValueError('State is None')

    message_pipe, bytes_pipe = state
    text = message_pipe[-1]
    data = bytes_pipe[-1]
    verbose = config['verbose']

    pipe_verbose = config['pipe_verbose']
    encode = config['encode']
    decode = config['decode']

    if encode:
      encoded_text,rem = Emojier.encode(text,data)
      message_pipe.append(encoded_text)
      bytes_pipe.append(rem)

    if next_callback is not None:
        state = next_callback(state, next_callback, config)
    else:
      print(state)

    if decode:
      encoded_pipe_text = message_pipe.pop()
      rem_pipe_bytes = bytes_pipe.pop()

      original_text, deData = Emojier.decode(encoded_pipe_text)
      deData += rem_pipe_bytes
      if encode and decode:
        assert deData == bytes_pipe[-1]
        assert original_text == message_pipe[-1]
      else:
        message_pipe.append(original_text)
        bytes_pipe.append(deData)

    return state

def typo_callback(state, next_callback, config):
    if state is None:
        raise ValueError('State is None')

    message_pipe, bytes_pipe = state
    text = message_pipe[-1]
    data = bytes_pipe[-1]
    verbose = config['verbose']
    pipe_verbose = config['pipe_verbose']
    encode = config['encode']
    decode = config['decode']

    if pipe_verbose:
      print(state)
    if encode:

      encoded_text, rem = Typo.encode(text,data)

      message_pipe.append(encoded_text)
      bytes_pipe.append(rem)

    if next_callback is not None:
        state = next_callback(state, next_callback, config)

    if decode :
      encoded_pipe_text = message_pipe.pop()
      rem_pipe_bytes = bytes_pipe.pop()

      original_string, deData = Typo.decode(encoded_pipe_text)
      if encode and decode:
        assert original_string == text
        assert deData == data
      else:
        message_pipe.append(original_string)
        bytes_pipe.append(deData)


    return state

callbacks = [bert_callback, emojer_callback,typo_callback]
# # callbacks = [typo_callback]

# # Apply the function with an initial state
# initial_state = [['Hi, How are you?'],[random_bit_stream(30)]]
# p = pipe(callbacks, {"verbose": False,"pipe_verbose": False,"encode":True,"decode":False,"test":False})
# mq, bq = p(initial_state)

# print(mq[-1],bq[-1])


def StegasusEncode(text,bytes_str):
  initial_state = [[text],[bytes_str]]
  callbacks = [bert_callback, emojer_callback,typo_callback]
  p = pipe(callbacks, {"verbose": False,"pipe_verbose": False,"encode":True,"decode":False,"test":False})
  mq, bq = p(initial_state)
  return (mq[-1],bq[-1])
def StegasusDecode(text):
  initial_state = [[text],['']]
  callbacks = [bert_callback, emojer_callback,typo_callback]
  p = pipe(callbacks, {"verbose": False,"pipe_verbose": False,"encode":False,"decode":True,"test":False})
  mq, bq = p(initial_state)
  return (mq[-1],bq[-1])
def StegasusTest(text):
  initial_state = [[text],[random_bit_stream(len(text))]]
  callbacks = [bert_callback, emojer_callback,typo_callback]
  p = pipe(callbacks, {"verbose": False,"pipe_verbose": False,"encode":False,"decode":True,"test":False})
  mq, bq = p(initial_state)
  return (mq[-1],bq[-1])