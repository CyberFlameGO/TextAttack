import numpy as np
import os

from textattack import utils as utils
from textattack.transformations.word_swap import WordSwap

class WordSwapEmbedding(WordSwap):
    """ Transforms an input by replacing its words with synonyms in the word
        embedding space. """
    
    PATH = '/p/qdata/jm8wx/research/text_attacks/RobustNLP/AttackGeneration/word_embeddings'
    
    def __init__(self, max_candidates=15, word_embedding='paragramcf', 
        replace_stopwords=False, **kwargs):
        super().__init__(**kwargs)
        self.max_candidates = max_candidates
        
        if word_embedding == 'paragramcf':
            word_embeddings_folder = 'paragramcf'
            word_embeddings_file = 'paragram.npy'
            word_list_file = 'wordlist.pickle'
            nn_matrix_file = 'nn.npy'
        else:
            raise ValueError(f'Could not find word embedding {word_embedding}')
        
        # Download embeddings if they're not cached.
        utils.download_if_needed(WordSwapEmbedding.PATH)
        # Concatenate folder names to create full path to files.
        word_embeddings_file = os.path.join(WordSwapEmbedding.PATH, word_embeddings_folder, word_embeddings_file)
        word_list_file = os.path.join(WordSwapEmbedding.PATH, word_embeddings_folder, word_list_file)
        nn_matrix_file = os.path.join(WordSwapEmbedding.PATH, word_embeddings_folder, nn_matrix_file)
        
        # Actually load the files from disk.
        self.word_embeddings = np.load(word_embeddings_file)
        self.word_embedding_word2index = np.load(word_list_file, allow_pickle=True)
        self.nn = np.load(nn_matrix_file)
        
        # Build glove dict and index.
        self.word_embedding_index2word = {}
        for word, index in self.word_embedding_word2index.items():
            self.word_embedding_index2word[index] = word
        
    def _get_replacement_words(self, word):
        """ Returns a list of possible 'candidate words' to replace a word in a sentence 
            or phrase. Based on nearest neighbors selected word embeddings.
        """
        try:
            word_id = self.word_embedding_word2index[word.lower()]
            nnids = self.nn[word_id][1:self.max_candidates+1]
            candidate_words = []
            for i, nbr_id in enumerate(nnids):
                nbr_word = self.word_embedding_index2word[nbr_id]
                candidate_words.append(recover_word_case(nbr_word, word))
            return candidate_words
        except KeyError:
            # This word is not in our word embedding database, so return an empty list.
            return []

def recover_word_case(word, reference_word):
    """ Makes the case of `word` like the case of `reference_word`. Supports 
        lowercase, UPPERCASE, and Capitalized. """
    if reference_word.islower():
        return word.lower()
    elif reference_word.isupper() and len(reference_word) > 1:
        return word.upper()
    elif reference_word[0].isupper() and reference_word[1:].islower():
        return word.capitalize()
    else:
        # if other, just do not alter the word's case
        return word