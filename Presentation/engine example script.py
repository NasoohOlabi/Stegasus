from json import dumps, loads
from os import path

script_directory = path.dirname(path.abspath(__file__))

nl = []
el = []
with open(script_directory+'\\chat.example.presentation.log') as log, \
  open(script_directory+ '\\normal.chat.example','w') as no, \
  open(script_directory+ '\\encoded.chat.example','w') as eo :
    for line in log.readlines():
        if line.startswith("text="):
            line = line[len('text='):]
            line = loads(line)
            nl.append(line[0])
            el.append(line[-1])
    no.write(dumps(nl,indent=2))
    eo.write(dumps(el,indent=2))