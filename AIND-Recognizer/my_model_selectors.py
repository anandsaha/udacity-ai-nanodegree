import math
import statistics
import warnings

import numpy as np
from hmmlearn.hmm import GaussianHMM
from sklearn.model_selection import KFold
from asl_utils import combine_sequences


class ModelSelector(object):
    '''
    base class for model selection (strategy design pattern)
    '''

    def __init__(self, all_word_sequences: dict, all_word_Xlengths: dict, this_word: str,
                 n_constant=3,
                 min_n_components=2, max_n_components=10,
                 random_state=14, verbose=False):
        self.words = all_word_sequences
        self.hwords = all_word_Xlengths
        self.sequences = all_word_sequences[this_word]
        self.X, self.lengths = all_word_Xlengths[this_word]
        self.this_word = this_word
        self.n_constant = n_constant
        self.min_n_components = min_n_components
        self.max_n_components = max_n_components
        self.random_state = random_state
        self.verbose = verbose

    def select(self):
        raise NotImplementedError

    def base_model(self, num_states):
        # with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        # warnings.filterwarnings("ignore", category=RuntimeWarning)
        try:
            hmm_model = GaussianHMM(n_components=num_states, covariance_type="diag", n_iter=1000,
                                    random_state=self.random_state, verbose=False).fit(self.X, self.lengths)
            if self.verbose:
                print("model created for {} with {} states".format(self.this_word, num_states))
            return hmm_model
        except:
            if self.verbose:
                print("failure on {} with {} states".format(self.this_word, num_states))
            return None


class SelectorConstant(ModelSelector):
    """ select the model with value self.n_constant

    """

    def select(self):
        """ select based on n_constant value

        :return: GaussianHMM object
        """
        best_num_components = self.n_constant
        return self.base_model(best_num_components)


class SelectorBIC(ModelSelector):
    """ select the model with the lowest Bayesian Information Criterion(BIC) score

    http://www2.imm.dtu.dk/courses/02433/doc/ch6_slides.pdf
    Bayesian information criteria: BIC = -2 * logL + p * logN
    """

    def select(self):
        """ select the best model for self.this_word based on
        BIC score for n between self.min_n_components and self.max_n_components

        :return: GaussianHMM object
        """
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        # TODO implement model selection based on BIC scores
        # Ref: https://discussions.udacity.com/t/number-of-parameters-bic-calculation/233235/15
        
        best_model = None
        best_model_bic_score = float("inf")

        for num_states in range(self.min_n_components, self.max_n_components + 1):
            hmm_model = self.base_model(num_states)
            if hmm_model is not None:
                try:

                    logL = hmm_model.score(self.X, self.lengths) 

                    num_features = self.X.shape[1]
                    p = num_states*num_states + 2*num_states*num_features-1
                    N = len(self.X)    

                    BIC = -2 * logL + p * np.log(N)

                    if BIC < best_model_bic_score:
                        best_model = hmm_model 
                        best_model_bic_score = BIC

                except:
                    pass

        return best_model


class SelectorDIC(ModelSelector):
    ''' select best model based on Discriminative Information Criterion

    Biem, Alain. "A model selection criterion for classification: Application to hmm topology optimization."
    Document Analysis and Recognition, 2003. Proceedings. Seventh International Conference on. IEEE, 2003.
    http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.58.6208&rep=rep1&type=pdf
    DIC = log(P(X(i)) - 1/(M-1)SUM(log(P(X(all but i))
    '''

    logl_cache = {}
    
    @staticmethod
    def generate_cache(selector):
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        min_components = selector.min_n_components
        max_components = selector.max_n_components
        random_state = selector.random_state

        for word in selector.words:
            #print("Preprocessing ", word)
            num_state_cache = {}
            for num_states in range(min_components, max_components+1):
                X, lengths = selector.hwords[word]
                try:
                    model = GaussianHMM(n_components=num_states, covariance_type="diag", n_iter=1000, 
                                        random_state=selector.random_state, verbose=False).fit(X, lengths)
                    score = model.score(X, lengths)
                    num_state_cache[num_states] = score
                except:
                    # print("Failed to calculate score for word {0}, num state {1}".format(word, num_states))
                    pass
                
            SelectorDIC.logl_cache[word] = num_state_cache

    
    def select(self):
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        # TODO implement model selection based on DIC scores
        
        if len(SelectorDIC.logl_cache) == 0:
            SelectorDIC.generate_cache(self)
 
        best_num_states = 0 
        best_model_dic_score = float("-inf")
        total_words =  len(self.words.keys())

        for num_states in range(self.min_n_components, self.max_n_components + 1):
            try:
                logL = SelectorDIC.logl_cache[self.this_word][num_states]  

                listLogL = []
                for word in self.words.keys():
                    if word != self.this_word:
                        try:
                            listLogL.append(SelectorDIC.logl_cache[word][num_states])
                        except:
                            pass

                DIC = logL - np.average(listLogL)

                if DIC > best_model_dic_score:
                    best_num_states = num_states
                    best_model_dic_score = DIC

            except:
                pass

        return self.base_model(best_num_states)


class SelectorCV(ModelSelector):
    ''' select best model based on average log Likelihood of cross-validation folds

    '''

    def select(self):
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        # TODO implement model selection using CV

        num_splits = 2

        if num_splits > len(self.sequences):
            return None # Cannot proceed, not enough data
 
        best_num_states = self.n_constant
        best_average_logL_score = float("-inf")

        for num_states in range(self.min_n_components, self.max_n_components + 1):

            all_scores = []
            split_method = KFold(n_splits=num_splits)

            for cv_train_idx, cv_test_idx in split_method.split(self.sequences):
                train_X, train_lengths = combine_sequences(cv_train_idx, self.sequences)
                test_X, test_lengths = combine_sequences(cv_test_idx, self.sequences)

                try:
 
                    hmm_model = GaussianHMM(n_components=num_states, covariance_type="diag", 
                            n_iter=1000, random_state=self.random_state, verbose=False)

                    hmm_model.fit(train_X, train_lengths)
                    score = hmm_model.score(test_X, test_lengths)
                    all_scores.append(score)
                except:
                    pass

            logL = float("-inf")
            if len(all_scores) > 0:
                logL = np.average(all_scores)

            if logL > best_average_logL_score:
                best_average_logL_score = logL
                best_num_states = num_states

        return self.base_model(best_num_states)

