import spacy


def extract_pos(text):
    """Extract the start and end positions of verbs, nouns, and adjectives in the given text."""
    # Load the spaCy English model
    nlp = spacy.load('en_core_web_sm')
    
    # Parse the text with spaCy
    doc = nlp(text)
    
    # Create a dictionary to store the start and end positions of each POS tag
    # pos_dict = {
    #     'VERB': [],
    #     'NOUN': [],
    #     'ADJ': []
    # }
    pos_list = []
    
    # Loop through each token in the parsed text
    for token in doc:
        if token.pos_ in ['VERB','NOUN','ADJ']:
            # If the token's POS tag is a verb, noun, or adjective, add its start and end positions to the dictionary
            # pos_dict[token.pos_]
            pos_list.append((token.idx, token.idx + len(token)))
    
    return sorted(pos_list)
