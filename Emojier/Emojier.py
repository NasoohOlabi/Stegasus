#@title https://github.com/farkmarnum/emojify
import json
import random
from math import log2,floor 
import itertools
import re
import os

# Get the path of the script
script_path = os.path.abspath(__file__)

ROOT_DIR = os.path.dirname(script_path)

emoticons_file = ROOT_DIR + './emoji-data.json'

with open(emoticons_file, 'r') as f:
		emoji_data = json.load(f)

		#@title Constants
regex = re.compile(r'[a-z0-9]+')
ALL_EMOJIS = set()
for k,v in emoji_data.items():
	if regex.match(k) is None:
		ALL_EMOJIS.add(k)
		# print('k',k)
	if isinstance(v,str) and regex.match(v) is None:
		ALL_EMOJIS.add(v)
		# print('v',v)
	else:
		for kk,vv in v.items():
			if regex.match(kk) is None:
				ALL_EMOJIS.add(kk)
				# print('kk',kk)
			if isinstance(vv,str) and regex.match(vv) is None:
				ALL_EMOJIS.add(v)
				# print('vv',vv)
EMOJER_COMMON_WORDS = {
		'a',
		'an',
		'as',
		'is',
		'if',
		'of',
		'the',
		'it',
		'its',
		'or',
		'are',
		'this',
		'with',
		'so',
		'to',
		'at',
		'was',
		'and',
	}


class Emojier:
	@staticmethod
	def gaussian_order(lst):
		length = len(lst)
		max_odd_ind = length - 1 if length % 2 == 0 else length - 2
		max_even_ind = length - 1 if length % 2 != 0 else length - 2
		dist = itertools.chain(range(max_odd_ind,0,-2),range(0,max_even_ind + 1 , 2))
		return [lst[i] for i in dist]

	@staticmethod
	def encode(input_str: str, bytes_str: str, verbose=False) -> str:
		if verbose:
			print('encode:')
		words = StringSpans(input_str).get_words()
		result = ''
		for word_raw in words:
			word = ''.join(c for c in word_raw if c.isalnum()).lower()
			acc_next = f'{result} {word_raw}'
			is_too_common = word in EMOJER_COMMON_WORDS

			emoji_options = \
				Emojer.gaussian_order( ['']+
					[x[0] for x in
						sorted(
							emoji_data.get(word, {}).items(),
							key=lambda x:x[1],
							reverse=True
						)
					]
				)

			if verbose:
				print(f"word: {word} \tis_too_common={is_too_common} \nlen: {len(emoji_options)} \temoji_options: {emoji_options}")

			if is_too_common or len(emoji_options)<2:
				result = acc_next
			else:
				bits = floor(log2(len(emoji_options)))
				taken_bits = bytes_str[:bits]
				ind = int(taken_bits, 2)
				bytes_str = bytes_str[bits:]
				emojis = emoji_options[ind]
				if verbose:
					print(f'>>>encoding {taken_bits} = {ind} as {emojis}')
				result = f'{acc_next} {emojis}' if len(emojis) > 0 else acc_next

		return result.strip(), bytes_str

	@staticmethod
	def decode(input_str: str, verbose=False) -> str:
		if verbose:
			print('decoding!')
		words = [input_str[s:e] for s,e in StringSpans(input_str).non_spaces]
		result = ''
		bytes_str = ''
		for i, word_raw in enumerate(words[:-1]):
			if word_raw in ALL_EMOJIS:
				continue
			word = ''.join(c for c in word_raw if c.isalnum()).lower()

			acc_next = f'{result} {word_raw}'
			is_too_common = word in EMOJER_COMMON_WORDS

			emoji_options = \
				Emojer.gaussian_order( ['']+
					[x[0] for x in
						sorted(
							emoji_data.get(word, {}).items(),
							key=lambda x:x[1],
							reverse=True
						)
					]
				)

			if verbose:
				print(f"word: {word} \tis_too_common={is_too_common} \nlen: {len(emoji_options)} \temoji_options: {emoji_options}")

			if is_too_common or len(emoji_options)<2:
				result = acc_next
			else:
				bits = floor(log2(len(emoji_options)))
				if words[i+1] in emoji_options:
					index = emoji_options.index(words[i+1])
				else:
					index = emoji_options.index('')
				data_extracted = int_to_binary_string(index,bits)
				if verbose:
					print(f'decoding word:"{words[i]}" next word:"{words[i+1]}" length:"{len(emoji_options)}"')
					print(f'bits:"{bits}" data extracted:"{data_extracted}" index:"{index}"')
				bytes_str += data_extracted
		return result.strip(), bytes_str

# tests = 10
# print(f"Running {tests} tests")
# for i in range(tests):
# 	data = random_bit_stream(60)
# 	# text = 'hi, how are you?'
# 	text = LOONG_TEXT
# 	verbose = True
# 	encoded_text,rem = Emojer.encode(text,data,verbose=verbose)
# 	print('rem=',rem)
# 	_, deData = Emojer.decode(encoded_text,verbose=verbose)
# 	deData += rem
# 	print(f'text="{text}"\n->\nencoded_text="{encoded_text}" \ndata="{data}"\ndeData="{deData}"\ndata==deData="{data==deData}"')
# 	print(f'ratio={len(data)-len(rem)} / {len(text)}={(len(data)-len(rem)) / len(text)}')
# 	assert data==deData
# 	print('\n')
# 	print("#"*100)
# 	print('\n')
