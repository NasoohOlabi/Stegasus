import os
import re
from dataclasses import dataclass, field
from typing import List

from icecream import ic

old = True

first_line = re.compile(r'idx=(\d+),payload size=(\d+)')
chat_line = re.compile(r'([^:]+): `([^`]+)`')
step_line = lambda : re.compile(r'^(.*) (\d+)$') if old else  re.compile(r'text length=(\d+).*encoded bits=(\d+).*ratio=(\d+)%.*text=([^\n]+)')  

@dataclass
class Summary:
  ratio: int = field(init=True,repr=True)
  bits: int = field(init=True,repr=True)
  encoded_text: str = field(init=True,repr=True)
  text: str = field(init=True,repr=True)
  person: str = field(init=True,repr=True)
  rem_payload_size: int = field(init=True,repr=True)

def get_chat(lines: List[str],after=0):
  
  chat = []
  s = lines.index('--------------------- Chat ---------------------',after)
  e = lines.index( '------------------------------------------------',s)
  for i in range(s+1,e):
    message_match = chat_line.match(lines[i])
    if message_match is None:
      break
    message_line_data = message_match.groups()
    chat.append(message_line_data)
  return chat, e
  

for dirpath, dirnames, filenames in os.walk('.'):
  if not dirpath.startswith('.\\chat'):
    continue
  for file in filenames:
    if not dirpath.startswith('.\\chat') \
    or file.endswith('original.chat') \
      or file.endswith('encoded.chat') \
        or file.endswith('.info') \
        or file.endswith('.txt'):
        continue
    
    old = file.endswith('.old')
    runOutput = ''
    with open(dirpath+'\\'+file) as f:
      runOutput = f.read()
    lines = runOutput.splitlines()
    match = first_line.match(lines[0])
    if match is None:
      break
    idx, payloadSize = match.groups()
    
    original_chat, chat_end = get_chat(lines)
    # ic(original_chat)
    
    i = chat_end
    steps = []
    while lines[i] != '-'*21+' Chat '+'-'*21:
      match = step_line().match(lines[i])
      if match is not None:
        steps.append(match.groups())
      i += 1
    # ic(steps)
    
    encoded_chat, _ = get_chat(lines,chat_end)
    
    steps_summary = [Summary(person=u[0],text=u[1],encoded_text=v[0],rem_payload_size=v[1],ratio=0,bits=0) for u,v in zip(original_chat,steps)] \
      if old else \
        [Summary(person=u[0],text=u[1],encoded_text=v[3],rem_payload_size=0,ratio=int(v[2]),bits=int(v[1])) for u,v in zip(original_chat,steps)]
    
    if old:
      for idx in range(len(steps_summary)):
        step = steps_summary[idx]

        carrier_len = len(step.text)
        encoded_bits_len = (int(steps_summary[idx-1].rem_payload_size) - int(step.rem_payload_size) if idx > 0 else int(payloadSize) - int(step.rem_payload_size))
        ratio = (encoded_bits_len*100 // carrier_len) 
        
        steps_summary[idx].ratio = int(round(ratio,0))
        steps_summary[idx].bits = encoded_bits_len
    
    if not os.path.isdir(dirpath+f'\\messages'):
      os.mkdir(dirpath+f'\\messages')
    for idx, step in enumerate(steps_summary):
      with open(dirpath+f'\\messages\\m{idx+1}.info','w') as o:
        o.writelines([
          f'ratio={step.ratio}\n'
          f'original={step.text}\n'
          f'encoded={step.encoded_text}\n'
          ])
    
      
    with open(dirpath+f'\\{steps_summary[0].person}.info','w') as o:
      ratio = 0
      A_ratios = list(map((lambda x: x.ratio),(x for i, x in enumerate(steps_summary) if i % 2 == 0)))
      A_payload_size = sum(map((lambda x: x.bits),(x for i, x in enumerate(steps_summary) if i % 2 == 0)))
      A_avg_ratio = sum(A_ratios) // len(A_ratios)
      o.writelines([
        f"{steps_summary[0].person}'s ratio={A_avg_ratio}%\n",
        f"{steps_summary[0].person}'s payload size={A_payload_size}bits\n",
        ] + [f'ratio={x.ratio}\noriginal text={x.text}\nencoded text={x.encoded_text}\n' for i, x in enumerate(steps_summary) if i%2 ==0]
                   )
      
    with open(dirpath+f'\\{steps_summary[1].person}.info','w') as o:
      B_ratios = list(map((lambda x: x.ratio),(x for i, x in enumerate(steps_summary) if i % 2 != 0)))
      B_avg_ratio = sum(B_ratios) // len(B_ratios)
      B_payload_size = sum(map((lambda x: int(x.bits)),(x for i, x in enumerate(steps_summary) if i % 2 != 0)))
      o.writelines([
        f"{steps_summary[1].person}'s ratio={B_avg_ratio}%\n",
        f"{steps_summary[1].person}'s payload size={B_payload_size}bits\n"
        ] + [(50*'-')+'\n'+f'ratio={x.ratio}\noriginal text={x.text}\nencoded text={x.encoded_text}\n' for i, x in enumerate(steps_summary) if i%2 !=0]
                   )
    
    with open(dirpath+'\\normal chat.txt','w') as nor:
      nor.write(f'\n{"_"*50}\n\n'.join([f'{step.person}:`{step.text.strip()}`' for step in steps_summary]))

    with open(dirpath+'\\encoded chat.txt','w') as enc:
      enc.write(f'\n{"_"*50}\n\n'.join([f'{step.person}:`{step.encoded_text.strip()}`' for step in steps_summary]))

    print(f"✅ {dirpath}\\{file}")
    
    os.remove(dirpath+'\\'+file)