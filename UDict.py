import os
import pickle

import pygtrie

# Get the path of the script
script_path = os.path.abspath(__file__)

ROOT_DIR = os.path.dirname(script_path)

dict_path = ROOT_DIR + '/dict.pkl'

if not os.path.exists(dict_path):
	trie = pygtrie.CharTrie()
	with open(dict_path, 'wb') as f:
		pickle.dump(trie, f)

# Load the trie from the file using pickle
with open(dict_path, 'rb') as f:
	trie = pickle.load(f)

def add_word(word:str) -> None:
	trie[word] = True
	# Save the trie to a file using pickle
	with open(dict_path, 'wb') as f:
		pickle.dump(trie, f)

def check_word(word:str) -> bool:
	return word in trie


if __name__ == '__main__':
	print(trie)