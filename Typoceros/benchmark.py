import random

from SampleData import ConversationsRepo
from stegasus import random_bit_stream
from TypocerosJar import Typo


def runBenchmark():
  chat_id = random.randint(1,ConversationsRepo.ConversationsCount)
  print(f"chat_id\tc size\tbits\tratio")
  for i in range(100):
    for text in ConversationsRepo.get(chat_id):
      data = random_bit_stream(len(text))
      # data = '1' * len(text)
      # text = 'hi, how are you?'
      encoded_text,rem = Typo.encode(text,data)
      print('rem=',rem)
      _, deData = Typo.decode(encoded_text)
      deData += rem
      print(f'text="{text}"\n->\nencoded_text="{encoded_text}" \ndata="{data}"\ndeData="{deData}"\ndata==deData="{data==deData}"')
      print(f'ratio={len(data)-len(rem)} / {len(text)}={(len(data)-len(rem)) / len(text)}')
      assert data==deData
      print('\n')


      bits = len(text)-len(rem)
      coverSize = len(text)
      line = f"{chat_id}\t{coverSize}\t{bits}\t{(bits*100)//coverSize}"
      print(line)
      with open('typo benchmark.tsv','a') as f:
        f.write(line+'\n')
    chat_id = random.randint(1,ConversationsRepo.ConversationsCount)

# runBenchmark()