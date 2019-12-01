import nltk

from textattack.constraints import Constraint
from textattack.tokenized_text import TokenizedText

class PartOfSpeech(Constraint):
    """ Constraints word swaps to only swap words with the same part of speech.
        Uses the NLTK universal part-of-speech tagger by default.
    """
    def __init__(self, tagset='universal', allow_verb_noun_swap=True):
        self.tagset = tagset
        self.allow_verb_noun_swap = allow_verb_noun_swap
   
    def _can_replace_pos(self, pos_a, pos_b):
        return (pos_a == pos_b) or (self.allow_verb_noun_swap and set([pos_a,pos_b]) <= set(['NOUN','VERB']))

    def _get_pos(self, before_ctx, word, after_ctx):
        _, pos_list = zip(*nltk.pos_tag(before_ctx + [word] + after_ctx, tagset=self.tagset))
        return pos_list[len(before_ctx)]
        
    def __call__(self, x, x_adv, original_text=None):
        if not isinstance(x, TokenizedText):
            raise TypeError('x must be of type TokenizedText')
        if not isinstance(x_adv, TokenizedText):
            raise TypeError('x_adv must be of type TokenizedText')
        
        try:
            i = x_adv.attack_attrs['modified_word_index']
            x_word = x.words[i]
            x_adv_word = x_adv.words[i]
        except AttributeError:
            raise AttributeError('Cannot apply word embedding distance constraint without `modified_word_index`')
        
        before_ctx = x.words[max(i-4,0):i]
        after_ctx = x.words[i+1:min(i+5,len(x.words))]
        cur_pos = self._get_pos(before_ctx, x_word, after_ctx)
        replace_pos = self._get_pos(before_ctx, x_adv_word, after_ctx)
        return self._can_replace_pos(cur_pos, replace_pos)