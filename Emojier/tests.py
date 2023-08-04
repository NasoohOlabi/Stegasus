import random

from Emojier import Emojier
from stegasus import random_bit_stream

tests = 10
def runTests():
  print(f"Running {tests} tests")
  for i in range(tests):
    data = random_bit_stream(600)
    text = 'hi, how are you?'
    verbose = False
    encoded_text,rem = Emojier.encode(text,data)
    print('rem=',rem)
    _, deData = Emojier.decode(encoded_text)
    deData += rem
    print(f'text="{text}"\n->\nencoded_text="{encoded_text}" \ndata="{data}"\ndeData="{deData}"\ndata==deData="{data==deData}"')
    print(f'ratio={len(data)-len(rem)} / {len(text)}={(len(data)-len(rem)) / len(text)}')
    assert data==deData
    print('\n')
    print("#"*100)
    print('\n')
# runTests()
# 0000


def test_stream():
  gened = set()
  byte_string_length = 48
  for i in range(2**byte_string_length):
    x = random.randint(0,2**byte_string_length-1)
    while x in gened:
      x = random.randint(0,2**byte_string_length-1)
    gened.add(x)
    yield Emojier.int_to_binary_string(x,byte_string_length)
    # yield x