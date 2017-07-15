import warnings
from asl_data import SinglesData


def recognize(models: dict, test_set: SinglesData):
    """ Recognize test word sequences from word models set

   :param models: dict of trained models
       {'SOMEWORD': GaussianHMM model object, 'SOMEOTHERWORD': GaussianHMM model object, ...}
   :param test_set: SinglesData object
   :return: (list, list)  as probabilities, guesses
       both lists are ordered by the test set word_id
       probabilities is a list of dictionaries where each key a word and value is Log Liklihood
           [{SOMEWORD': LogLvalue, 'SOMEOTHERWORD' LogLvalue, ... },
            {SOMEWORD': LogLvalue, 'SOMEOTHERWORD' LogLvalue, ... },
            ]
       guesses is a list of the best guess words ordered by the test set word_id
           ['WORDGUESS0', 'WORDGUESS1', 'WORDGUESS2',...]
   """
    

    warnings.filterwarnings("ignore", category=DeprecationWarning)
    probabilities = []
    guesses = []
    # TODO implement the recognizer
    
    for unknown_word_index in range(test_set.num_items):
        
        word_probs = {}
        max_prob = float("-inf")
        the_word = None
        
        X, lengths = test_set.get_item_Xlengths(unknown_word_index)
        
        for word, model in models.items():
            
            try:
                prob = model.score(X, lengths)
            except:
                prob = float("-inf")
            
            word_probs[word] = prob
            
            if prob > max_prob:
                max_prob = prob
                the_word = word
     
        probabilities.append(word_probs)
        guesses.append(the_word)
        
        if the_word is None:
            print("None found")
    
    return probabilities, guesses
    
