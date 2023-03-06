qwerty_neighbors = {
   'q': 'w',
   'w': 'qe',
   'e': 'wr',
   'r': 'et',
   't': 'ry',
   'y': 'tu',
   'u': 'yi',
   'i': 'uo',
   'o': 'ip',
   'p': 'o',
   'a': 's',
   's': 'ad',
   'd': 'sf',
   'f': 'dg',
   'g': 'fh',
   'h': 'gj',
   'j': 'hk',
   'k': 'jl',
   'l': 'k',
   'z': 'x',
   'x': 'zc',
   'c': 'xv',
   'v': 'cb',
   'b': 'vn',
   'n': 'bm',
   'm': 'n'
}

qwerty_neighbors_neighbors = {'q': 'e', 'w': 'r', 'e': 'qt', 'r': 'wy', 't': 'eu', 'y': 'ir', 'u': 'ot', 'i': 'py', 'o': 'u', 'p': 'i', 'a': 'd', 's': 'f', 'd': 'ag', 'f': 'sh', 'g': 'jd', 'h': 'kf', 'j': 'gl', 'k': 'h', 'l': 'j', 'z': 'c', 'x': 'v', 'c': 'zb', 'v': 'xn', 'b': 'cm', 'n': 'v', 'm': 'b'}

def neighbor_neighbor_thats_not_neighbor(c:str,n:str)->str:
   s1 = qwerty_neighbors_neighbors[c] 
   s2 = qwerty_neighbors[n]
   return ''.join(set(s1).intersection(set(s2)))



rules = {} 
anti_rules = {} 

# fat fingers
for c,ns in qwerty_neighbors.items():
   for n in ns:
      cn = '[^\\s'+c+n+']'
      cnn = '[^\\s'+c+n+neighbor_neighbor_thats_not_neighbor(c,n)+']'
      
      rules[f'({cnn*2}){c}({cn*2})'] = f'\\1{n+c}\\2'
      rules[f'({cn*2}){c}({cnn*2})'] = f'\\1{c+n}\\2'
      rules[f'({cnn*2}){c}({cnn*2})'] = f'\\1{n}\\2'

# long shift
for c in qwerty_neighbors.keys():
   rules[f'((\\s|^)[A-Z]){c}([a-z])'] = f'\\1{c.upper()}\\2'

# odd repetitions is zero even is one
for c in qwerty_neighbors.keys():
   rules[f'(^|[^{c}])({c}({c}{c})+)([^{c}]|$)'] = f'\\1\\2{c}\\4'

# fat fingers require grammar tool

# long shift
for c in qwerty_neighbors.keys():
   anti_rules[f'((\\s|^)[A-Z]){c.upper()}([a-z])'] = f'\\1{c.upper()}\\2'

# odd repetitions is zero even is one
for c in qwerty_neighbors.keys():
   anti_rules[f'(^|[^{c}]){c}({c}({c}{c})+)([^{c}]|$)'] = f'\\1\\2{c}\\4'
   

with open('keyboard.tsv','w') as f:
   for k,v in rules.items():
      f.write(f'{k}\t{v}\n')

with open('anti.keyboard.tsv','w') as f:
   for k,v in anti_rules.items():
      f.write(f'{k}\t{v}\n')