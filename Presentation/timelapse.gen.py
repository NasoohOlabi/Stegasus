from json import dumps, loads
from os import mkdir, path, walk
from re import compile, sub

template = ''

dirname = path.dirname(__file__)

with open(dirname+ '\\timeLapse.template.html') as f:
  template = f.read()
start1 = 'vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv\n'
start2 = 'valid_slots: \n'

end = '''^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n'''

def make_windows_filename(s):
    # Define a list of invalid characters for Windows file names
    invalid_chars = r'[/\\:*?"<>|]'

    # Replace invalid characters with underscores
    clean_s = sub(invalid_chars, '_', s)

    # Remove leading and trailing spaces and dots
    clean_s = clean_s.strip(' .')

    # Ensure the filename is not empty
    if not clean_s:
        clean_s = 'untitled'

    # Limit the filename length to 255 characters
    clean_s = clean_s[:255]

    return clean_s

cnt = 0
with open(dirname + '\\Typoceros.log','r') as log:
  inRange = False
  start1_flag = False
  start2_flag = False
  end_flag = False
  texts = []
  last_arrow = -1
  for i, line in enumerate(log):
    end_flag = line == end
      
    if start1_flag and start2_flag and not end_flag:
      if line.startswith('|>'):
        last_arrow = i
      elif i == last_arrow + 1 and len(texts) == 0:
        line = line.strip()
        texts.append(line)
      elif i == last_arrow + 2:
        line = line.strip()
        texts.append(line)

    elif start1_flag and start2_flag and end_flag:
      with open(dirname+f'\\generated examples\\{make_windows_filename(texts[0])}.html','w') as o:
        o.write(template.replace('$$$$$$$$$$$$$$',dumps(texts)))
      if cnt == 1000:
        break
      cnt += 1
      texts = []
      start1_flag = False
      start2_flag = False
      
    start1_flag = start1_flag or (line == start1)
    start2_flag = start2_flag or (line == start2)