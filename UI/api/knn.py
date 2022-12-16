
"""

Heavily modified from the KNN tutorial at https://towardsdatascience.com/text-classification-using-k-nearest-neighbors-46fa8a77acc5

"""
import warnings
warnings.filterwarnings('ignore')

import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus import genesis
nltk.download('genesis')
nltk.download('wordnet')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
genesis_ic = wn.ic(genesis, False, 0.0)
import copy
import numpy as np
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
from nltk.stem.porter import PorterStemmer
from nltk.stem import SnowballStemmer
from nltk.stem.lancaster import LancasterStemmer
from nltk.corpus import stopwords
from sklearn.metrics import roc_auc_score
from collections import Counter
import re

def format_tags(df):
    tags = []
    tag_lists = []

    for subjects in df.subjects:
        if type(subjects) is str:
            s = subjects.split(",")
        else:
            if type(subjects) is list:
                s = subjects
            else:
                s = []
        s = [t.lstrip().rstrip() for t in s]
        tag_lists.append(s)
        for tag in s:
            tags.append(tag)
    df['tags'] = tag_lists
    return df, tags


# Helper function for masking dataframe with relevant tags
def health(x):
    health_tags = ['Health', 'Health News', "Health Care", 'Medical', 'Public Health', 'ADHD', 'Health / Medical', 'Medical Myths', 'diet']
    for t in health_tags:
        if t in x:
            return True
    return False


def read_data(data_file_path):
    # Importing the dataset      

    df = pd.read_csv(data_file_path, sep='\t')
    df, df_tags = format_tags(df)

    mask = df['tags'].apply(lambda x: health(x))
    df = df[mask]

    # text_col contains the column name of where claims are found
    # answer_col contains the column name of where post labels (true, false, etc.) are found
    text_col = "text"
    answer_col = "label"

    # Rename the claim column to "text" and label column to "label_categorical"
    df.rename(columns = {"claim": "text", "label": "label_categorical"}, inplace = True)
    # Make the categorical labels into numbers (0, 1, 2, 3)
    df["label"] = pd.factorize(df["label_categorical"])[0]
    df = df.dropna(subset=[text_col])
    df.reset_index(drop=True, inplace=True)

    # Make a copy of the 'text' column
    df['text_original'] = df['text']

    # print(f"Shape of df {df.shape}")
    # print(df[-23:])
    return df


def preprocess_text(text):
    lem = nltk.wordnet.WordNetLemmatizer()
    nltk.download('stopwords')
    s = stopwords.words('english')
    text = re.sub('[^a-zA-Z]', ' ', text)
    text = text.lower()
    text = text.split()
    text = [lem.lemmatize(word) for word in text if not word in s]
    text = ' '.join(text)
    return text

def preprocess_data(df):
    for i in range(df.shape[0]):
        text = df.loc[i,'text']
        text = preprocess_text(text)
        df.loc[i, 'text'] = text
        X_train = df['text']
    y_train = df['label']

    print("Preprocessed claims")
    print(df['text'][:10])
    return X_train, y_train, df

class KNN_Model():
    def __init__(self, k=3, distance_type = 'path', preprocess=True):
        self.k = k
        self.distance_type = distance_type
        self.preprocess = preprocess

    # This function is used for training
    def fit(self, x_train, y_train):
        self.x_train = x_train
        self.y_train = y_train
        
    def split_input(self, input_sentence):
        test_corpus = []
        
        # Preprocess the full x_test input
        input_sentence_copy = copy.deepcopy(input_sentence)
        if self.preprocess:
            input_sentence_copy = preprocess_text(input_sentence_copy)
        
        # Preprocess sentences of the input
        sentences = sent_tokenize(input_sentence)
        for sentence in sentences:
            if self.preprocess:
                sentence = preprocess_text(sentence)
            test_corpus.append(sentence)
            
        if len(test_corpus) > 1:
            test_corpus.append(input_sentence_copy)
        
        return test_corpus

    # Returns the k most similar sentences for the input sentence
    # Predict returns the n similar sentences as a list of tuples [(sentence, score), (sentence, score), ...]
    # Takes in only one input at a time
    def predict(self, x_test):
        test_corpus = self.split_input(x_test)
            
        self.x_test = test_corpus
    
        # {score: [(index of sentence in `test_corpus`, similar sentence index in `dataset`)], ...}
        all_top_scores_dict = {}

        # Iterate over sentences of the input
        for i in range(len(self.x_test)):
            print(f"------- Getting similar sentences for \"{self.x_test[i]}\" ({i+1}/{len(self.x_test)}) ------")
            
            # {score: similar_sentence_index_in_`dataset`, ...}
            score_to_index_dict = {}
            
            # Iterate over training examples and find sentence similarity scores
            for j in range(self.x_train.shape[0]): 
                score = self.document_similarity(self.x_test[i], self.x_train[j])
                score_to_index_dict[score] = j

            sorted_scores = list(score_to_index_dict.keys())
            sorted_scores.sort(reverse=True)

            # Get the top k similar sentences for the current sentence (x_test[i])
            for k in range(self.k):
                score = sorted_scores[k]
                
                if score in all_top_scores_dict:
                    all_top_scores_dict[score].append( (i, score_to_index_dict[score]) )
                else:
                    all_top_scores_dict[score] = [ (i, score_to_index_dict[score]) ]
                    
        # Get the top k scoring sentences and similar sentences from all_top_scores_dict
        sorted_scores = list(all_top_scores_dict.keys())
        sorted_scores.sort(reverse=True)
        
        # [ ((index_of_sentence_in_input, index_of_similar_sentence_in_`dataset`), score), ...]
        similar_texts_list = []
        
        for k in range(self.k):
            score = sorted_scores[k]
            new_tuple = (all_top_scores_dict[score], score)
            similar_texts_list.append(new_tuple)

        return similar_texts_list
    
    def convert_tag(self, tag):
        """Convert the tag given by nltk.pos_tag to the tag used by wordnet.synsets"""
        tag_dict = {'N': 'n', 'J': 'a', 'R': 'r', 'V': 'v'}
        try:
            return tag_dict[tag[0]]
        except KeyError:
            return None

    def doc_to_synsets(self, doc):
        """
            Returns a list of synsets in document.
            Tokenizes and tags the words in the document doc.
            Then finds the first synset for each word/tag combination.
        If a synset is not found for that combination it is skipped.

        Args:
            doc: string to be converted

        Returns:
            list of synsets
        """
        tokens = word_tokenize(doc+' ')
        
        l = []
        tags = nltk.pos_tag([tokens[0] + ' ']) if len(tokens) == 1 else nltk.pos_tag(tokens)
        
        for token, tag in zip(tokens, tags):
            syntag = self.convert_tag(tag[1])
            syns = wn.synsets(token, syntag)
            if (len(syns) > 0):
                l.append(syns[0])
        return l  
    
    def similarity_score(self, s1, s2, distance_type = 'path'):
        """
        Calculate the normalized similarity score of s1 onto s2
        For each synset in s1, finds the synset in s2 with the largest similarity value.
        Sum of all of the largest similarity values and normalize this value by dividing it by the
        number of largest similarity values found.

        Args:
          s1, s2: list of synsets from doc_to_synsets

        Returns:
          normalized similarity score of s1 onto s2
        """
        s1_largest_scores = []

        for i, s1_synset in enumerate(s1, 0):
            max_score = 0
            for s2_synset in s2:
                if distance_type == 'path':
                    score = s1_synset.path_similarity(s2_synset, simulate_root = False)
                else:
                    score = s1_synset.wup_similarity(s2_synset)                  
                if score != None:
                    if score > max_score:
                        max_score = score

            if max_score != 0:
                s1_largest_scores.append(max_score)

        mean_score = np.mean(s1_largest_scores)

        return mean_score 
    
    def document_similarity(self, doc1, doc2):
        """Finds the similarity between doc1 and doc2"""

        synsets1 = self.doc_to_synsets(doc1)
        synsets2 = self.doc_to_synsets(doc2)
          
        return (self.similarity_score(synsets1, synsets2) + self.similarity_score(synsets2, synsets1)) / 2

def get_similarity_counts(y_pred, input_sentences, df):
    unique_similar_sentences = []
    all_similar_sentences = []
    similar_sentence_to_original_sentence_dict = {}  # Value is a tuple like (original_sentence, score)

    # Get the k most similar sentences (across all sentences in input)
    for i, result in enumerate (y_pred):
        original_sentence_index = result[0][0][0]
        
        if original_sentence_index == len(input_sentences):
            original_sentence = input_text
        else:
            original_sentence = input_sentences[original_sentence_index]
        
        similar_sentence_index = result[0][0][1]
        similar_sentence_data = df.iloc[[similar_sentence_index]].values.tolist()[0]
        
        text_original_column_index = 11
        label_categorical_column_index = 7
        
        score = result[1]
        
        similar_sentence = similar_sentence_data[text_original_column_index]
        all_similar_sentences.append(similar_sentence)
        
        original_sentence_score_tuple = (original_sentence, score)
        if similar_sentence in similar_sentence_to_original_sentence_dict:
            similar_sentence_to_original_sentence_dict[similar_sentence].append(original_sentence_score_tuple)
        else:
            similar_sentence_to_original_sentence_dict[similar_sentence] = [original_sentence_score_tuple]
            
        if similar_sentence in unique_similar_sentences:
            continue
        else:
            unique_similar_sentences.append(similar_sentence)
        
        
    return Counter(all_similar_sentences), similar_sentence_to_original_sentence_dict

def format_output(input_text, similar_sentence_counter, similar_sentence_to_original_sentence_dict):
    most_common = similar_sentence_counter.most_common()

    # output_string = "Most common similar sentences for input text\n\n"
    outputs = []

    for (similar_sentence, count) in most_common:
        # output_string = "{0} SIMILAR SENTENCE: {1}; COUNT: {2} \n".format(output_string, similar_sentence, count)]
        original_sentence_score_tuple_list = similar_sentence_to_original_sentence_dict[similar_sentence]
        
        # Sort the tuples by the length of the first object in the tuple so that if the full input_text is 
        #    one of the similar sentences, it will be printed first
        original_sentence_score_tuple_list.sort(key=lambda x: len(x[0]), reverse=True)
        
        # output_string += "ORIGINAL SENTENCES\n"
        scores = []
        for original_sentence_score_tuple in original_sentence_score_tuple_list:
            original_sentence = original_sentence_score_tuple[0]
            score = original_sentence_score_tuple[1]

            scores.append(score)
            # if original_sentence == input_text:
            #     # output_string  = "{0} - [***FULL INPUT TEXT***] {1} ({2})\n".format(output_string, original_sentence, score)
                
            # else:
            #     output_string = "{0} - {1} ({2})\n".format(output_string, original_sentence, score)
            #     print(f'   - {original_sentence}  ({score})')
        
        outputs.append([similar_sentence, np.mean(scores)])
            
    return outputs

def save_prediction_to_jsonl(input_text, input_text_label, input_sentences, similar_texts_list, output_file_path, train_df):
    # prediction_dict is a dict that contains
    #   * `input_text`
    #   * `original_sentence_index`
    #   * `similar_sentences_dict`, a dict storing the index of each similar sentence, like {similar_sentence: index}
    #   * `count_dict`, a dict storing the count of each similar sentence, like {similar_sentence: count}
    #   * `score_dict`, a dict storing the score of each similar sentence, like {similar_sentence: [list of scores]}. it is a list in case because count can be > 1
    #   * `label_dict`, a dict storing the label of each similar sentence, like {similar_sentence: label}
    prediction_dict = {}
    similar_sentences_dict = {}
    count_dict = {}
    score_dict = {}
    label_dict = {}
    original_sentence_index = None

    all_similar_sentences = []  # Used for Counter

    for i, result in enumerate(similar_texts_list):
        original_sentence_index = result[0][0][0]
        if original_sentence_index == len(input_sentences):
            original_sentence = input_text
        else:
            original_sentence = input_sentences[original_sentence_index]

        similar_sentence_index = result[0][0][1]
        similar_sentence_data = train_df.iloc[[similar_sentence_index]].values.tolist()[0]

        text_original_column_index = 11
        label_categorical_column_index = 7

        score = result[1]

        similar_sentence = similar_sentence_data[text_original_column_index]
        all_similar_sentences.append(similar_sentence)

        label = similar_sentence_data[label_categorical_column_index]
        label_dict[similar_sentence] = label.lower()

        # Save similar sentence index
        similar_sentences_dict[similar_sentence] = similar_sentence_index
        # Save score
        if similar_sentence in score_dict:
            score_dict[similar_sentence].append(score)
        else:
            score_dict[similar_sentence] = [score]
        # Update count of this similar sentence
        if similar_sentence in count_dict:
            count_dict[similar_sentence] += 1
        else:
            count_dict[similar_sentence] = 1

    """ Add stuff to prediction_dict """
    prediction_dict['input_text'] = input_text
    prediction_dict['input_text_label'] = input_text_label
    prediction_dict['original_sentence_index'] = original_sentence_index
    prediction_dict['similar_sentence_dict'] = similar_sentences_dict
    prediction_dict['score_dict'] = score_dict
    prediction_dict['count_dict'] = count_dict
    prediction_dict['label_dict'] = label_dict

    similar_sentence_counter = Counter(all_similar_sentences)
    most_common = similar_sentence_counter.most_common()

    prediction_dict['most_common'] = most_common

    print(prediction_dict)
    print()

    return prediction_dict


def evaluate_test_set(X_train, y_train, train_df, input_text):
    test_data_file_path = "test.tsv"
    test_df = read_data(test_data_file_path)

    k_value = 3
    preprocess = False

    classifier = KNN_Model(preprocess=preprocess, k=k_value, distance_type='path')
    classifier.fit(X_train, y_train)

    output_file_path = 'pubhealth_test_predictions.jsonl'

    count = 1
    # for index, row in test_df.iterrows():
    #     input_text = row['text']
    input_sentences = classifier.split_input(input_text)
    print(f'Getting similar sentences for \"{input_text}\"')
    count += 1

    input_text_label = 'None'

    similar_texts_list = classifier.predict(input_text)
    # similar_texts_list: [ ((index_of_sentence_in_input, index_of_similar_sentence_in_`dataset`), score), ...]

    return save_prediction_to_jsonl(input_text, input_text_label, input_sentences, similar_texts_list, output_file_path, train_df)
    

def run_knn(input_text, k_value):
    lem = nltk.wordnet.WordNetLemmatizer()
    df = read_data("train.tsv")
    X_train, y_train, df = preprocess_data(df)

    preprocess = False

    classifier = KNN_Model(preprocess=preprocess, k=k_value, distance_type='path')
    classifier.fit(X_train, y_train)
    input_sentences = classifier.split_input(input_text)

    # y_pred = classifier.predict(input_text)
    # print(y_pred)
    prediction = evaluate_test_set(X_train, y_train, df, input_text)

    output_string = "🚨 ALERT! 🚨 \n HealthAdviceCheckBot here! Here are the top claims that match the potential misinformation above: \n "
    # for prediction in output:
    original_statement = prediction['input_text']
    # print(f"INPUT: {original_statement.strip()}")
    label_dict = prediction['label_dict']
    score_dict = prediction['score_dict']

    for similar_sentence in label_dict:
        label = label_dict[similar_sentence]
        scores = score_dict[similar_sentence]
        avg_score = sum(scores) / float(len(scores))
        avg_score_as_percentage = int(avg_score * 100)
        if label == "true":
            output_string = "{0} ✅{1}✅ {2}  ({3}% similar to the original statement) \n \n".format(output_string, label.upper(), similar_sentence, avg_score_as_percentage)
        else:
            output_string = "{0} ❌{1}❌ {2}  ({3}% similar to the original statement) \n \n".format(output_string, label.upper(), similar_sentence, avg_score_as_percentage)
            # print(f'  **{label.upper()}** {similar_sentence}  ({avg_score_as_percentage}%)')
        # print("\n\n")
    # similar_sentence_counter, similar_sentence_to_original_sentence_dict = get_similarity_counts(y_pred, input_sentences, df)
    # output = format_output(input_text, similar_sentence_counter, similar_sentence_to_original_sentence_dict)

    # if len(output) < 3:
    #     output.append(["The model was only able to find two similar sources.", ""])

    return output_string
