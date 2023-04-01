import re


def reverse_rules(input_file, output_file):
    with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
        for line in f_in:
            # Skip comments and empty lines
            if line.startswith('#') or not line.strip():
                continue
            
            # Parse the rule
            match_str, replace_str = line.strip().split('\t')
            
            # Reverse the rule
            if match_str[:2] == '((':
               if (match_str[:10] != r'((?:\W|^)['):
                  print(('>'*10)+match_str)
               reverse_match_str = match_str[:14]+ replace_str[2:-2] +match_str[-6:]
               reverse_replace_str = r'\1' + match_str[14:-6] + r'\2'
            elif match_str[0] == '(':
               if (match_str[:6] != r'(\W|^)'):
                  print(('>'*10)+match_str)
               reverse_match_str = match_str[:6] + replace_str[2:-2] + match_str[-6:]
               reverse_replace_str = match_str[6:-6]
            else:
               print(line)
               continue
            

            # Write the reversed rule to the output file
            f_out.write(f"{reverse_match_str}\t{reverse_replace_str}\n")

reverse_rules('misspelling.tsv', 'anti.misspelling.tsv')
reverse_rules('variant.tsv', 'anti.variant.tsv')
