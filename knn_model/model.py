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
import json
import os
nltk.download('stopwords')
s = stopwords.words('english')


# Select claims from relevant categories
HEALTH_TAGS = ['Health', 'Health News', "Health Care", 'Medical', 'Public Health', 'ADHD', 'Health / Medical', 'Medical Myths', 'diet']


class KNN_Model():
    def __init__(self, k=3, distance_type='path', preprocess=True):
        self.k = k
        self.distance_type = distance_type
        self.preprocess = preprocess
        self.x_train = None
        self.y_train = None
        self.x_test = None

    def fit(self, x_train, y_train):
        self.x_train = x_train
        self.y_train = y_train

    # Convert an input_text to a list of individual sentences plus the full input
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

        # If there is more than one sentence in the input text, also append the original input text
        if len(test_corpus) > 1:
            test_corpus.append(input_sentence_copy)

        return test_corpus

    # Returns the self.k most similar sentences for the input sentence
    # Predict returns the n similar sentences as a list of tuples [(sentence, score), (sentence, score), ...]
    # Makes prediction for a single input text at a time
    def predict(self, x_test):
        test_corpus = self.split_input(x_test)
        self.x_test = test_corpus

        # {score: [(index of sentence in `test_corpus`, similar sentence index in `dataset`)], ...}
        all_top_scores_dict = {}

        # Iterate over sentences of the input
        for i in range(len(self.x_test)):
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
                    all_top_scores_dict[score].append((i, score_to_index_dict[score]))
                else:
                    all_top_scores_dict[score] = [(i, score_to_index_dict[score])]

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
        tokens = word_tokenize(doc + ' ')

        l = []
        tags = nltk.pos_tag([tokens[0] + ' ']) if len(tokens) == 1 else nltk.pos_tag(tokens)

        for token, tag in zip(tokens, tags):
            syntag = self.convert_tag(tag[1])
            syns = wn.synsets(token, syntag)
            if len(syns) > 0:
                l.append(syns[0])
        return l

    # Returns the normalized similarity score of s1 and s2
    def similarity_score(self, s1, s2, distance_type='path'):
        """
        Calculate the normalized similarity score of s1 onto s2
        For each synset in s1, finds the synset in s2 with the largest similarity value.
        Sum of all of the largest similarity values and normalize this value by dividing it by the
        number of largest similarity values found.

        Args:
          s1, s2: list of synsets from doc_to_synsets
        """
        s1_largest_scores = []

        for i, s1_synset in enumerate(s1, 0):
            max_score = 0
            for s2_synset in s2:
                if distance_type == 'path':
                    score = s1_synset.path_similarity(s2_synset, simulate_root=False)
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


# Format tags columns in df
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
    for t in HEALTH_TAGS:
        if t in x:
            return True
    return False


def preprocess_text(text, ps):
    text = re.sub('[^a-zA-Z]', ' ', text)
    text = text.lower()
    text = text.split()
    text = [ps.lemmatize(word) for word in text if not word in s]
    text = ' '.join(text)
    return text


def prepare_df(data_file_path):
    if data_file_path.endswith('tsv'):
        df = pd.read_csv(data_file_path, sep='\t')
    else:  # assume csv
        df = pd.read_csv(data_file_path)

    df, df_tags = format_tags(df)

    mask = df['tags'].apply(lambda x: health(x))
    df = df[mask]

    # text_col contains the column name of where claims are found
    # answer_col contains the column name of where post labels (true, false, etc.) are found
    text_col = "text"
    answer_col = "label"

    # Rename the claim column to "text" and label column to "label_categorical"
    df.rename(columns={"claim": "text", "label": "label_categorical"}, inplace=True)
    # Make the categorical labels into numbers (0, 1, 2, 3)
    df["label"] = pd.factorize(df["label_categorical"])[0]
    df = df.dropna(subset=[text_col])
    df.reset_index(drop=True, inplace=True)

    # Make a copy of the 'text' column
    df['text_original'] = df['text']

    return df


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

    append_record(output_file_path, prediction_dict)


def evaluate_test_set(X_train, y_train, train_df):
    test_data_file_path = "./test.tsv"
    test_df = prepare_df(test_data_file_path)

    k_value = 3
    preprocess = False

    classifier = KNN_Model(preprocess=preprocess, k=k_value, distance_type='path')
    classifier.fit(X_train, y_train)

    output_file_path = 'pubhealth_test_predictions.jsonl'

    count = 1
    for index, row in test_df.iterrows():
        input_text = row['text']
        input_sentences = classifier.split_input(input_text)
        print(f'Getting similar sentences for \"{input_text}\" ({count}/{len(test_df)})')
        count += 1

        input_text_label = row['label_categorical']

        similar_texts_list = classifier.predict(input_text)
        # similar_texts_list: [ ((index_of_sentence_in_input, index_of_similar_sentence_in_`dataset`), score), ...]

        save_prediction_to_jsonl(input_text, input_text_label, input_sentences, similar_texts_list, output_file_path, train_df)


def append_record(file_path, record):
    with open(file_path, 'a') as f:
        json.dump(record, f)
        f.write(os.linesep)


def main():
    # Importing the dataset
    data_file_path = "train.tsv"

    df = pd.read_csv(data_file_path, sep='\t', encoding = "ISO-8859-1")
    df, df_tags = format_tags(df)

    mask = df['tags'].apply(lambda x: health(x))
    df = df[mask]

    # text_col contains the column name of where claims are found
    # answer_col contains the column name of where post labels (true, false, etc.) are found
    text_col = "text"
    answer_col = "label"

    # Rename the claim column to "text" and label column to "label_categorical"
    df.rename(columns={"claim": "text", "label": "label_categorical"}, inplace=True)
    # Make the categorical labels into numbers (0, 1, 2, 3)
    df["label"] = pd.factorize(df["label_categorical"])[0]
    df = df.dropna(subset=[text_col])
    df.reset_index(drop=True, inplace=True)

    # Make a copy of the 'text' column
    df['text_original'] = df['text']

    ps = nltk.wordnet.WordNetLemmatizer()
    for i in range(df.shape[0]):
        text = df.loc[i, 'text']
        text = preprocess_text(text, ps)
        df.loc[i, 'text'] = text
        X_train = df['text']
    y_train = df['label']

    evaluate_test_set(X_train, y_train, df)  # Pass train df


if __name__ == "__main__":
    main()
